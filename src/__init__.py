# -*- coding: utf-8 -*-
# @Author: Bruno Piato
# @Date:   2026-02-12 07:38:47
# @Last Modified by:   Bruno Piato
# @Last Modified time: 2026-02-12 07:54:21
# __init__.py

from .functions import calculate_color_percentage, process_images_in_folder, pick_color_from_image

__version__ = '0.1.0'
__name__ = '_Hippocampus reidi_'
__author__ = 'Bruno Garcia Piato'

__all__ = [
    'calculate_color_percentage',
    'pick_color_from_image',
    'process_images_in_folder',
]

