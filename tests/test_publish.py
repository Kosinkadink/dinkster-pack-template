"""Publishing the template or its placeholder pack must never reach the registry."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("repository", "pack", "message"),
    [
        ("Kosinkadink/dinkster-pack-template", "maple-text", "must never submit"),
        ("an-author/a-pack", "my-pack", "Rename the example pack"),
    ],
)
def test_template_submission_is_refused(
    tmp_path: Path, repository: str, pack: str, message: str
) -> None:
    wheel = tmp_path / "example.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "example/dinkster-pack.toml", f'[pack]\nname = "{pack}"\nversion = "0.1.0"\n'
        )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "tools/publish.py"),
            str(wheel),
            "--registry",
            "http://127.0.0.1:1",
        ],
        env={**os.environ, "GITHUB_REPOSITORY": repository, "DINKSTER_REGISTRY_TOKEN": ""},
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode != 0
    assert message in result.stderr


def test_submission_waits_for_promotion(tmp_path: Path) -> None:
    wheel = tmp_path / "example.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "maple_text/dinkster-pack.toml",
            '[pack]\nname = "maple-text"\nversion = "0.1.0"\n',
        )
    states = iter(("promoting", "accepted"))

    class Registry(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers["Content-Length"]))
            self.respond({"candidateId": "trial-candidate"})

        def do_GET(self):
            if self.path == "/v1/publish/trial-candidate":
                self.respond({"status": next(states)})
            elif self.path == "/v1/packs/maple-text/versions/0.1.0":
                self.respond({"state": "active"})
            else:
                self.send_error(404)

        def respond(self, body):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body).encode())

    with ThreadingHTTPServer(("127.0.0.1", 0), Registry) as registry:
        server = threading.Thread(target=registry.serve_forever)
        server.start()
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve().parents[1] / "tools/publish.py"),
                    str(wheel),
                    "--registry",
                    f"http://127.0.0.1:{registry.server_port}",
                ],
                env={
                    **os.environ,
                    "GITHUB_REPOSITORY": "an-author/a-pack",
                    "GITHUB_REF": "refs/tags/v0.1.0",
                    "DINKSTER_REGISTRY_TOKEN": "disposable-test-token",
                },
                capture_output=True,
                text=True,
                timeout=15,
            )
        finally:
            registry.shutdown()
            server.join()
    assert result.returncode == 0, result.stderr
    assert "Candidate state: promoting" in result.stdout
    assert "Active: maple-text 0.1.0" in result.stdout
