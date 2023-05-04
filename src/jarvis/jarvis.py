"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re
import os
import getpass
import shutil
from datetime import datetime
from io import StringIO
from IPython.core.magic import (Magics, magics_class, cell_magic)

# Modules
from xml_adapter import XmlWriter3SE, XmlParser3SE
from tools import Logger


# The class MUST call this class decorator at creation time
@magics_class
class MagicJarvis(Magics):
    """Magic iPython class"""
    def __init__(self, shell, parser):
        # You must call the parent constructor
        super().__init__(shell)
        self.parser = parser

    @cell_magic
    def jarvis(self, _, cell):
        """Entry point for jarvi4se"""
        # Initialize xml_parser i.e. empty obj_dict that will contain objet's lists
        xml_parser = XmlParser3SE()
        obj_dict = xml_parser.xml_dict
        # We create a string buffer containing the
        # contents of the cell.
        sio = StringIO(cell)
        # Take the value within the buffer
        input_str = sio.getvalue()
        # Delete the '"' from input string, to avoid xml to plantuml errors.
        input_str = input_str.replace('"', "")
        # Delete extra whitespaces
        input_str = re.sub(' +', ' ', input_str)
        # Get model's declaration, need a space after "with" otherwise print a message
        xml_name_str = re.match(r"^with (.*)(?=.|\n)", input_str, re.MULTILINE)
        if xml_name_str:
            xml_name = xml_name_str.group(1)
            # If the model(i.e. file) already exists, parse it to extract lists
            if os.path.isfile(f"{xml_name}.xml"):
                obj_dict = xml_parser.parse_xml(f"{xml_name}.xml")
                Logger.set_info(__name__,
                                f"{xml_name}.xml parsed")
                output_xml = XmlWriter3SE(f"{xml_name}.xml")
            # Else create an empty xml_lists
            # or will be named by default "Outpout"
            else:
                if len(xml_name) > 1:
                    Logger.set_info(__name__,
                                    f"Creating {xml_name}.xml !")

                    output_xml = XmlWriter3SE(f"{xml_name}.xml")
                else:
                    Logger.set_info(__name__,
                                    "Xml's file does not exists, creating it ('output.xml' by default) !")
                    output_xml = XmlWriter3SE("")
                output_xml.write()

            obj_dict['output_xml'] = output_xml
            update = self.parser.lookup_table(input_str, **obj_dict)

            if not update:
                return

            if 1 in update:
                Logger.set_info(__name__,
                                f"{output_xml.file} updated")
            else:
                Logger.set_info(__name__,
                                f"No update for {output_xml.file}")
        else:
            Logger.set_error(__name__,
                             "Bad model's declaration, model's name should be written or add a ' '(blank space) "
                             "after 'with' command to create default 'Output.xml'")


def greet_user():
    """Greets the user according to the time thanks to :
    https://ireadblog.com/posts/141/how-to-build-your-personal-ai-assistant-using-python"""
    hour = datetime.now().hour
    # Use getpass() because available on Unix/Windows
    user_name = getpass.getuser()

    # Single display (not related to logging)
    if 6 <= hour < 12:
        print(f"Good morning {user_name}")
    elif 12 <= hour < 16:
        print(f"Good afternoon {user_name}")
    elif 16 <= hour < 19:
        print(f"Good evening {user_name}")
    else:
        print(f"Hello {user_name}")

    print("I am Jarvis. How may I assist you?")


def clean_folders():
    """ Clean Jarvis folder
    @return None
    """
    for folder in ["./diagrams", "./log"]:
        if os.path.isdir(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as ex:
                    # function called before Logger initialization.
                    print('[ERROR] Failed to delete %s. Reason: %s' % (file_path, ex))
