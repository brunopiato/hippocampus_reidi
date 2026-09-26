"""Image analysis and CSV export for standardized seahorse photographs."""

from __future__ import annotations

import csv
from collections.abc import Mapping, Sequence
from os import PathLike
from pathlib import Path
from typing import TypedDict

import cv2
import numpy as np
from numpy.typing import NDArray

type ImagePath = str | PathLike[str]
type RGBColor = tuple[int, int, int]
type ColorRange = tuple[Sequence[int], Sequence[int]]


class ColorMeasurement(TypedDict):
    """Measurements for one selected RGB range."""

    lower: RGBColor
    upper: RGBColor
    pixels: int
    percentage: float


class ImageAnalysis(TypedDict):
    """Measurements produced for one image."""

    image: str
    total_pixels: int
    body_pixels: int
    background_pixels: int
    background_percentage: float
    colors: dict[str, ColorMeasurement]


_BACKGROUND_COLOR = np.array([0, 0, 0], dtype=np.uint8)
_SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
_DEFAULT_OUTPUT_DIRECTORY = Path("data/output")
_DEFAULT_OUTPUT_FILENAME = "biofluorescence_results.csv"


def _read_rgb_image(image_path: ImagePath) -> NDArray[np.uint8]:
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def _validate_color_ranges(
    color_ranges: Mapping[str, ColorRange],
) -> list[tuple[str, NDArray[np.uint8], NDArray[np.uint8], RGBColor, RGBColor]]:
    if not color_ranges:
        raise ValueError("color_ranges must contain at least one RGB range")

    validated_ranges: list[
        tuple[str, NDArray[np.uint8], NDArray[np.uint8], RGBColor, RGBColor]
    ] = []
    for name, bounds in color_ranges.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Color range names must be non-empty strings")
        if name.lower() == "background":
            raise ValueError("'background' is reserved for the image background")

        try:
            bounds_array = np.asarray(bounds, dtype=np.int64)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Color range for {name!r} must contain two RGB triplets") from error

        if bounds_array.shape != (2, 3):
            raise ValueError(f"Color range for {name!r} must contain two RGB triplets")
        if np.any((bounds_array < 0) | (bounds_array > 255)):
            raise ValueError(f"RGB values for {name!r} must be between 0 and 255")

        lower_tuple = tuple(int(value) for value in bounds_array[0])
        upper_tuple = tuple(int(value) for value in bounds_array[1])
        if any(lower > upper for lower, upper in zip(lower_tuple, upper_tuple, strict=True)):
            raise ValueError(f"Lower RGB bound must not exceed upper bound for {name!r}")

        validated_ranges.append(
            (
                name,
                np.asarray(lower_tuple, dtype=np.uint8),
                np.asarray(upper_tuple, dtype=np.uint8),
                lower_tuple,
                upper_tuple,
            )
        )

    return validated_ranges


def make_patternize_color_ranges(
    rgb_colors: Mapping[str, Sequence[int]],
    col_offset: float = 0.10,
) -> dict[str, ColorRange]:
    """Build RGB ranges using Patternize's per-channel color tolerance.

    Patternize selects a pixel when ``abs(pixel - RGB) < col_offset * 255`` for
    each channel. This function converts that strict condition into inclusive
    integer RGB bounds that can be passed to :func:`analyze_image`.

    This reproduces the color-threshold rule only. It does not reproduce
    Patternize image alignment, resampling, outline masking, or ``patArea``'s
    denominator.
    """
    try:
        offset = float(col_offset)
    except (TypeError, ValueError) as error:
        raise ValueError("col_offset must be a finite number greater than zero") from error
    if not np.isfinite(offset) or offset <= 0:
        raise ValueError("col_offset must be a finite number greater than zero")

    color_ranges: dict[str, ColorRange] = {}
    delta = offset * 255
    for name, rgb_color in rgb_colors.items():
        try:
            center = np.asarray(rgb_color, dtype=np.float64)
        except (TypeError, ValueError) as error:
            raise ValueError(f"RGB value for {name!r} must contain three integers") from error

        if (
            center.shape != (3,)
            or np.any(~np.isfinite(center))
            or np.any(center != np.floor(center))
            or np.any((center < 0) | (center > 255))
        ):
            raise ValueError(f"RGB value for {name!r} must contain three integers from 0 to 255")

        lower = np.clip(np.floor(center - delta) + 1, 0, 255).astype(int)
        upper = np.clip(np.ceil(center + delta) - 1, 0, 255).astype(int)
        color_ranges[name] = (
            tuple(int(value) for value in lower),
            tuple(int(value) for value in upper),
        )

    _validate_color_ranges(color_ranges)
    return color_ranges


