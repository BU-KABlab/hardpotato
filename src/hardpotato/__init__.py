"""
hardpotato library

"""

from . import load_data, potentiostat

__version__ = "1.3.14"
__author__ = "Oliver Rodriguez, Odin Holmes, Gregory Robben"

# modules to import when user does 'from pypotato import *':
__all__ = ["potentiostat", "load_data"]
