#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module to write plantuml text and write plantuml text within file"""
# Libraries
import os
import re
import inspect
import pathlib
import subprocess
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from plantuml import PlantUML


class PlantUmlPicoServer:
    """Class that looks for .jar file in root, check version and handle local PlantUML PicoWeb
    Server (https://plantuml.com/en/picoweb)"""
    def __init__(self):
        """If . jar, get it, check if picoweb is running, if not start new process else default url
        to online plantuml server"""
        jar_file = self.get_jar()
        if not jar_file:
            self.url = 'http://www.plantuml.com/plantuml/svg/'
        else:
            self.plantuml_jar_path = str(pathlib.Path(f'./{jar_file}'))
            self.version_cmd = ['java', '-jar', self.plantuml_jar_path, '-version']
            pico_cmd = ['java', '-DPLANTUML_LIMIT_SIZE=20000', '-jar', self.plantuml_jar_path,
                        '-picoweb']

            self.check_version()
            # Default localhost pico server
            self.url = "http://127.0.0.1:8080/plantuml/svg/"
            # Check if pico is running
            check_pico = False
            try:
                with urlopen(f"{self.url}"):
                    pass
            except HTTPError:
                pass
            except URLError:
                pass
            else:
                check_pico = True
            if not check_pico:
                self.process = subprocess.Popen(pico_cmd)

    @classmethod
    def get_jar(cls):
        """Get .jar file(s) in root and return first one if 'plantuml' in filename"""
        end_message = ", large diagrams will not be displayed.\n" \
                      "See: " \
                      "https://github.com/rcasteran/jarvis4se/blob/main/docs/installation.md"
        list_dir = os.listdir('.')
        if not any('.jar' in f for f in list_dir):
            print(f"WARNING:\nNot any .jar found for plantuml in root{end_message}")
            return None
        jar_list = [f.string for f in [re.search("plantuml.*jar", i) for i in list_dir] if f]
        if not jar_list:
            print(f"WARNING:\nNot any .jar found with 'plantuml' in its name{end_message}")
            return None
        # Return first filename with plantuml in it
        return jar_list.pop(0)

    def check_version(self):
        """Get .jar version and check with latest release"""
        jar_version = subprocess.run(
            self.version_cmd, capture_output=True, encoding="utf-8").stdout[17:25]
        github_url = "https://github.com/plantuml/plantuml/releases/latest"
        with urlopen(f"{github_url}") as rep:
            release_ver = str(rep.geturl())[-8:]

        if int(release_ver[0]) > int(jar_version[0]) or \
                int(release_ver[2:6]) > int(jar_version[2:6]) or \
                int(release_ver[7:len(release_ver)]) > int(jar_version[7:len(jar_version)]):
            print(f"WARNING:\nPlantUml .jar is not up-to-date, see latest release {github_url}")


class PlantUmlGen(PlantUmlPicoServer):
    """Class to encode PLantuml text and get server url as .svg"""
    def __init__(self):
        """Init pico server from PlantUMLPicoServer if .jar found or default online plantuml,
        send it to Plantuml for encoding and HTTP handling"""
        super().__init__()
        # PlantUML has encoding and handling errors
        self.server = PlantUML(url=self.url,
                               basic_auth={},
                               form_auth={}, http_opts={}, request_opts={})

    def get_diagram_url(self, string, from_diagram_cell=False):
        """
        Generate .svg from string using  plantuml default server or plantuml.jar picoweb
        """
        if not from_diagram_cell:
            full_string = "@startuml\nskin rose\nskinparam NoteBackgroundColor PapayaWhip\n" \
                          + string + "@enduml"
        else:
            full_string = string

        if len(string) > 15000 and not self.plantuml_jar_path:
            print(f"Diagram is too large to be display with Plantuml Online Server, "
                  f"please consider download https://plantuml.com/fr/download .jar")
            return None

        return self.server.get_url(full_string)


