"""Authoring rules that keep episodes consistent (see AUTHORING.md)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from conftest import ROOT, episode_files, front_matter

CELL_RE = re.compile(r"```\{python\}\n(.*?)```", re.S)
PLOT_HINTS = ("plt.subplots(", "plt.figure(", "sns.pairplot(", "sns.catplot(", "sns.relplot(", "sns.displot(", "sns.lmplot(", "sns.jointplot(", ".plot(")
GLOSSARY = yaml.safe_load((ROOT / "glossary.yml").read_text(encoding="utf8"))
TERM_IDS = {t["id"] for t in GLOSSARY["terms"]}


def code_cells(text: str) -> list[str]:
    return CELL_RE.findall(text)


@pytest.mark.parametrize("path", episode_files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_figure_cells_have_renderings_alt_and_show(path: Path):
    text = path.read_text(encoding="utf8")
    problems = []
    for i, cell in enumerate(code_cells(text), 1):
        makes_figure = any(h in cell for h in PLOT_HINTS) and "#| echo: false" not in cell
        if not makes_figure:
            continue
        if "#| renderings: [light, dark]" not in cell:
            problems.append(f"cell {i}: figure cell without `#| renderings: [light, dark]`")
        if "#| fig-alt:" not in cell:
            problems.append(f"cell {i}: figure cell without `#| fig-alt`")
        body = [l for l in cell.strip().splitlines() if l.strip() and not l.startswith("#|")]
        if not body or body[-1].strip() != "plt.show()":
            problems.append(f"cell {i}: figure cell must end with plt.show()")
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("path", episode_files(), ids=lambda p: p.relative_to(ROOT).as_posix())
def test_episode_pedagogy(path: Path):
    text = path.read_text(encoding="utf8")
    fm = front_matter(path)
    levels = re.findall(r"::: \{\.challenge level=(\d)", text)
    upper = 12 if fm["chapter"] == 0 else 6
    assert 2 <= len(levels) <= upper, f"expected 2–{upper} exercises, found {len(levels)}"
    assert "1" in levels and ("2" in levels or "3" in levels), "need at least one ★ and one ★★/★★★ exercise"
    assert text.count("{.solution}") >= len(levels), "every exercise needs a solution"
    assert "{.predict}" in text, "missing a 'predict before you run' prompt"
    assert re.search(r"\{\.bridge audience=", text), "missing a bridge box"
    # glossary terms used must exist
    for tid in re.findall(r"\{\{< term ([a-z0-9-]+)", text):
        assert tid in TERM_IDS, f"unknown glossary term '{tid}'"
    # seeds
    assert "random_state=" not in text or "random_state=42" in text or "random_state=seed" in text or "random_state=rs" in text
    assert "np.random.seed" not in text, "use np.random.default_rng(42), not np.random.seed"
    assert "warnings.filterwarnings" not in text and "simplefilter(\"ignore\"" not in text, "never suppress warnings"


def test_one_debug_exercise_per_chapter():
    chapters: dict[int, int] = {}
    for p in episode_files():
        fm = front_matter(p)
        text = p.read_text(encoding="utf8")
        chapters[fm["chapter"]] = chapters.get(fm["chapter"], 0) + len(re.findall(r'title="Debug this', text))
    for ch, n in chapters.items():
        if ch == 0:
            continue
        assert n >= 1, f"chapter {ch} has no 'Debug this' exercise"


def test_glossary_file_is_consistent():
    ids = [t["id"] for t in GLOSSARY["terms"]]
    assert len(ids) == len(set(ids)), "duplicate glossary ids"
    for t in GLOSSARY["terms"]:
        for s in t.get("see", []) or []:
            assert s in TERM_IDS, f"{t['id']}: see-also '{s}' does not exist"
        assert len(t["short"]) <= 200, f"{t['id']}: tooltip text too long"
