"""Synthesizers module."""

from ctgan.synthesizer.ctgan import CTGAN_New
from ctgan.synthesizer.tvae import TVAE

__all__ = (
    'CTGAN_New',
    'TVAE'
)


def get_all_synthesizers():
    return {
        name: globals()[name]
        for name in __all__
    }
