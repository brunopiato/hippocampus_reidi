"""Interactive RGB color pickers."""

from __future__ import annotations

from os import PathLike

import cv2
import matplotlib.pyplot as plt


def pick_color_from_image(image_path: str | PathLike[str]) -> list[list[int]]:
    """Collect RGB values from an image displayed in an OpenCV window."""
    colors: list[list[int]] = []
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    def pick_color(
        event: int,
        x: int,
        y: int,
        _flags: int,
        _parameter: object,
    ) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        blue, green, red = image[y, x]
        colors.append([int(red), int(green), int(blue)])
        print(f"Color at ({x}, {y}): R={red}, G={green}, B={blue}")

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", pick_color)
    while True:
        cv2.imshow("Image", image)
        key = cv2.waitKey(1)
        if key == 27 or cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
            break
    cv2.destroyAllWindows()
    return colors


def pick_color_from_image_matplotlib(
    image_path: str | PathLike[str],
) -> list[list[int]]:
    """Collect RGB values from an image using an ipympl-backed widget."""
    try:
        import ipywidgets as widgets
        from IPython.display import display
    except ImportError as error:
        raise RuntimeError(
            "Notebook color picking requires the project dependencies. "
            "Install them with `python -m pip install -e .`."
        ) from error

    colors: list[list[int]] = []
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with plt.ioff():
        figure, axis = plt.subplots()
    axis.imshow(image)
    axis.set_title("Click on the image to pick colors")
    axis.axis("off")

    output = widgets.Output()
    done = widgets.Button(description="End color selection", button_style="success")

    def on_click(event: object) -> None:
        if event.inaxes != axis or event.xdata is None or event.ydata is None:
            return

        x, y = int(event.xdata), int(event.ydata)
        red, green, blue = image[y, x]
        colors.append([int(red), int(green), int(blue)])
        output.append_stdout(f"Pixel ({x}, {y}) -> RGB = {red}, {green}, {blue}\n")
        axis.scatter(x, y, c="red", s=40)
        figure.canvas.draw_idle()

    def finish(_button: object) -> None:
        figure.canvas.mpl_disconnect(connection_id)
        done.disabled = True
        plt.close(figure)
        output.append_stdout("Selection finished.\n")
        output.append_stdout(f"Captured colors: {colors}\n")

    connection_id = figure.canvas.mpl_connect("button_press_event", on_click)
    done.on_click(finish)
    display(widgets.VBox([figure.canvas, done, output]))
    return colors
