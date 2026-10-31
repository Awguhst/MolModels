#!/usr/bin/env python
"""Download datasets that are not redistributed in this repository, verifying their SHA-256.

Currently: ESOL / Delaney (MoleculeNet "delaney-processed.csv").
The redistribution terms of the MoleculeNet copy are not stated explicitly, so we do not
bundle the file: it is fetched from the canonical DeepChem location at build time and cached
in data/esol.csv (git-ignored). See data/README.md.

    python scripts/fetch_data.py          # download if missing or corrupt
    python scripts/fetch_data.py --force  # re-download
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASETS = {
    "esol.csv": {
        "url": "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/delaney-processed.csv",
        "sha256": "8c06a76f0c6487d29ab0f903e6a7a7139f189ab3c1178f159c8be8964602f189",
    },
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(name: str, spec: dict, force: bool = False) -> bool:
    dest = ROOT / "data" / name
    if dest.exists() and not force and sha256(dest) == spec["sha256"]:
        print(f"ok        {dest.relative_to(ROOT)} (checksum verified)")
        return True
    print(f"download  {spec['url']}")
    tmp = dest.with_suffix(".part")
    try:
        with urllib.request.urlopen(spec["url"], timeout=60) as r, tmp.open("wb") as f:
            f.write(r.read())
    except OSError as exc:
        print(f"FAILED    {name}: {exc}")
        return False
    digest = sha256(tmp)
    if digest != spec["sha256"]:
        tmp.unlink(missing_ok=True)
        print(f"FAILED    {name}: checksum mismatch\n  expected {spec['sha256']}\n  got      {digest}")
        return False
    tmp.replace(dest)
    print(f"saved     {dest.relative_to(ROOT)} (checksum verified)")
    return True


def main(argv: list[str]) -> int:
    force = "--force" in argv
    ok = all(fetch(n, s, force) for n, s in DATASETS.items())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
