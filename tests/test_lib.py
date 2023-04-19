"""@defgroup test_lib
Test libraries
"""

# Libraries
import os
from pathlib import Path
from IPython import get_ipython

# Modules
import jarvis


def get_jarvis4se():
    """@ingroup test_lib
    Start an ipython session, init parser and jarvis4se magic call

    @return jarvis4se magic call, jarvis4se diagram generator, jarvis4se magic tool
    """
    ip = get_ipython()
    generator_jarvis = jarvis.PlantUmlGen()
    parser = jarvis.command_parser.CmdParser(generator_jarvis)
    my_magic_jarvis = jarvis.MagicJarvis(ip, parser)
    my_magic_tool = jarvis.MagicTools(ip, generator_jarvis)
    return my_magic_jarvis, generator_jarvis, my_magic_tool


def remove_xml_file(file_name):
    """@ingroup test_lib
    Remove the XML file generated during the test

    @return None
    """
    file_path = os.path.join("./", f"{file_name}.xml")
    path = Path(file_path)
    if path:
        os.remove(path)
