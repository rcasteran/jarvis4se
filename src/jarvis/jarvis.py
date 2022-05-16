#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import re
import os
import shutil
import getpass
from datetime import datetime
from io import StringIO

from IPython.core.magic import (Magics, magics_class, cell_magic)

# Modules
from xml_adapter import parse_xml, generate_xml


# The class MUST call this class decorator at creation time
@magics_class
class MyMagics(Magics):
    """Magic iPython class"""
    def __init__(self, shell, parser):
        # You must call the parent constructor
        super().__init__(shell)
        self.parser = parser

    @cell_magic
    def jarvis(self, _, cell):
        """Entry point for jarvi4se"""
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
                xml_lists = parse_xml(f"{xml_name}.xml")
                if isinstance(xml_lists, str):
                    print(xml_lists)
                    return
                else:
                    print(f"{xml_name}.xml parsed")
                    output_xml = generate_xml(f"{xml_name}.xml")
            # Else create an empty xml_lists
            # or will be named by default "Outpout"
            else:
                xml_lists = [set(), [], [], set(), set(), set(), set(), set(), set(), set(), set(),
                             set()]
                if len(xml_name) > 1:
                    print(f"Creating {xml_name}.xml !")
                    output_xml = generate_xml(f"{xml_name}.xml")
                    output_xml.write()
                else:
                    print("Xml's file does not exists, creating it('output.xml' by default) !")
                    output_xml = generate_xml("")
                    output_xml.write()

            xml_dict = {'xml_function_list': xml_lists[0],
                        'xml_consumer_function_list': xml_lists[1],
                        'xml_producer_function_list': xml_lists[2],
                        'xml_data_list': xml_lists[3],
                        'xml_state_list': xml_lists[4],
                        'xml_transition_list': xml_lists[5],
                        'xml_fun_elem_list': xml_lists[6],
                        'xml_chain_list': xml_lists[7],
                        'xml_attribute_list': xml_lists[8],
                        'xml_fun_inter_list': xml_lists[9],
                        'xml_phy_elem_list': xml_lists[10],
                        'xml_phy_inter_list': xml_lists[11],
                        'output_xml': output_xml,
                        'xml_name': xml_name}

            update = self.parser.lookup_table(input_str, **xml_dict)

            if not update:
                return
            else:
                if 1 in update:
                    self.show_model_update_msg(xml_name)
                else:
                    self.show_no_model_update_msg(xml_name)
        else:
            print(
                "Bad model's declaration, model's name should be written or add a ' '(blank space) "
                "after 'with' command to create default 'Output.xml'")

    @classmethod
    def show_model_update_msg(cls, xml_name):
        print(f"{xml_name}.xml updated")

    @classmethod
    def show_no_model_update_msg(cls, xml_name):
        print(f"No update for {xml_name}.xml")


def greet_user():
    """Greets the user according to the time thanks to :
    https://ireadblog.com/posts/141/how-to-build-your-personal-ai-assistant-using-python"""
    hour = datetime.now().hour
    # Use getpass() because available on Unix/Windows
    user_name = getpass.getuser()
    if 6 <= hour < 12:
        print(f"Good Morning {user_name}")
    elif 12 <= hour < 16:
        print(f"Good afternoon {user_name}")
    elif 16 <= hour < 19:
        print(f"Good Evening {user_name}")
    print("I am Jarvis. How may I assist you?")


def clean_diagram_folder():
    """Clean/erase all files within Diagram's folder"""
    folder = './Diagrams'
    if not os.path.exists(folder):
        os.mkdir(folder)
    else:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as err:
                print(f"Failed to delete {file_path}. Reason: {err}")