def _analyze_rgb_image(
    image: NDArray[np.uint8],
    image_name: str,
    validated_ranges: Sequence[
        tuple[str, NDArray[np.uint8], NDArray[np.uint8], RGBColor, RGBColor]
    ],
) -> tuple[ImageAnalysis, NDArray[np.uint8], dict[str, NDArray[np.uint8]]]:
    total_pixels = int(image.shape[0] * image.shape[1])
    background_mask = cv2.inRange(image, _BACKGROUND_COLOR, _BACKGROUND_COLOR)
    background_pixels = int(cv2.countNonZero(background_mask))
    body_pixels = total_pixels - background_pixels
    if body_pixels == 0:
        raise ValueError("The image contains no non-black foreground pixels")

    body_mask = cv2.bitwise_not(background_mask)
    colors: dict[str, ColorMeasurement] = {}
    masks: dict[str, NDArray[np.uint8]] = {}
    for name, lower, upper, lower_tuple, upper_tuple in validated_ranges:
        mask = cv2.inRange(image, lower, upper)
        mask = cv2.bitwise_and(mask, body_mask)
        pixels = int(cv2.countNonZero(mask))
        colors[name] = {
            "lower": lower_tuple,
            "upper": upper_tuple,
            "pixels": pixels,
            "percentage": pixels / body_pixels * 100,
        }
        masks[name] = mask

    analysis: ImageAnalysis = {
        "image": image_name,
        "total_pixels": total_pixels,
        "body_pixels": body_pixels,
        "background_pixels": background_pixels,
        "background_percentage": background_pixels / total_pixels * 100,
        "colors": colors,
    }
    return analysis, background_mask, masks


def analyze_image(
    image_path: ImagePath,
    color_ranges: Mapping[str, ColorRange],
) -> ImageAnalysis:
    """Calculate RGB-range coverage for one standardized image.

    Pure black pixels define the background and are excluded from the denominator and
    numerator of every selected color range. Color ranges are evaluated independently,
    so overlapping ranges may count the same body pixel more than once.
    """
    validated_ranges = _validate_color_ranges(color_ranges)
    image = _read_rgb_image(image_path)
    analysis, _background_mask, _masks = _analyze_rgb_image(
        image,
        Path(image_path).name,
        validated_ranges,
    )
    return analysis


def _resolve_output_path(output_path: ImagePath) -> Path:
    path = Path(output_path)
    if path.suffix.lower() != ".csv":
        path /= _DEFAULT_OUTPUT_FILENAME
    return path


def _write_results_csv(
    results: Sequence[tuple[str, ImageAnalysis]],
    output_path: ImagePath,
) -> Path:
    resolved_path = _resolve_output_path(output_path)
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "image",
        "total_pixels",
        "body_pixels",
        "background_pixels",
        "background_percentage",
        "color",
        "pixels",
        "percentage",
        "lower_rgb",
        "upper_rgb",
    ]

    with resolved_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for filename, analysis in results:
            for color_name, measurement in analysis["colors"].items():
                writer.writerow(
                    {
                        "image": filename,
                        "total_pixels": analysis["total_pixels"],
                        "body_pixels": analysis["body_pixels"],
                        "background_pixels": analysis["background_pixels"],
                        "background_percentage": analysis["background_percentage"],
                        "color": color_name,
                        "pixels": measurement["pixels"],
                        "percentage": measurement["percentage"],
                        "lower_rgb": ",".join(str(value) for value in measurement["lower"]),
                        "upper_rgb": ",".join(str(value) for value in measurement["upper"]),
                    }
                )
    return resolved_path


def analyze_folder(
    folder_path: ImagePath,
    color_ranges: Mapping[str, ColorRange],
    output_path: ImagePath | None = _DEFAULT_OUTPUT_DIRECTORY,
) -> list[tuple[str, ImageAnalysis]]:
    """Analyze supported images in a folder and optionally save a CSV summary.

    Images are processed in deterministic filename order. By default, results are saved
    to data/output/biofluorescence_results.csv. Pass None to disable CSV export or
    provide a directory or CSV path to choose another destination.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        raise ValueError(f"Image folder does not exist: {folder}")

    validated_ranges = _validate_color_ranges(color_ranges)
    image_paths = sorted(
        (
            path
            for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in _SUPPORTED_IMAGE_SUFFIXES
        ),
        key=lambda path: path.name.casefold(),
    )
    results: list[tuple[str, ImageAnalysis]] = []
    for image_path in image_paths:
        image = _read_rgb_image(image_path)
        analysis, _background_mask, _masks = _analyze_rgb_image(
            image,
            image_path.name,
            validated_ranges,
        )
        results.append((image_path.name, analysis))

    if output_path is not None:
        _write_results_csv(results, output_path)
    return results
