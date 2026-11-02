"""Dark rendering must keep plot details readable without altering their meaning."""
import runpy

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest
import seaborn as sns
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, to_rgba

from conftest import ROOT

THEME = runpy.run_path(str(ROOT / "_includes" / "plot_theme.py"))
restyle_dark = THEME["restyle_dark"]


def contrast(colour, background):
    foreground = np.array(to_rgba(colour))
    background = np.array(to_rgba(background))[:3]
    composite = foreground[:3] * foreground[3] + background * (1 - foreground[3])

    def luminance(rgb):
        linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
        return linear @ np.array([.2126, .7152, .0722])

    values = sorted([luminance(composite), luminance(background)])
    return (values[1] + .05) / (values[0] + .05)


@pytest.fixture(autouse=True)
def course_style():
    with plt.style.context(str(ROOT / "assets" / "mpl" / "mm-light.mplstyle")):
        yield
    plt.close("all")


def test_translucent_scatter_and_legend_remain_readable_in_dark_mode():
    fig, ax = plt.subplots()
    points = ax.scatter([1, 2, 3], [4, 2, 5], alpha=.6, label="measurements")
    ax.legend()
    offsets = points.get_offsets().copy()
    restyle_dark(fig)
    fig.canvas.draw()
    np.testing.assert_array_equal(points.get_offsets(), offsets)
    assert points.get_alpha() == .6
    assert contrast(points.get_facecolor()[0], ax.get_facecolor()) >= 3  # graphical marks, including alpha
    np.testing.assert_allclose(ax.get_legend().legend_handles[0].get_facecolor(), points.get_facecolor())


def test_box_and_violin_summary_lines_survive_dark_rendering():
    fig, axes = plt.subplots(1, 2)
    values = [1, 2, 2, 3, 4, 5, 12]
    sns.boxplot(y=values, ax=axes[0])
    sns.violinplot(y=values, ax=axes[1])
    neutral_lines = []
    for ax in axes:
        for line in ax.lines:
            rgba = to_rgba(line.get_color())
            if max(rgba[:3]) - min(rgba[:3]) < 1e-6 and max(rgba[:3]) <= .6:
                neutral_lines.append((ax, line, line.get_ydata().copy()))
    assert neutral_lines, "fixture must include seaborn's dark neutral summary marks"
    restyle_dark(fig)
    for ax, line, original in neutral_lines:
        assert contrast(line.get_color(), ax.get_facecolor()) >= 3
        np.testing.assert_array_equal(line.get_ydata(), original)


def test_heatmap_values_scale_and_annotation_contrast_are_preserved():
    fig, ax = plt.subplots()
    values = np.array([[0, .5], [.8, 1]])
    sns.heatmap(values, annot=True, cmap="viridis", vmin=0, vmax=1, ax=ax)
    mesh = ax.collections[0]
    colours = mesh.cmap(np.linspace(0, 1, 20))
    annotation_colours = [text.get_color() for text in ax.texts]
    restyle_dark(fig)
    np.testing.assert_array_equal(mesh.get_array(), values)
    np.testing.assert_array_equal(mesh.cmap(np.linspace(0, 1, 20)), colours)
    assert [text.get_color() for text in ax.texts] == annotation_colours
    assert (mesh.norm.vmin, mesh.norm.vmax) == (0, 1)


def test_categorical_regions_keep_the_same_hue_as_their_points():
    fig, ax = plt.subplots()
    x, y = np.meshgrid([0, 1], [0, 1])
    classes = np.array([[0, 0], [1, 1]])
    region = ax.contourf(x, y, classes, levels=[-.5, .5, 1.5],
                         cmap=ListedColormap(["#2C5D9B", "#E69F00"]), alpha=.15)
    points = ax.scatter([0, 1], [0, 1], c=["#2C5D9B", "#E69F00"])
    restyle_dark(fig)
    fig.canvas.draw()
    np.testing.assert_allclose(region.cmap([0, 1])[:, :3], points.get_facecolor()[:, :3])
    assert (region.norm.vmin, region.norm.vmax) == (-.5, 1.5)


def test_scalar_mapped_line_colours_keep_their_numeric_meaning():
    fig, ax = plt.subplots()
    lines = LineCollection([[(0, n), (1, n)] for n in range(3)], cmap="gray", norm=plt.Normalize(0, 1))
    lines.set_array(np.array([.1, .4, .8]))
    ax.add_collection(lines)
    fig.colorbar(lines, ax=ax)
    fig.canvas.draw()
    colours = lines.get_edgecolor().copy()
    restyle_dark(fig)
    fig.canvas.draw()
    np.testing.assert_array_equal(lines.get_edgecolor(), colours)
    np.testing.assert_array_equal(lines.get_array(), [.1, .4, .8])