class StateDiagram:
    """Class for plantuml State diagram"""
    def __init__(self):
        """Init string"""
        self.string = inspect.cleandoc("""skinparam useBetaStyle true
                                            hide empty description
                                            <style>
                                                 .Entry{
                                                    FontColor white
                                                    BackgroundColor black
                                                 }
                                                 .Exit{
                                                    FontColor white
                                                    BackgroundColor black
                                                 }
                                            </style>""") + "\n"

    def append_string(self, *string_list):
        """Append *string_list to string"""
        self.string = "".join([self.string, *string_list])

    def create_state(self, state, parent=False):
        """Create state"""
        if parent:
            open_bracket_str = ' {'
        else:
            open_bracket_str = ''
        if state.alias:
            state_alias = state.alias
        else:
            state_alias = state.name.lower().replace(" ", "_").replace("-", "")
        self.append_string("'id: ", state.id, '\nstate "', state.name, '"', ' as ', state_alias,
                           ' <<', str(state.type), '>>', open_bracket_str, '\n')

    def create_transition(self, transition_list):
        """Create transition"""
        for transition in transition_list:
            if transition[0].alias:
                source_alias = transition[0].alias
            else:
                source_alias = transition[0].name.lower().replace(" ", "_").replace("-", "")

            if transition[1].alias:
                destination_alias = transition[1].alias
            else:
                destination_alias = transition[1].name.lower().replace(" ", "_").replace("-", "")

            self.append_string(str(source_alias), " --> ", str(destination_alias), " : ")
            conditions_str = ""
            last = len(transition[2]) - 1
            if not transition[2]:
                conditions_str += "No Condition Yet\n"
            else:
                for idx, trans in enumerate(transition[2]):
                    condition = trans.strip("{''}")
                    if idx < last:
                        conditions_str += condition + ' \\n '
                        idx += 1
                    elif idx == last:
                        conditions_str += condition + "\n"
            self.string += conditions_str


class SequenceDiagram:
    """Class for plantuml sequence diagram"""
    def __init__(self):
        """Init string"""
        # Allow plantuml option to put duration between 2 messages (not used yet)
        self.string = "!pragma teoz true\n"

    def append_string(self, *string_list):
        """Append *string_list to string"""
        self.string = "".join([self.string, *string_list])

    def create_sequence_message(self, message_list):
        """Create sequence message"""
        activate_list = []
        deactivate_list = []
        for idx, val in enumerate(message_list):
            for i in range(2):
                if val[i] not in activate_list:
                    activate_list.append(val[i])
                    self.append_string("activate ", val[i].replace(" ", "_").replace("-", ""), "\n")

            relationship_str = val[0].replace(" ", "_").replace("-", "") + ' -> ' \
                               + val[1].replace(" ", "_").replace("-", "")
            if val[3]:
                seq_number = str(idx + 1) + "- "
            else:
                seq_number = ""
            self.append_string(relationship_str, ' : ', seq_number + val[2], '\n')
            for i in range(2):
                if val[i] in activate_list and \
                        not any(val[i] in sub for sub in message_list[idx + 1:]):
                    deactivate_list.append(val[i])
                    self.append_string("deactivate ", val[i].replace(" ", "_").replace("-", ""),
                                       "\n")

    def create_participant(self, function):
        """Create participant"""
        # If the string is not formatted like this, plantuml raises error
        function_name = function.name.lower().replace(" ", "_").replace("-", "")
        self.append_string("participant ", function_name, ' <<', str(function.type), '>>', "\n")


