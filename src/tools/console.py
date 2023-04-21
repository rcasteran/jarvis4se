"""@defgroup tools
Tooling module
"""

# Libraries
import re
import os

# Modules
from jarvis.command_parser import CmdParser
from plantuml_adapter import PlantUmlGen
from xml_adapter import XmlWriter3SE, XmlParser3SE


def main():
    """@ingroup tools
    @anchor main
    Jarvis console
    @return None
    """
    is_exit = False

    # Initialize jarvis4se
    generator = PlantUmlGen()
    parser = CmdParser(generator)

    # Initialize xml_parser i.e. empty obj_dict that will contain objet's lists
    xml_parser = XmlParser3SE()
    obj_dict = xml_parser.xml_dict

    # Initialize model name
    xml_name = ""

    while not is_exit:
        # Add carriage return to input due to MagicCell compatibility
        input_str = input(f"? ") + "\n"
        if input_str == "":
            continue
        elif input_str == "q\n":
            is_exit = True
        else:
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
                    print(f"{xml_name}.xml parsed")
                    output_xml = XmlWriter3SE(f"{xml_name}.xml")
                # Else create an empty xml_lists
                # or will be named by default "Output"
                else:
                    if len(xml_name) > 1:
                        print(f"Creating {xml_name}.xml !")
                        output_xml = XmlWriter3SE(f"{xml_name}.xml")
                    else:
                        print("Xml's file does not exists, creating it('output.xml' by default) !")
                        output_xml = XmlWriter3SE("")
                    output_xml.write()

                obj_dict['output_xml'] = output_xml
            elif len(xml_name) > 0:
                update = parser.lookup_table(input_str, **obj_dict)

                if 1 in update:
                    print(f"{output_xml.file} updated")
                else:
                    print(f"No update for {output_xml.file}")
            else:
                print(
                    "Bad model's declaration, model's name should be written or add a ' '(blank space) "
                    "after 'with' command to create default 'Output.xml'")


if __name__ == "__main__":
    main()
