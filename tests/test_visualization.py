from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")

from hippocampus_reidi import visualization  # noqa: E402


def write_rgb_image(path: Path, image: np.ndarray) -> None:
    success = cv2.imwrite(str(path), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    assert success


def test_plot_image_analysis_uses_one_axis_per_panel_and_disables_interactive_creation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    image_path = tmp_path / "sample.png"
    write_rgb_image(image_path, np.array([[[255, 0, 0], [0, 255, 0]]], dtype=np.uint8))
    color_ranges = {
        "red": ((200, 0, 0), (255, 10, 10)),
        "green": ((0, 200, 0), (10, 255, 10)),
        "blue": ((0, 0, 200), (10, 10, 255)),
    }
    interactive_states: list[bool] = []
    original_subplots = visualization.plt.subplots

    def capture_interactive_state(*args, **kwargs):
        interactive_states.append(visualization.plt.isinteractive())
        return original_subplots(*args, **kwargs)

    monkeypatch.setattr(visualization.plt, "subplots", capture_interactive_state)
    visualization.plt.ion()

    figure = visualization.plot_image_analysis(image_path, color_ranges)

    assert interactive_states == [False]
    assert len(figure.axes) == 2 + len(color_ranges)
