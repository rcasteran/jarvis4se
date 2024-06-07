""" @package jarvis
Jarvis module

Contains IPython Magic Class with magic cell as entry point of Jarvis
"""
__version__ = '0.0.1'
from . import command_parser
from .jarvis import MagicJarvis, greet_user, clean_folders
from tools import MagicTools, Config
from plantuml_adapter import PlantUmlConnector
from open_modelica_adapter import OpenModelicaConnector


def load_ipython_extension(ipython):
    """Entry point from notebook/ipython when executing %(re)load_ext jarvis"""
    clean_folders()
    Config.read()
    generator = PlantUmlConnector()
    simulator = OpenModelicaConnector()
    parser = command_parser.CmdParser(generator, simulator)
    jarvis4se = MagicJarvis(ipython, parser)
    tools = MagicTools(ipython, generator, simulator)
    ipython.register_magics(jarvis4se, tools)
    greet_user()
