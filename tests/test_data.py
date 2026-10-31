"""Data integrity: bundled files match their documented SHA-256; downloaded files too (if present)."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from conftest import ROOT
from fetch_data import DATASETS

README = (ROOT / "data" / "README.md").read_text(encoding="utf8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def documented_hash(name: str) -> str:
    section = README.split(f"`{name}`", 1)[1]
    m = re.search(r"SHA-256 \| `([0-9a-f]{64})`", section)
    assert m, f"no SHA-256 documented for {name} in data/README.md"
    return m.group(1)


def test_penguins_checksum():
    path = ROOT / "data" / "penguins.csv"
    assert path.exists()
    assert sha256(path) == documented_hash("penguins.csv")


@pytest.mark.parametrize("name", list(DATASETS))
def test_downloaded_dataset_checksum(name: str):
    path = ROOT / "data" / name
    if not path.exists():
        pytest.skip(f"{name} not downloaded (python scripts/fetch_data.py)")
    assert sha256(path) == DATASETS[name]["sha256"]
    assert DATASETS[name]["sha256"] == documented_hash(name), "README and fetch_data.py disagree"


def test_no_large_files_in_data():
    for f in (ROOT / "data").glob("*.csv"):
        assert f.stat().st_size < 5 * 1024 * 1024, f"{f.name} is over 5 MB"
