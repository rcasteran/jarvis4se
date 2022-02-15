"""An example magic"""
__version__ = '0.0.1'

from .jarvis import MyMagics


def load_ipython_extension(ipython):
    ipython.register_magics(MyMagics)

