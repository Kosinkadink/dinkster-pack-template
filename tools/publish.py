"""Submit one renamed pack through the documented registry HTTP API."""

from __future__ import annotations

import argparse
import json
import os
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Registry redirects are refused; use its direct URL")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    parser.add_argument("--registry", required=True)
    args = parser.parse_args()
    if os.environ.get("GITHUB_REPOSITORY", "").lower() == "kosinkadink/dinkster-pack-template":
        raise SystemExit("The template repository must never submit a pack")
    with zipfile.ZipFile(args.wheel) as wheel:
        manifests = [name for name in wheel.namelist() if name.endswith("/dinkster-pack.toml")]
        if len(manifests) != 1:
            raise SystemExit("Expected exactly one packaged manifest")
        pack = tomllib.loads(wheel.read(manifests[0]).decode())["pack"]
    name, version = pack["name"], pack["version"]
    if name == "my-pack":
        raise SystemExit("Rename the example pack before submitting")
    tag = os.environ.get("GITHUB_REF", "")
    if tag.startswith("refs/tags/") and tag != f"refs/tags/v{version}":
        raise SystemExit("The version tag must match the packaged manifest")
    base = args.registry.rstrip("/")
    url = urllib.parse.urlsplit(base)
    if url.scheme not in {"https", "http"} or not url.hostname or url.username or url.password:
        raise SystemExit("Registry must be a direct HTTP(S) URL without credentials")
    if url.query or url.fragment or url.path:
        raise SystemExit("Registry must be an origin URL without a path, query or fragment")
    if url.scheme == "http" and url.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Plain HTTP is allowed only for a disposable loopback registry")
    token = os.environ.get("DINKSTER_REGISTRY_TOKEN")
    if not token:
        raise SystemExit("Set DINKSTER_REGISTRY_TOKEN to a publisher token")
    opener = urllib.request.build_opener(NoRedirect())

    def request(path: str, payload: bytes | None = None) -> dict:
        headers = {"Authorization": f"Bearer {token}"}
        if payload is not None:
            headers["Content-Type"] = "application/octet-stream"
        req = urllib.request.Request(base + path, data=payload, headers=headers)
        try:
            with opener.open(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            raise SystemExit(
                f"Registry returned HTTP {error.code}; submission was not retried"
            ) from None

    pack_path = urllib.parse.quote(name, safe="")
    version_path = urllib.parse.quote(version, safe="")
    result = request(f"/v1/publish/{pack_path}/versions/{version_path}", args.wheel.read_bytes())
    candidate = urllib.parse.quote(result["candidateId"], safe="")
    print(f"Candidate: {candidate}", flush=True)
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        state = request(f"/v1/publish/{candidate}")["status"]
        print(f"Candidate state: {state}", flush=True)
        if state == "accepted":
            release = request(f"/v1/packs/{pack_path}/versions/{version_path}")
            if release["state"] != "active":
                raise SystemExit("Accepted candidate is not active")
            print(f"Active: {name} {version}")
            return
        if state not in {"queued", "scanning", "promoting"}:
            raise SystemExit(f"Candidate did not become active: {state}")
        time.sleep(3)
    raise SystemExit("Timed out; inspect the candidate before submitting again")


if __name__ == "__main__":
    main()
