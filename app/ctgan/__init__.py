# -*- coding: utf-8 -*-

"""Top-level package for ctgan."""

__author__ = 'MIT Data To AI Lab'
__email__ = 'dailabmit@gmail.com'
__version__ = '0.6.1.dev0'

from ctgan.demo import load_demo
from ctgan.synthesizer.ctgan import CTGAN_New
from ctgan.synthesizer.tvae import TVAE

__all__ = (
    'CTGAN_New',
    'TVAE',
    'load_demo'
)
