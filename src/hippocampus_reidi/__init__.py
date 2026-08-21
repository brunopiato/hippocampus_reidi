# -*- coding: utf-8 -*-
# @Author: Bruno Piato
# @Date:   2026-08-21 13:41:07
# @Last Modified by:   Bruno Piato
# @Last Modified time: 2026-08-21 14:58:33
"""Public API for the Hippocampus reidi image analysis package."""

from importlib.metadata import version

from .analysis import calculate_color_percentage, process_images_in_folder
from .color_picker import pick_color_from_image, pick_color_from_image_matplotlib

__version__ = version("hippocampus-reidi")
__author__ = "Amanda do Carmo Vaccani, Natalie VillarFreret-Meurer, Bruno GarciaPiato, Vinicius Neres-Lima & Luciano Neves Santos"

__all__ = [
    "calculate_color_percentage",
    "pick_color_from_image",
    "pick_color_from_image_matplotlib",
    "process_images_in_folder",
]
