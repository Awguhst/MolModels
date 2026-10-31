from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}
    return yaml.safe_load(m.group(1)) or {}


def episode_files() -> list[Path]:
    return sorted(p for p in ROOT.glob("part-*/ch*/[0-9][0-9]-*.qmd"))


def lab_pages() -> list[Path]:
    return sorted(ROOT.glob("part-*/ch*/labs/lab-*.qmd"))


def solution_notebooks() -> list[Path]:
    return sorted(ROOT.glob("part-*/ch*/labs/*-solutions.ipynb"))
