"""Every solutions notebook executes end to end on CPU, with no errors and no warnings,
and finishes within the 3-minute budget. (nbmake is also available: `pytest --nbmake part-*/ch*/labs/*-solutions.ipynb`.)"""
from __future__ import annotations

import time
from pathlib import Path

import nbformat
import pytest
from nbclient import NotebookClient

from conftest import ROOT, solution_notebooks


@pytest.mark.parametrize("sol", solution_notebooks(), ids=lambda p: p.name)
def test_solutions_notebook_executes(sol: Path):
    nb = nbformat.read(sol, as_version=4)
    client = NotebookClient(nb, timeout=240, kernel_name="python3", resources={"metadata": {"path": str(sol.parent)}})
    t0 = time.perf_counter()
    client.execute()
    elapsed = time.perf_counter() - t0
    assert elapsed < 180, f"{sol.name} took {elapsed:.0f}s (budget 180s)"
    for i, cell in enumerate(nb.cells):
        for out in cell.get("outputs", []):
            assert out.get("output_type") != "error", f"cell {i} raised {out.get('ename')}: {out.get('evalue')}"
            if out.get("output_type") == "stream" and out.get("name") == "stderr":
                text = out.get("text", "")
                assert "Warning" not in text, f"cell {i} emitted a warning:\n{text}"
