"""Public API for the Hippocampus reidi image-analysis workflow."""

from importlib.metadata import version

from .analysis import analyze_folder, analyze_image, make_patternize_color_ranges
from .color_picker import pick_color_from_image, pick_color_from_image_matplotlib
from .visualization import plot_image_analysis

__version__ = version("hippocampus-reidi")
__author__ = (
    "Amanda do Carmo Vaccani, Natalie VillarFreret-Meurer, Bruno GarciaPiato, "
    "Vinicius Neres-Lima & Luciano Neves Santos"
)

__all__ = [
    "analyze_folder",
    "analyze_image",
    "make_patternize_color_ranges",
    "pick_color_from_image",
    "pick_color_from_image_matplotlib",
    "plot_image_analysis",
]
