"""Held-out results must not change the model selected for the lab's parity plot."""
from __future__ import annotations

import json
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from conftest import ROOT


class FixedRegressor:
    def __init__(self, predictions, cv_rmse):
        self.predictions = np.array(predictions, dtype=float)
        self.best_score_ = -cv_rmse

    def predict(self, X):
        assert len(X) == len(self.predictions)
        return self.predictions.copy()


@pytest.mark.parametrize("targets", [[0, 0, 0], [3, 4, 5]])
def test_lab_model_choice_does_not_depend_on_held_out_targets(targets, monkeypatch):
    # Exercise the plot cell without opening an interactive window in the test runner.
    monkeypatch.setattr(plt, "show", lambda: None)
    notebook = ROOT / "part-1-foundations/ch02-ml-fundamentals/labs/lab-02-first-ml-project-solutions.ipynb"
    cells = json.loads(notebook.read_text(encoding="utf8"))["cells"]

    def task_source(number):
        return next(
            "".join(cell["source"])
            for cell in cells
            if cell["cell_type"] == "code"
            and re.search(rf"^# Task {number}:", "".join(cell["source"]), re.M)
        )

    baseline = FixedRegressor([0, 0, 0], 2.2)
    linear = FixedRegressor([1, 1, 1], 1.2)
    ridge = FixedRegressor([1.1, 1.1, 1.1], 1.19)
    knn = FixedRegressor([3, 4, 5], 0.9)

    def report(model, X, y):
        residual = np.asarray(y) - model.predict(X)
        return {"MAE": np.abs(residual).mean(), "RMSE": np.sqrt(np.mean(residual**2)), "R2": 0.0}

    namespace = {
        "np": np, "pd": pd, "plt": plt, "report": report,
        "baseline": baseline, "baseline_cv_rmse": 2.2,
        "linreg": linear, "linreg_cv_rmse": 1.2,
        "ridge_search": ridge, "knn_search": knn,
        "X_test": np.zeros((3, 1)), "y_test": np.array(targets, dtype=float),
        "y": np.array([-1, 6], dtype=float),
    }
    try:
        exec(compile(task_source(7), str(notebook), "exec"), namespace)
        exec(compile(task_source(8), str(notebook), "exec"), namespace)
        # The first scenario makes the baseline win on the test set, while training CV is unchanged.
        expected_test_winner = "baseline (mean)" if targets == [0, 0, 0] else "kNN (scaled, tuned)"
        assert namespace["results"]["test RMSE"].idxmin() == expected_test_winner
        assert namespace["best_model"] is knn
        np.testing.assert_array_equal(namespace["pred_best"], knn.predictions)
    finally:
        plt.close("all")
