"""An example magic"""
__version__ = '0.0.1'
from . import command_parser
from .jarvis import MagicJarvis
from .jarvis import clean_diagram_folder
from .jarvis import greet_user
from tools import MagicTools


def load_ipython_extension(ipython):
    parser = command_parser.CmdParser()
    magics = MagicJarvis(ipython, parser)
    ipython.register_magics(magics, MagicTools)
    clean_diagram_folder()
    greet_user()
