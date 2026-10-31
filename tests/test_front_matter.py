"""Every episode and lab page must carry valid front matter, and ids must be consistent."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from conftest import ROOT, episode_files, front_matter, lab_pages

EPISODE_SCHEMA = json.loads((ROOT / "tests" / "episode-schema.json").read_text(encoding="utf8"))
LAB_SCHEMA = json.loads((ROOT / "tests" / "lab-schema.json").read_text(encoding="utf8"))


def _errors(schema: dict, data: dict) -> list[str]:
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in Draft202012Validator(schema).iter_errors(data)]


@pytest.mark.parametrize("path", episode_files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_episode_front_matter(path: Path):
    fm = front_matter(path)
    assert fm, f"{path} has no front matter"
    errs = _errors(EPISODE_SCHEMA, fm)
    assert not errs, "\n".join(errs)
    # file name NN- must match the episode number
    assert path.name.startswith(f"{fm['episode']:02d}-"), f"{path.name} does not start with {fm['episode']:02d}-"
    # chapter must match the directory
    m = re.match(r"ch(\d\d)-", path.parent.name)
    assert m and int(m.group(1)) == fm["chapter"], f"{path} chapter {fm['chapter']} vs directory {path.parent.name}"
    # every episode includes the hidden setup cell exactly once
    text = path.read_text(encoding="utf8")
    assert text.count("{{< include /_includes/mm-setup.qmd >}}") == 1, "missing or duplicated mm-setup include"
    # a closing section linking forward
    assert "## Where this is going" in text, "missing 'Where this is going' section"


@pytest.mark.parametrize("path", lab_pages(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_lab_front_matter(path: Path):
    fm = front_matter(path)
    errs = _errors(LAB_SCHEMA, fm)
    assert not errs, "\n".join(errs)
    nb = path.parent / f"{fm['notebook']}-solutions.ipynb"
    assert nb.exists(), f"solutions notebook {nb.name} missing"


def test_prerequisite_ids_exist():
    ids = set()
    for p in episode_files():
        fm = front_matter(p)
        ids.add(f"ch{fm['chapter']:02d}-ep{fm['episode']:02d}")
    for p in lab_pages():
        fm = front_matter(p)
        ids.add(f"ch{fm['chapter']:02d}-lab{fm['lab']:02d}")
    for p in episode_files():
        for pre in front_matter(p).get("prerequisites", []) or []:
            assert pre in ids, f"{p.name}: unknown prerequisite {pre}"


def test_episode_numbers_are_contiguous():
    by_chapter: dict[int, list[int]] = {}
    for p in episode_files():
        fm = front_matter(p)
        by_chapter.setdefault(fm["chapter"], []).append(fm["episode"])
    for ch, eps in by_chapter.items():
        assert sorted(eps) == list(range(1, len(eps) + 1)), f"chapter {ch} episodes are {sorted(eps)}"
