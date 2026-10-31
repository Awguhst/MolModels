"""Student notebooks must be exactly what make_student_notebooks.py generates (no drift),
and solutions notebooks must follow the lab conventions."""
from __future__ import annotations

from pathlib import Path

import nbformat
import pytest

from conftest import ROOT, solution_notebooks
from make_student_notebooks import student_version


@pytest.mark.parametrize("sol", solution_notebooks(), ids=lambda p: p.name)
def test_student_notebook_matches_generator(sol: Path):
    student = sol.with_name(sol.name.replace("-solutions.ipynb", ".ipynb"))
    assert student.exists(), f"missing {student.name}; run scripts/make_student_notebooks.py"
    expected = nbformat.writes(student_version(nbformat.read(sol, as_version=4))) + "\n"
    assert student.read_text(encoding="utf8") == expected, f"{student.name} is out of date; run scripts/make_student_notebooks.py"


@pytest.mark.parametrize("sol", solution_notebooks(), ids=lambda p: p.name)
def test_solutions_notebook_conventions(sol: Path):
    nb = nbformat.read(sol, as_version=4)
    tags = [set(c.get("metadata", {}).get("tags", [])) for c in nb.cells]
    assert any("solution" in t for t in tags), "no cell tagged 'solution'"
    assert any("check" in t for t in tags), "no auto-feedback cell tagged 'check'"
    src = "\n".join(c.source for c in nb.cells if c.cell_type == "code")
    assert "google.colab" in src, "setup cell should be Colab-aware"
    assert "raw.githubusercontent.com" in src, "data loading needs a raw-GitHub fallback"
    assert "random_state=42" in src or "default_rng(42)" in src, "fix the seeds"
    assert "filterwarnings" not in src, "never suppress warnings"
    md = "\n".join(c.source for c in nb.cells if c.cell_type == "markdown").lower()
    assert "reflection" in md, "end with reflection questions"
