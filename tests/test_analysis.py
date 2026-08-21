from pathlib import Path

import cv2
import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from hippocampus_reidi.analysis import (  # noqa: E402
    calculate_color_percentage,
    process_images_in_folder,
)


def write_rgb_image(path: Path, image: np.ndarray) -> None:
    success = cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    assert success


def test_calculate_color_percentage_excludes_black_background(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image = np.array(
        [
            [[0, 0, 0], [255, 0, 0]],
            [[0, 255, 0], [200, 10, 10]],
        ],
        dtype=np.uint8,
    )
    write_rgb_image(image_path, image)

    results = calculate_color_percentage(
        image_path,
        color_names=["red", "green"],
        color_ranges=[[[190, 0, 0], [255, 20, 20]], [[0, 200, 0], [20, 255, 20]]],
    )

    assert results["red"]["pixels"] == 2
    assert results["red"]["percentage"] == pytest.approx(2 / 3)
    assert results["green"]["pixels"] == 1
    assert results["green"]["percentage"] == pytest.approx(1 / 3)
    assert results["image"]["pixels"] == 1
    assert results["image"]["percentage"] == pytest.approx(1 / 4)


@pytest.mark.parametrize(
    ("color_names", "color_ranges", "message"),
    [
        (["red"], [], "same number"),
        (["red", "red"], [[[0, 0, 0], [1, 1, 1]]] * 2, "unique"),
        (["red"], [[[255, 0, 0], [100, 1, 1]]], "Lower RGB bound"),
        (["red"], [[[0, 0], [1, 1]]], "RGB triplets"),
    ],
)
def test_calculate_color_percentage_validates_ranges(
    tmp_path: Path,
    color_names: list[str],
    color_ranges: list[list[list[int]]],
    message: str,
) -> None:
    image_path = tmp_path / "sample.png"
    write_rgb_image(image_path, np.full((1, 1, 3), 255, dtype=np.uint8))

    with pytest.raises(ValueError, match=message):
        calculate_color_percentage(image_path, color_names, color_ranges)


def test_calculate_color_percentage_rejects_empty_foreground(tmp_path: Path) -> None:
    image_path = tmp_path / "black.png"
    write_rgb_image(image_path, np.zeros((2, 2, 3), dtype=np.uint8))

    with pytest.raises(ValueError, match="no non-black foreground"):
        calculate_color_percentage(image_path, ["red"], [[[100, 0, 0], [255, 10, 10]]])


def test_process_images_in_folder_is_sorted_and_filters_files(tmp_path: Path) -> None:
    image = np.full((1, 1, 3), [255, 0, 0], dtype=np.uint8)
    write_rgb_image(tmp_path / "b.png", image)
    write_rgb_image(tmp_path / "a.JPG", image)
    (tmp_path / "notes.txt").write_text("not an image", encoding="utf-8")

    results = process_images_in_folder(
        tmp_path,
        color_names=["red"],
        color_ranges=[[[200, 0, 0], [255, 10, 10]]],
    )

    assert [filename for filename, _result in results] == ["a.JPG", "b.png"]
