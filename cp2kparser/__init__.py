"""A package for parsing CP2K input files."""

from .__version__ import __version__

from .parser import read_input

__version__ = __version__
__author__ = "B. F. van Beek"
__email__ = 'b.f.van.beek@vu.nl'

__all__ = ['parser']
