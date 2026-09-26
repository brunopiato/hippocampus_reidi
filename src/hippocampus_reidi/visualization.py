"""Visualization helpers for image-analysis results."""

from __future__ import annotations

from collections.abc import Mapping
from math import ceil
from os import PathLike

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from .analysis import (
    ColorRange,
    _analyze_rgb_image,
    _read_rgb_image,
    _validate_color_ranges,
)


def plot_image_analysis(
    image_path: str | PathLike[str],
    color_ranges: Mapping[str, ColorRange],
) -> Figure:
    """Plot the original image, background mask, and selected-color masks."""
    validated_ranges = _validate_color_ranges(color_ranges)
    image = _read_rgb_image(image_path)
    analysis, background_mask, masks = _analyze_rgb_image(
        image,
        str(image_path),
        validated_ranges,
    )

    plot_count = len(masks) + 2
    column_count = min(3, plot_count)
    row_count = ceil(plot_count / column_count)

    with plt.ioff():
        figure, axes = plt.subplots(
            row_count,
            column_count,
            figsize=(4 * column_count, 3.5 * row_count),
            squeeze=False,
        )
        axes_flat = list(axes.flat)
        panel_index = 0

        axis = axes_flat[panel_index]
        panel_index += 1
        axis.imshow(image)
        axis.set_title("Original image")
        axis.axis("off")

        axis = axes_flat[panel_index]
        panel_index += 1
        axis.imshow(background_mask, cmap="gray")
        axis.set_title("Background mask")
        axis.axis("off")
        axis.text(
            0.5,
            -0.05,
            f"{analysis['background_percentage']:.4f}",
            ha="center",
            va="top",
            transform=axis.transAxes,
        )

        for name, mask in masks.items():
            axis = axes_flat[panel_index]
            panel_index += 1
            axis.imshow(mask, cmap="gray")
            axis.set_title(f"{name.capitalize()} mask")
            axis.axis("off")
            axis.text(
                0.5,
                -0.05,
                f"{analysis['colors'][name]['percentage']:.4f}",
                ha="center",
                va="top",
                transform=axis.transAxes,
            )

        for axis in axes_flat[panel_index:]:
            figure.delaxes(axis)

        figure.tight_layout()

    return figure
