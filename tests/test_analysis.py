import csv
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from hippocampus_reidi import (  # noqa: E402
    analyze_folder,
    analyze_image,
    make_patternize_color_ranges,
)


def write_rgb_image(path: Path, image: np.ndarray) -> None:
    success = cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    assert success


def test_analyze_image_excludes_black_background(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = np.array(
        [
            [[0, 0, 0], [255, 0, 0]],
            [[0, 255, 0], [200, 10, 10]],
        ],
        dtype=np.uint8,
    )
    write_rgb_image(image_path, image)

    results = analyze_image(
        image_path,
        color_ranges={
            "red": ((190, 0, 0), (255, 20, 20)),
            "green": ((0, 200, 0), (20, 255, 20)),
        },
    )

    assert results["body_pixels"] == 3
    assert results["background_pixels"] == 1
    assert results["background_percentage"] == pytest.approx(25)
    assert results["colors"]["red"]["pixels"] == 2
    assert results["colors"]["red"]["percentage"] == pytest.approx(2 / 3 * 100)
    assert results["colors"]["green"]["pixels"] == 1
    assert results["colors"]["green"]["percentage"] == pytest.approx(1 / 3 * 100)


def test_analyze_image_does_not_count_black_pixels_in_color_range(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = np.array([[[0, 0, 0], [255, 0, 0]]], dtype=np.uint8)
    write_rgb_image(image_path, image)

    results = analyze_image(
        image_path,
        color_ranges={
            "black": ((0, 0, 0), (0, 0, 0)),
            "red": ((255, 0, 0), (255, 0, 0)),
        },
    )

    assert results["colors"]["black"]["pixels"] == 0
    assert results["colors"]["red"]["percentage"] == pytest.approx(100)


@pytest.mark.parametrize(
    ("color_ranges", "message"),
    [
        ({}, "at least one"),
        ({"red": ((255, 0, 0), (100, 1, 1))}, "Lower RGB bound"),
        ({"red": ((0, 0), (1, 1))}, "RGB triplets"),
        ({"background": ((0, 0, 0), (1, 1, 1))}, "reserved"),
    ],
)
def test_analyze_image_validates_ranges(
    tmp_path: Path,
    color_ranges: dict[str, tuple[tuple[int, ...], tuple[int, ...]]],
    message: str,
) -> None:
    image_path = tmp_path / "sample.png"
    write_rgb_image(image_path, np.full((1, 1, 3), 255, dtype=np.uint8))

    with pytest.raises(ValueError, match=message):
        analyze_image(image_path, color_ranges)


def test_analyze_image_rejects_empty_foreground(tmp_path: Path) -> None:
    image_path = tmp_path / "black.png"
    write_rgb_image(image_path, np.zeros((2, 2, 3), dtype=np.uint8))

    with pytest.raises(ValueError, match="no non-black foreground"):
        analyze_image(
            image_path,
            {"red": ((100, 0, 0), (255, 10, 10))},
        )


def test_make_patternize_color_ranges_matches_channel_tolerance() -> None:
    color_ranges = make_patternize_color_ranges(
        {"green": (110, 172, 3)},
        col_offset=0.10,
    )

    assert color_ranges == {"green": ((85, 147, 0), (135, 197, 28))}


@pytest.mark.parametrize(
    "col_offset",
    [0, -0.1, float("nan"), float("inf")],
)
def test_make_patternize_color_ranges_validates_col_offset(col_offset: float) -> None:
    with pytest.raises(ValueError, match="col_offset"):
        make_patternize_color_ranges({"green": (110, 172, 3)}, col_offset)


def test_analyze_folder_is_sorted_filters_files_and_writes_csv(tmp_path: Path) -> None:
    image = np.full((1, 1, 3), [255, 0, 0], dtype=np.uint8)
    write_rgb_image(tmp_path / "b.png", image)
    write_rgb_image(tmp_path / "a.JPG", image)
    (tmp_path / "notes.txt").write_text("not an image", encoding="utf-8")

    output_directory = tmp_path / "output"
    results = analyze_folder(
        tmp_path,
        {"red": ((200, 0, 0), (255, 10, 10))},
        output_path=output_directory,
    )

    assert [filename for filename, _result in results] == ["a.JPG", "b.png"]
    output_path = output_directory / "biofluorescence_results.csv"
    with output_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    assert [row["image"] for row in rows] == ["a.JPG", "b.png"]
    assert rows[0]["body_pixels"] == "1"
    assert rows[0]["background_pixels"] == "0"
    assert rows[0]["color"] == "red"
    assert rows[0]["percentage"] == "100.0"


def test_analyze_folder_can_skip_csv_export(tmp_path: Path) -> None:
    image = np.full((1, 1, 3), [255, 0, 0], dtype=np.uint8)
    write_rgb_image(tmp_path / "sample.png", image)

    analyze_folder(
        tmp_path,
        {"red": ((200, 0, 0), (255, 10, 10))},
        output_path=None,
    )

    assert not (tmp_path / "biofluorescence_results.csv").exists()
