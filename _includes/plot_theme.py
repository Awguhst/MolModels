"""Dark variants of the course figures without rerunning or changing their data."""
from __future__ import annotations

import colorsys

import matplotlib as mpl
import numpy as np
from matplotlib.collections import Collection
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.text import Annotation, Text

LIGHT = {"bg": "#FFFFFF", "text": "#1E2228", "axis": "#5E6168", "grid": "#D8D5CE"}
DARK = {"bg": "#1C2025", "text": "#E8E4DC", "axis": "#A6A197", "grid": "#2F353D"}


def _rgb_key(colour):
    return mpl.colors.to_hex(colour, keep_alpha=False).upper()


# Retain category hues, but lift the two dark palette entries above the dark canvas.
# Seaborn uses a desaturated version of these fills for boxes and violins.
_DATA_COLOURS = {}
for _light, _dark in (("#2C5D9B", "#93BBF5"), ("#8C5600", "#E3AA5C")):
    for _saturation in (1.0, 0.75):
        _h, _l, _s = colorsys.rgb_to_hls(*mpl.colors.to_rgb(_light))
        _source = colorsys.hls_to_rgb(_h, _l, _s * _saturation)
        _h, _l, _s = colorsys.rgb_to_hls(*mpl.colors.to_rgb(_dark))
        _DATA_COLOURS[_rgb_key(_source)] = colorsys.hls_to_rgb(_h, _l, _s * _saturation)


def _replace(colour, mapping):
    try:
        rgba = mpl.colors.to_rgba(colour)
        replacement = mapping.get(_rgb_key(rgba)) if rgba[3] else None
        return (*mpl.colors.to_rgb(replacement), rgba[3]) if replacement is not None else colour
    except (ValueError, TypeError):
        return colour  # e.g. marker colour "auto"


def _swap(colour, key):
    return _replace(colour, {LIGHT[key]: DARK[key]})


def _ink(colour):
    """Keep thin neutral references, whiskers and medians visible on dark axes."""
    colour = _swap(colour, "axis")
    try:
        r, g, b, alpha = mpl.colors.to_rgba(colour)
        if alpha and max(r, g, b) - min(r, g, b) < 1e-6 and r <= 0.6:
            return (*mpl.colors.to_rgb(DARK["axis"]), alpha)
    except (ValueError, TypeError):
        pass
    return _replace(colour, _DATA_COLOURS)


def _edge(colour):
    return _ink(_swap(colour, "bg"))


def restyle_dark(fig):
    """Restyle chrome and low-contrast ink while preserving values and colour scales."""
    fig.patch.set_facecolor(_swap(fig.patch.get_facecolor(), "bg"))
    for ax in fig.axes:
        ax.patch.set_facecolor(_swap(ax.patch.get_facecolor(), "bg"))
        for spine in ax.spines.values():
            spine.set_edgecolor(_swap(spine.get_edgecolor(), "axis"))
        ax.tick_params(colors=DARK["axis"], labelcolor=DARK["text"], which="both")
        for line in ax.get_xgridlines() + ax.get_ygridlines():
            line.set_color(_swap(line.get_color(), "grid"))

    for line in fig.findobj(Line2D):
        line.set_color(_ink(line.get_color()))
        line.set_markerfacecolor(_replace(line.get_markerfacecolor(), _DATA_COLOURS))
        line.set_markeredgecolor(_edge(line.get_markeredgecolor()))

    for collection in fig.findobj(Collection):
        # Continuous colour scales carry numeric meaning; leave them untouched.
        # Small categorical maps can share the same brighter hue as their points.
        cmap = collection.get_cmap()
        if isinstance(cmap, mpl.colors.ListedColormap) and cmap.N <= 8:
            colours = [_replace(c, _DATA_COLOURS) for c in cmap.colors]
            if not np.allclose(mpl.colors.to_rgba_array(colours), mpl.colors.to_rgba_array(cmap.colors)):
                collection.set_cmap(mpl.colors.ListedColormap(colours, name=cmap.name + "_dark"))
        if collection.get_array() is None:
            faces = collection.get_facecolor()
            if len(faces):
                collection.set_facecolor([_replace(c, _DATA_COLOURS) for c in faces])
            # Scalar-mapped line segments can carry their values in edge colours.
            edges = collection.get_edgecolor()
            if len(edges):
                collection.set_edgecolor([_edge(c) for c in edges])

    for patch in fig.findobj(Patch):
        patch.set_facecolor(_replace(patch.get_facecolor(), _DATA_COLOURS))
        patch.set_edgecolor(_edge(patch.get_edgecolor()))

    for text in fig.findobj(Text):
        # Preserve heatmap annotations' deliberately light/dark contrast colours.
        text.set_color(_swap(text.get_color(), "text"))
        if isinstance(text, Annotation) and text.arrow_patch is not None:
            arrow = text.arrow_patch
            arrow.set_edgecolor(_edge(arrow.get_edgecolor()))
            arrow.set_facecolor(_ink(arrow.get_facecolor()))

    legends = list(fig.legends) + [ax.get_legend() for ax in fig.axes if ax.get_legend() is not None]
    for legend in legends:
        frame = legend.get_frame()
        frame.set_facecolor(_swap(frame.get_facecolor(), "bg"))
        frame.set_edgecolor(_swap(frame.get_edgecolor(), "grid"))
    return fig
