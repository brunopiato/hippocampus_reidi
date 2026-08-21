"""Image color analysis and batch processing."""

from __future__ import annotations

from collections.abc import Sequence
from os import PathLike
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray

type ImagePath = str | PathLike[str]
type RGBColor = Sequence[int]
type ColorRange = Sequence[RGBColor]
type ColorMetric = NDArray[np.uint8] | int | float
type ColorResults = dict[str, dict[str, ColorMetric]]

_BACKGROUND_COLOR = np.array([0, 0, 0], dtype=np.uint8)
_SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def _read_rgb_image(image_path: ImagePath) -> NDArray[np.uint8]:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def _validate_color_inputs(
    color_names: Sequence[str],
    color_ranges: Sequence[ColorRange],
) -> list[tuple[str, NDArray[np.uint8], NDArray[np.uint8]]]:
    if len(color_names) != len(color_ranges):
        raise ValueError(
            "color_names and color_ranges must contain the same number of items "
            f"({len(color_names)} != {len(color_ranges)})"
        )
    if len(set(color_names)) != len(color_names):
        raise ValueError("color_names must be unique")

    validated_ranges: list[tuple[str, NDArray[np.uint8], NDArray[np.uint8]]] = []
    for name, bounds in zip(color_names, color_ranges, strict=True):
        bounds_array = np.asarray(bounds)
        if bounds_array.shape != (2, 3):
            raise ValueError(f"Color range for {name!r} must contain two RGB triplets")
        if np.any((bounds_array < 0) | (bounds_array > 255)):
            raise ValueError(f"RGB values for {name!r} must be between 0 and 255")

        lower = bounds_array[0].astype(np.uint8)
        upper = bounds_array[1].astype(np.uint8)
        if np.any(lower > upper):
            raise ValueError(f"Lower RGB bound must not exceed upper bound for {name!r}")
        validated_ranges.append((name, lower, upper))

    return validated_ranges


def calculate_color_percentage(
    image_path: ImagePath,
    color_names: Sequence[str],
    color_ranges: Sequence[ColorRange],
) -> ColorResults:
    """Calculate foreground coverage for each RGB range and plot the generated masks.

    Pure black pixels are treated as background and excluded from each selected color's
    denominator. The returned ``image`` entry describes that background mask.
    """
    validated_ranges = _validate_color_inputs(color_names, color_ranges)
    image = _read_rgb_image(image_path)
    total_pixels = int(image.shape[0] * image.shape[1])

    background_mask = cv2.inRange(image, _BACKGROUND_COLOR, _BACKGROUND_COLOR)
    background_pixels = int(cv2.countNonZero(background_mask))
    foreground_pixels = total_pixels - background_pixels
    if foreground_pixels == 0:
        raise ValueError("The image contains no non-black foreground pixels")

    results: ColorResults = {}
    masks: dict[str, NDArray[np.uint8]] = {}
    for name, lower, upper in validated_ranges:
        mask = cv2.inRange(image, lower, upper)
        pixels = int(cv2.countNonZero(mask))
        results[name] = {
            "lower": lower,
            "upper": upper,
            "pixels": pixels,
            "percentage": pixels / foreground_pixels,
        }
        masks[name] = mask

    background_percentage = background_pixels / total_pixels
    results["image"] = {
        "lower": _BACKGROUND_COLOR.copy(),
        "upper": _BACKGROUND_COLOR.copy(),
        "pixels": background_pixels,
        "percentage": background_percentage,
    }

    _plot_masks(image, background_mask, background_percentage, masks, results)
    for name, metrics in results.items():
        percentage = float(metrics["percentage"])
        print(f"The {name.lower()} percentage is {percentage * 100:.3f}%.")

    return results


def _plot_masks(
    image: NDArray[np.uint8],
    background_mask: NDArray[np.uint8],
    background_percentage: float,
    masks: dict[str, NDArray[np.uint8]],
    results: ColorResults,
) -> None:
    plot_count = len(masks) + 2
    column_count = (plot_count + 1) // 2
    figure = plt.figure(figsize=(12, 6))

    axis = figure.add_subplot(2, column_count, 1)
    axis.imshow(image)
    axis.set_title("Original Image")
    axis.axis("off")

    axis = figure.add_subplot(2, column_count, 2)
    axis.imshow(background_mask, cmap="gray")
    axis.set_title("Image mask")
    axis.axis("off")
    axis.text(
        0.5,
        -0.05,
        round(background_percentage, 3),
        ha="center",
        va="top",
        transform=axis.transAxes,
    )

    for position, (name, mask) in enumerate(masks.items(), start=3):
        axis = figure.add_subplot(2, column_count, position)
        axis.imshow(mask, cmap="gray")
        axis.set_title(f"{name.capitalize()} mask")
        axis.axis("off")
        axis.text(
            0.5,
            -0.05,
            round(float(results[name]["percentage"]), 3),
            ha="center",
            va="top",
            transform=axis.transAxes,
        )

    figure.subplots_adjust(hspace=0.4)


def process_images_in_folder(
    folder_path: ImagePath,
    color_names: Sequence[str],
    color_ranges: Sequence[ColorRange],
) -> list[tuple[str, ColorResults]]:
    """Analyze supported images in a folder in deterministic filename order."""
    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"Image folder does not exist: {folder}")

    results: list[tuple[str, ColorResults]] = []
    image_paths = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in _SUPPORTED_IMAGE_SUFFIXES
    )
    for image_path in image_paths:
        print(image_path.name)
        result = calculate_color_percentage(image_path, color_names, color_ranges)
        results.append((image_path.name, result))
    return results
