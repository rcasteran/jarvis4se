#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module to write plantuml text and write plantuml text within file"""
# Libraries
import os
import inspect
import pathlib
import uuid
import subprocess

from plantuml import PlantUML


class PlantUmlGen:
    """Class to generate PLantuml string/.txt and .svg/url diagram"""
    # Open(or create) output file in root folder
    def __init__(self):
        """Init server, uuid and path"""
        # Quickest by HTTP request to plantuml server (only for small diagrams)
        self.server = PlantUML(url='http://www.plantuml.com/plantuml/svg/',
                               basic_auth={},
                               form_auth={}, http_opts={}, request_opts={})
        # Generate and set unique identifier of length 10 integers
        identi = uuid.uuid4()
        self.identi = str(identi.int)[:10]
        self.current_file_path = str(pathlib.Path('./Diagrams/Diagram' + self.identi + '.txt'))
        self.plantuml_jar_path = str(pathlib.Path('./plantuml.jar'))

    def get_diagram_path_or_url(self, string, from_diagram_cell=False):
        """Generate unique .svg from string using  plantuml default server or plantuml.jar client,
        depending on the diagram's size (limit around 15000 char.)
        """
        if not from_diagram_cell:
            full_string = "@startuml\nskin rose\nskinparam NoteBackgroundColor PapayaWhip\n" \
                          + string + "@enduml"
        else:
            full_string = string

        if len(string) < 15000:
            out = self.server.get_url(full_string)
        else:
            with open(self.current_file_path, 'w+', encoding="utf8") as my_file:
                my_file.write(full_string)
                my_file.close()
            subprocess.check_output(
                ['java', '-DPLANTUML_LIMIT_SIZE=20000', '-jar', self.plantuml_jar_path,
                 f'{self.current_file_path}', '-tsvg'])
            out = str(self.current_file_path).replace(".txt", ".svg")
            if not os.path.isfile(out):
                print("Diagram not generated")
                return None

            if os.path.isfile(out):
                os.remove(self.current_file_path)

        return out


class StateDiagram:
    """Class for plantuml State diagram"""
    def __init__(self):
        """Init string and PLantumlGen()"""
        self.generator = PlantUmlGen()
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
        """Init string and PLantumlGen()"""
        self.generator = PlantUmlGen()
        # Allow plantuml option to put duration between 2 messages
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
        """Init string and PLantumlGen()"""
        self.generator = PlantUmlGen()
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
