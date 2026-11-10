"""Rename the example pack before its first release."""

from __future__ import annotations

import argparse
import keyword
import re
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="your lowercase, hyphen-separated pack name")
    args = parser.parse_args()
    name = args.name
    if len(name) > 64 or re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*", name) is None:
        parser.error("use at most 64 lowercase ASCII letters, digits and single hyphens")
    if name == "my-pack":
        parser.error("choose a name other than my-pack")
    root = Path(__file__).resolve().parent.parent
    package = name.replace("-", "_")
    if keyword.iskeyword(package):
        parser.error("the import package cannot be a Python keyword")
    sources = [
        root / "pyproject.toml",
        root / "dinkster-pack.toml",
        root / "src/my_pack/__init__.py",
        root / "tests/test_pack.py",
    ]
    if not all(path.is_file() for path in sources):
        parser.error("run once on an unrenamed template")
    if (root / "src" / package).exists():
        parser.error("destination package already exists")
    for path in sources:
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("my-pack", name).replace("my_pack", package), encoding="utf-8")
    (root / "src/my_pack").rename(root / "src" / package)
    (root / "docs/nodes/my-pack.shout").rename(root / "docs/nodes" / f"{name}.shout")
    print(f"Renamed to {name}; run uv sync to refresh the lock and installed package")


if __name__ == "__main__":
    main()
