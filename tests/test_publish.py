"""Publishing the template or its placeholder pack must never reach the registry."""

from __future__ import annotations

import os
import subprocess
import sys
import zipfile
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
