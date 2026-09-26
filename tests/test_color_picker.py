from __future__ import annotations

import sys
from contextlib import nullcontext
from types import SimpleNamespace

import numpy as np

from hippocampus_reidi import color_picker


class FakeOutput:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def append_stdout(self, message: str) -> None:
        self.messages.append(message)


class FakeButton:
    def __init__(self, **_: object) -> None:
        self.callback = None
        self.disabled = False

    def on_click(self, callback: object) -> None:
        self.callback = callback


class FakeCanvas:
    def __init__(self) -> None:
        self.callback = None
        self.disconnect_calls: list[int] = []

    def mpl_connect(self, _event_name: str, callback: object) -> int:
        self.callback = callback
        return 1

    def mpl_disconnect(self, connection_id: int) -> None:
        self.disconnect_calls.append(connection_id)

    def draw_idle(self) -> None:
        pass


class FakeAxis:
    def imshow(self, _image: np.ndarray) -> None:
        pass

    def set_title(self, _title: str) -> None:
        pass

    def axis(self, _value: str) -> None:
        pass

    def scatter(self, _x: int, _y: int, **_: object) -> None:
        pass


class FakeFigure:
    def __init__(self) -> None:
        self.canvas = FakeCanvas()


def test_matplotlib_picker_writes_one_message_per_click(monkeypatch) -> None:
    output = FakeOutput()
    button = FakeButton()
    figure = FakeFigure()
    axis = FakeAxis()
    displayed: list[tuple[object, ...]] = []
    show_calls: list[None] = []

    monkeypatch.setattr(
        color_picker.cv2,
        "imread",
        lambda _path: np.array([[[3, 2, 1]]], dtype=np.uint8),
    )
    monkeypatch.setattr(
        color_picker.cv2,
        "cvtColor",
        lambda image, _code: image[..., ::-1],
    )
    monkeypatch.setattr(color_picker.plt, "subplots", lambda: (figure, axis))
    monkeypatch.setattr(color_picker.plt, "ioff", lambda: nullcontext())
    monkeypatch.setattr(color_picker.plt, "close", lambda _figure: None)
    monkeypatch.setattr(color_picker.plt, "show", lambda: show_calls.append(None))

    class FakeWidgets:
        @staticmethod
        def Output():
            return output

        @staticmethod
        def Button(**_kwargs: object):
            return button

        @staticmethod
        def VBox(children: list[object]):
            return children

    monkeypatch.setitem(sys.modules, "ipywidgets", FakeWidgets)
    monkeypatch.setattr(
        "IPython.display.display",
        lambda *objects: displayed.append(objects),
    )

    color_picker.pick_color_from_image_matplotlib("image.jpg")

    event = SimpleNamespace(inaxes=axis, xdata=0.0, ydata=0.0)
    figure.canvas.callback(event)

    assert output.messages == ["Pixel (0, 0) -> RGB = 1, 2, 3\n"]
    assert len(displayed) == 1
    assert show_calls == []
