#!/usr/bin/env python
"""Generate student lab notebooks from the solutions notebooks (the single source of truth).

For every  part-*/ch*/labs/<name>-solutions.ipynb  this writes  part-*/ch*/labs/<name>.ipynb  where
  * code cells tagged `solution` are replaced by a `# TODO` stub (the first line of the cell is kept
    if it is a comment, so the task stays visible; everything else is removed),
  * all outputs and execution counts are cleared,
  * cells tagged `check` (auto-feedback asserts) and `setup` are kept verbatim,
  * cells tagged `solutions-only` are dropped entirely.

    python scripts/make_student_notebooks.py          # write student notebooks
    python scripts/make_student_notebooks.py --check  # exit 1 if any student notebook is out of date

The --check mode is what tests/test_student_notebooks.py runs, so a solutions notebook can never be
edited without regenerating the student version.
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
STUB = "# TODO: your code here\n"


def student_version(nb: nbformat.NotebookNode) -> nbformat.NotebookNode:
    out = copy.deepcopy(nb)
    cells = []
    for cell in out.cells:
        tags = set(cell.get("metadata", {}).get("tags", []))
        if "solutions-only" in tags:
            continue
        if cell.cell_type == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
            if "solution" in tags:
                lines = cell.source.splitlines()
                keep = [l for l in lines if l.startswith("#")] if lines and lines[0].startswith("#") else []
                # keep only the leading comment block (the task description), then the stub
                head = []
                for l in lines:
                    if l.startswith("#"):
                        head.append(l)
                    else:
                        break
                cell.source = "\n".join(head + [STUB.rstrip("\n")]) if head else STUB.rstrip("\n")
                del keep
        cells.append(cell)
    out.cells = cells
    out.metadata.pop("widgets", None)
    return out


def write_clean(nb: nbformat.NotebookNode, path: Path) -> str:
    text = nbformat.writes(nb) + "\n"
    path.write_text(text, encoding="utf8")
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    stale = []
    n = 0
    for sol in sorted(ROOT.glob("part-*/ch*/labs/*-solutions.ipynb")):
        student = sol.with_name(sol.name.replace("-solutions.ipynb", ".ipynb"))
        nb = nbformat.read(sol, as_version=4)
        expected = nbformat.writes(student_version(nb)) + "\n"
        if args.check:
            current = student.read_text(encoding="utf8") if student.exists() else None
            if current != expected:
                stale.append(student)
        else:
            student.write_text(expected, encoding="utf8")
            print(f"wrote {student.relative_to(ROOT)}")
        n += 1
    if args.check:
        if stale:
            print("student notebooks out of date (run scripts/make_student_notebooks.py):")
            for s in stale:
                print("  ", s.relative_to(ROOT))
            return 1
        print(f"{n} student notebook(s) up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
