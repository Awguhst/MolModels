#!/usr/bin/env python
"""Check that the Molecules & Models environment is ready.

    python scripts/check_env.py

Prints the Python version and every course library with a tick or a cross, plus the version
that the course pins (requirements.txt / environment.yml). Exit code 1 if anything essential is missing.
Works in Colab too (copy the whole file into a cell).
"""
from __future__ import annotations

import importlib
import platform
import sys

# (import name, display name, pinned version, essential?)
LIBRARIES = [
    ("numpy", "numpy", "2.5.4", True),
    ("pandas", "pandas", "3.1.0", True),
    ("matplotlib", "matplotlib", "3.10.9", True),
    ("seaborn", "seaborn", "0.13.2", True),
    ("sklearn", "scikit-learn", "1.9.1", True),
    ("joblib", "joblib", "1.6.0", True),
    ("IPython", "ipython (notebooks)", None, True),
    ("jupyterlab", "jupyterlab", "4.6.5", False),
    ("torch", "pytorch (Chapter 4)", "2.9.1", True),
    # Added by later chapters; not needed yet:
    ("rdkit", "rdkit (Part II)", None, False),
    ("Bio", "biopython (Part III)", None, False),
]

OK, MISSING, OPTIONAL = "✅", "❌", "➖"


def version_of(module) -> str:
    for attr in ("__version__", "version", "VERSION"):
        v = getattr(module, attr, None)
        if v:
            return str(v)
    return "?"


def main() -> int:
    py = platform.python_version()
    py_ok = sys.version_info >= (3, 10)
    print(f"{OK if py_ok else MISSING} Python {py}  (3.12 recommended; 3.10+ required)")
    print(f"   {sys.executable}")
    print()
    problems = 0
    for mod, name, pinned, essential in LIBRARIES:
        try:
            m = importlib.import_module(mod)
        except ImportError:
            if essential:
                problems += 1
                print(f"{MISSING} {name:<24} not installed   -> python -m pip install -r requirements.txt")
            else:
                print(f"{OPTIONAL} {name:<24} not installed   (optional for now)")
            continue
        v = version_of(m)
        note = ""
        if pinned and v.split("+")[0] != pinned:
            note = f"   (course pins {pinned}; a different version usually works)"
        print(f"{OK} {name:<24} {v}{note}")
    print()
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        plt.close(fig)
        print(f"{OK} matplotlib can draw a figure")
    except Exception as exc:  # noqa: BLE001
        problems += 1
        print(f"{MISSING} matplotlib could not draw a figure: {exc}")
    try:
        import numpy as np
        from sklearn.linear_model import LinearRegression

        rng = np.random.default_rng(42)
        X = rng.normal(size=(20, 2))
        y = X @ np.array([1.0, -2.0]) + 0.1 * rng.normal(size=20)
        LinearRegression().fit(X, y)
        print(f"{OK} scikit-learn can fit a model")
    except Exception as exc:  # noqa: BLE001
        problems += 1
        print(f"{MISSING} scikit-learn test failed: {exc}")
    print()
    if problems:
        print(f"{problems} problem(s). See the troubleshooting section of the Setup episode.")
        return 1
    print("All good. The environment is ready for Part I, including CPU deep learning.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
