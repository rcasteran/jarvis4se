"""An example magic"""
__version__ = '0.0.1'

from .jarvis import MyMagics
from .jarvis import clean_diagram_folder
from .jarvis import greet_user


def load_ipython_extension(ipython):
    ipython.register_magics(MyMagics)
    clean_diagram_folder()
    greet_user()