class ObjDiagram:
    """Class for plantuml object/component diagram"""
    def __init__(self):
        """Init string"""
        self.string = ""

    def append_string(self, *string_list):
        """Append *string_list to string"""
        self.string = "".join([self.string, *string_list])

    def create_object(self, function, attribute_list):
        """Create plantuml object"""
        # If the string is not formatted like this, plantuml raises error
        operand_str = ''
        function_name = function.name.lower().replace(" ", "_").replace("-", "")
        self.append_string(
            "'id: ", str(function.id), '\nobject "', function.name, '" as ', function_name,
            ' <<', str(function.type), '>>')

        if function.operand:
            operand_str = str(function.operand) + ' : ' + str(function.input_role) + '\n'
        attribute_str = self.create_object_attributes(function, attribute_list)

        if len(attribute_str) > 1 or len(operand_str) > 1:
            self.append_string(" {\n", operand_str, attribute_str, "}\n")
        else:
            self.append_string("\n")

    def create_component_attribute(self, component, attribute_list):
        """Create component attribute"""
        attribute_str = self.create_object_attributes(component, attribute_list)
        if attribute_str:
            component_name = component.name.lower().replace(" ", "_").replace("-", "")
            self.append_string('note bottom of ', component_name, '\n', attribute_str, 'end note\n')

    def create_port(self, flow_list, flow_direction):
        """Create port i.e. circle"""
        for i in flow_list:
            end = ""
            if flow_direction == "in":
                end = '_i\n'
            elif flow_direction == "out":
                end = '_o\n'
            elif flow_direction == "None":
                end = '\n'
            self.append_string('circle ', i[0][1].replace(" ", "_").replace("-", ""), end)

    def create_component(self, component):
        """Create component"""
        # If the string is not formatted like this, plantuml raises error
        component_name = component.name.lower().replace(" ", "_").replace("-", "")
        self.append_string("'id: ", component.id, '\ncomponent "', component.name, '" ', 'as ',
                           component_name, ' <<', str(component.type), '>>{\n')

    def create_output_flow(self, output_flow_list):
        """Create output flow"""
        output_flow_str = ""
        for i in output_flow_list:
            name = i[0][1].replace(" ", "_").replace("-", "")
            middle_arrow = ''
            if i[0][0] is not None:
                middle_arrow = ' #--> '
            if i[0][0] is None:
                middle_arrow = ' --> '
            relationship_str = name + middle_arrow + name + '_o '
            if len(i[1]) > 1:
                self.string += self.create_multiple_arrow(relationship_str, output_flow_str, i)
            else:
                self.append_string(relationship_str, ' : ', i[1][0], '\n')

    def create_input_flow(self, input_flow_list):
        """Create input flow"""
        input_flow_str = ""
        for i in input_flow_list:
            relationship_str = "".join([i[0][1].replace(" ", "_").replace("-", ""), '_i', ' --> ',
                                        i[0][1].replace(" ", "_").replace("-", "")])
            if len(i[1]) > 1:
                self.string += self.create_multiple_arrow(relationship_str, input_flow_str, i)
            else:
                self.append_string(relationship_str, ' : ', i[1][0], '\n')

    def create_data_flow(self, data_flow_list):
        """Create data flow"""
        flow_str = ""
        for i in data_flow_list:
            relationship_str = "".join([i[0][0].replace(" ", "_").replace("-", ""), ' #--> ',
                                        i[0][1].replace(" ", "_").replace("-", "")])
            if len(i[1]) > 1:
                self.string += self.create_multiple_arrow(relationship_str, flow_str, i)
            else:
                self.append_string(relationship_str, ' : ', i[1][0], '\n')

    def create_interface(self, interface_list):
        """Create interfaces from interface_list"""
        for i in interface_list:
            relationship_str = ""
            if i[0] and i[1]:
                relationship_str = i[0].name.lower().replace(" ", "_").replace("-", "") + ' -- ' \
                                   + i[1].name.lower().replace(" ", "_").replace("-", "")
            elif not i[0] and i[1]:
                circle_name = i[1].name.lower().replace(" ", "_").replace("-", "") + '_o'
                relationship_str = 'circle ' + circle_name + '\n'
                relationship_str += i[1].name.lower().replace(" ", "_").replace("-", "") \
                                    + ' -- ' + circle_name
            elif i[0] and not i[1]:
                circle_name = i[0].name.lower().replace(" ", "_").replace("-", "") + '_o'
                relationship_str = 'circle ' + circle_name + '\n'
                relationship_str += circle_name + ' -- ' +\
                                    i[0].name.lower().replace(" ", "_").replace("-", "")

            self.append_string(relationship_str, ' : ',
                               i[2].name.lower().replace(" ", "_").replace("-", ""), '\n')

    @classmethod
    def create_object_attributes(cls, wanted_object, attribute_list):
        """Create object attributes"""
        attribute_str = ''
        if attribute_list:
            for attribute in attribute_list:
                for described_item in attribute.described_item_list:
                    if described_item[0] == wanted_object.id:
                        attribute_str += attribute.name + " = " + described_item[1] + "\n"
        return attribute_str

    @classmethod
    def create_multiple_arrow(cls, relationship_str, flow_str, flow_list):
        """Create multiples arrow, to split data names across for visualization improvements"""
        extended_flow_list = []
        new_prod_cons_flow_list = []
        producer_consumer_name = (flow_list[0][0], flow_list[0][1])
        flow_list = flow_list[1]
        flow_str += relationship_str + ' : ' + flow_list[0]
        count = 0
        for k, p in enumerate(flow_list):
            if k < len(flow_list) and k - 1 >= 0:
                count += len(p)
                if count < 350:
                    flow_str += '\\n' + flow_list[k]
                else:
                    extended_flow_list.append(p)
        flow_str += '\n'
        if len(extended_flow_list) > 0:
            rest = producer_consumer_name, extended_flow_list
            new_prod_cons_flow_list += rest
            return cls.create_multiple_arrow(relationship_str, flow_str, new_prod_cons_flow_list)
        return flow_str
