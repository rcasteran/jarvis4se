"""An example magic"""
__version__ = '0.0.1'
from . import command_parser
from .jarvis import MagicJarvis, greet_user
from tools import MagicTools
from plantuml_adapter import PlantUmlGen


def load_ipython_extension(ipython):
    """Entry point from notebook/ipython when executing %(re)load_ext jarvis"""
    generator = PlantUmlGen()
    parser = command_parser.CmdParser(generator)
    jarvis4se = MagicJarvis(ipython, parser)
    tools = MagicTools(ipython, generator)
    ipython.register_magics(jarvis4se, tools)
    greet_user()
