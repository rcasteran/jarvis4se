#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import sys
import os
import pathlib
import uuid
import subprocess

from plantuml import PlantUML

sys.path.append("../datamodel")
import datamodel  # noqa


# Class to generate PLantuml string/.txt and .svg/url diagram
class MakePlantUml:

    # Open(or create) output file in "plantuml_adapter" folder
    def __init__(self, plantuml_file):
        if len(plantuml_file) > 0:
            self.file = plantuml_file
        else:
            self.file = "Output.txt"
        self.output_file = open(self.file, "w")

    @staticmethod
    def create_object(function, attribute_list):
        # If the string is not formatted like this, plantuml raises error
        function_name = function.name.lower().replace(" ", "_").replace("-", "")
        object_str = "'id: " + function.id + '\nobject "' + function.name + '"' + ' as ' \
                     + function_name + ' <<' + str(function.type) + '>>'

        attribute_str = MakePlantUml.create_object_attributes(function, attribute_list)

        if len(attribute_str) > 1:
            object_str += " {\n" + attribute_str + "}\n"
        else:
            object_str += "\n"
        return object_str

    @staticmethod
    def create_object_with_operand(function, attribute_list):
        operand_str = ''
        # If the string is not formatted like this, plantuml raises error
        function_name = function.name.lower().replace(" ", "_").replace("-", "")
        object_str = "'id: " + function.id + '\nobject "' + function.name + '"' + ' as ' \
                     + function_name + ' <<' + str(function.type) + '>>'

        if function.operand:
            operand_str = str(function.operand) + ' : ' + str(function.input_role) + '\n'

        attribute_str = MakePlantUml.create_object_attributes(function, attribute_list)

        if len(attribute_str) > 1:
            object_str += " {\n" + operand_str + attribute_str + "}\n"
        elif len(attribute_str) == 0 and function.operand:
            object_str += " {\n" + operand_str + "}\n"
        else:
            object_str += "\n"
        return object_str

    @staticmethod
    def create_object_attributes(function, attribute_list):
        attribute_str = ''
        if attribute_list:
            for attribute in attribute_list:
                for described_item in attribute.described_item_list:
                    if described_item[0] == function.id:
                        attribute_str += attribute.name + " = " + described_item[1] + "\n"
        return attribute_str

    @staticmethod
    def create_component(component):
        # If the string is not formatted like this, plantuml raises error
        component_name = component.name.lower().replace(" ", "_").replace("-", "")
        component_str = "'id: " + component.id + '\ncomponent "' + component.name + '" ' + 'as ' + \
                        component_name + ' <<' + str(component.type) + '>>{\n'
        return component_str

    @staticmethod
    def close_component():
        close_bracket_str = '}\n'
        return close_bracket_str

    @staticmethod
    def create_component_attribute(component, attribute_list):
        attribute_str = MakePlantUml.create_object_attributes(component, attribute_list)
        if attribute_str:
            component_name = component.name.lower().replace(" ", "_").replace("-", "")
            note_str = 'note bottom of ' + component_name + '\n' + attribute_str + 'end note\n'
            return note_str
        else:
            return ''

    @staticmethod
    def create_output_flow(output_flow_list):
        output_flow_str = ""
        for i in output_flow_list:
            relationship_str = ''
            if i[0][0] is not None:
                relationship_str = i[0][1].replace(" ", "_").replace("-", "") + ' #--> '
                relationship_str += i[0][1].replace(" ", "_").replace("-", "") + '_o '
            if i[0][0] is None:
                relationship_str = i[0][1].replace(" ", "_").replace("-", "") + ' --> '
                relationship_str += i[0][1].replace(" ", "_").replace("-", "") + '_o '
            if len(i[1]) > 1:
                output_flow_str = MakePlantUml.create_multiple_arrow(relationship_str,
                                                                     output_flow_str, i)
            else:
                output_flow_str += relationship_str + ' : ' + i[1][0] + '\n'

        return output_flow_str

    @staticmethod
    def create_input_flow(input_flow_list):
        input_flow_str = ""
        for i in input_flow_list:
            relationship_str = i[0][1].replace(" ", "_").replace("-", "") + '_i' + ' --> '
            relationship_str += i[0][1].replace(" ", "_").replace("-", "")
            if len(i[1]) > 1:
                input_flow_str = MakePlantUml.create_multiple_arrow(relationship_str,
                                                                    input_flow_str, i)
            else:
                input_flow_str += relationship_str + ' : ' + i[1][0] + '\n'
        return input_flow_str

    @staticmethod
    def create_port(flow_list, flow_direction):
        port_str = ""
        for i in flow_list:
            if flow_direction == "in":
                port_str += 'circle ' + i[0][1].replace(" ", "_").replace("-", "") + '_i\n'
            elif flow_direction == "out":
                port_str += 'circle ' + i[0][1].replace(" ", "_").replace("-", "") + '_o\n'
            elif flow_direction == "None":
                port_str += 'circle ' + i[0][1].replace(" ", "_").replace("-", "") + '\n'
        return port_str

    @staticmethod
    def create_data_flow(data_flow_list):
        flow_str = ""
        for i in data_flow_list:
            relationship_str = i[0][0].replace(" ", "_").replace("-", "") + ' #--> ' \
                               + i[0][1].replace(" ", "_").replace("-", "")
            if len(i[1]) > 1:
                flow_str = MakePlantUml.create_multiple_arrow(relationship_str, flow_str, i)
            else:
                flow_str += relationship_str + ' : ' + i[1][0] + '\n'
        return flow_str

    @staticmethod
    def create_interface(interface_list):
        flow_str = ""
        for i in interface_list:
            relationship_str = ""
            if i[0] and i[1]:
                relationship_str = i[0].name.lower().replace(" ", "_").replace("-", "") + ' -- ' \
                                   + i[1].name.lower().replace(" ", "_").replace("-", "")
            elif not i[0] and i[1]:
                circle_name = i[1].name.lower().replace(" ", "_").replace("-", "") + '_o'
                relationship_str += 'circle ' + circle_name + '\n'
                relationship_str += i[1].name.lower().replace(" ", "_").replace("-", "") \
                                    + ' -- ' + circle_name

            elif i[0] and not i[1]:
                circle_name = i[1].name.lower().replace(" ", "_").replace("-", "") + '_o'
                relationship_str += 'circle ' + circle_name + '\n'
                relationship_str += circle_name + ' -- ' +\
                                    i[1].name.lower().replace(" ", "_").replace("-", "")

            flow_str += relationship_str + ' : ' + \
                        i[2].name.lower().replace(" ", "_").replace("-", "") + '\n'
        return flow_str

    @staticmethod
    def create_multiple_arrow(relationship_str, flow_str, flow_list):
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
            a = producer_consumer_name, extended_flow_list
            new_prod_cons_flow_list += a
            return MakePlantUml.create_multiple_arrow(relationship_str, flow_str,
                                                      new_prod_cons_flow_list)
        return flow_str

    @staticmethod
    def get_url_from_local(string):
        """Generate unique .svg from string using  plantuml default server or plantuml.jar client,
        depending on the diagram's size (limit around 15000 char.)
        """
        current_file_path = None
        out = None
        if len(string) < 15000:
            full_string = "@startuml\nskin rose\nskinparam NoteBackgroundColor PapayaWhip\n" \
                          + string + "@enduml"
            # Quickest by HTTP request to plantuml server (only for small diagrams)
            server = PlantUML(url='http://www.plantuml.com/plantuml/svg/',
                              basic_auth={},
                              form_auth={}, http_opts={}, request_opts={})
            out = server.get_url(full_string)
        else:
            full_string = "@startuml\n" + string + "@enduml"
            # Generate and set unique identifier of length 10 integers
            identi = uuid.uuid4()
            identi = str(identi.int)[:10]
            current_file_path = str(pathlib.Path('./Diagrams/Diagram' + identi + '.txt'))
            plantuml_jar_path = str(pathlib.Path('./plantuml.jar'))
            with open(current_file_path, 'w+') as my_file:
                my_file.write(full_string)
                my_file.close()
            subprocess.check_output(
                ['java', '-DPLANTUML_LIMIT_SIZE=20000', '-jar', plantuml_jar_path,
                 '%s' % current_file_path, '-tsvg'])
            out = str(current_file_path).replace(".txt", ".svg")
            if os.path.isfile(out):
                pass
        if out:
            if current_file_path:
                os.remove(current_file_path)
            return out
        else:
            print("Diagram not generated")
            return

    def write(self, lines):
        self.output_file.writelines(lines)

    @staticmethod
    def create_sequence_message(message_list):
        sequence_message_str = ""
        activate_list = []
        deactivate_list = []
        for idx, val in enumerate(message_list):
            if val[0] not in activate_list:
                activate_list.append(val[0])
                sequence_message_str += "activate " + val[0].replace(" ", "_").replace("-", "") \
                                        + "\n"
            if val[1] not in activate_list:
                activate_list.append(val[1])
                sequence_message_str += "activate " + val[1].replace(" ", "_").replace("-", "") \
                                        + "\n"
            relationship_str = val[0].replace(" ", "_").replace("-", "") + ' -> ' \
                               + val[1].replace(" ", "_").replace("-", "")
            if val[3]:
                seq_number = str(idx + 1) + "- "
            else:
                seq_number = ""
            sequence_message_str += relationship_str + ' : ' + seq_number + val[2] + '\n'
            if val[0] in activate_list and not any(val[0] in sub for sub in message_list[idx + 1:]):
                deactivate_list.append(val[0])
                sequence_message_str += "deactivate " + val[0].replace(" ", "_").replace("-", "") \
                                        + "\n"

            if val[1] in activate_list and not any(val[1] in sub for sub in message_list[idx + 1:]):
                deactivate_list.append(val[1])
                sequence_message_str += "deactivate " + val[1].replace(" ", "_").replace("-", "") \
                                        + "\n"

        return sequence_message_str

    @staticmethod
    def create_participant(function):
        # If the string is not formatted like this, plantuml raises error
        function_name = function.name.lower().replace(" ", "_").replace("-", "")
        participant_str = "participant " + function_name
        # TODO: In order to be more concise, need to change inputs lists for other
        #  methods by function and not function.name
        # if function.alias:
        #     participant_str += " as " + function.alias
        participant_str += ' <<' + str(function.type) + '>>' + "\n"
        return participant_str

    @staticmethod
    def create_state(state, parent=False):
        if parent:
            open_bracket_str = ' {'
        else:
            open_bracket_str = ''
        if state.alias:
            state_alias = state.alias
        else:
            state_alias = state.name.lower().replace(" ", "_").replace("-", "")
        state_str = "'id: " + state.id + '\nstate "' + state.name + '"' + ' as ' + state_alias \
                    + ' <<' + str(state.type) + '>>' + open_bracket_str + '\n'
        return state_str

    @staticmethod
    def create_transition(transition_list):
        transition_str = ""
        for transition in transition_list:
            if transition[0].alias:
                source_alias = transition[0].alias
            else:
                source_alias = transition[0].name.lower().replace(" ", "_").replace("-", "")

            if transition[1].alias:
                destination_alias = transition[1].alias
            else:
                destination_alias = transition[1].name.lower().replace(" ", "_").replace("-", "")

            transition_str += str(source_alias) + " --> " + str(destination_alias) + " : "
            conditions_str = ""
            last = len(transition[2]) - 1
            if not transition[2]:
                conditions_str += "No Condition Yet\n"
            else:
                for idx, c in enumerate(transition[2]):
                    condition = c.strip("{''}")
                    if idx < last:
                        conditions_str += condition + ' \\n '
                        idx += 1
                    elif idx == last:
                        conditions_str += condition + "\n"
            transition_str += conditions_str

        return transition_str
