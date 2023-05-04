"""@defgroup plantuml_adapter
Plantuml adapter module
"""
# Libraries
import os
import re
import inspect
import pathlib
import subprocess

from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from plantuml import PlantUML

# Modules
import datamodel
from tools import Logger


class PlantUmlPicoServer:
    """@ingroup plantuml_adapter
    @anchor PlantUmlPicoServer
    Class that looks for .jar file in root, check version and handle local PlantUml PicoWeb
    Server (https://plantuml.com/en/picoweb)

    If . jar, get it, check if PicoWeb is running, if not start new process else default url
    to online PlantUml server
    """
    def __init__(self):
        """
        @var plantuml_jar_path
        Filepath to the PlantUml jar

        @var url
        URL for the local PlantUml PicoWeb Server

        @var version_cmd
        JAVA command to retrieve the PlantUml jar file version
        """

        self.plantuml_jar_path = None

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
        """Return first jar filepath with 'plantuml' in filename

        @return jar filepath
        """

        end_message = ", large diagrams will not be displayed.\n" \
                      "See: " \
                      "https://github.com/rcasteran/jarvis4se/blob/main/docs/installation.md"

        list_dir = os.listdir('.')
        if not any('.jar' in f for f in list_dir):
            Logger.set_warning(__name__,
                              f"Not any .jar found for plantuml in root{end_message}")
            return None

        jar_list = [f.string for f in [re.search("plantuml.*jar", i) for i in list_dir] if f]
        if not jar_list:
            Logger.set_warning(__name__,
                              f"Not any .jar found with 'plantuml' in its name{end_message}")
            return None

        # Return first filename with plantuml in it
        return jar_list.pop(0)

    def check_version(self):
        """ Get .jar version and check with latest release

        @return None
        """

        jar_version = subprocess.run(
            self.version_cmd, capture_output=True, encoding="utf-8").stdout[17:26].strip()
        github_url = "https://github.com/plantuml/plantuml/releases/latest"

        try:
            with urlopen(f"{github_url}") as rep:
                release_ver = str(rep.geturl())[51:]

            if int(release_ver[0]) > int(jar_version[0]) or \
                    int(release_ver[2:6]) > int(jar_version[2:6]) or \
                    int(release_ver[7:len(release_ver)]) > int(jar_version[7:len(jar_version)]):
                Logger.set_info(__name__,
                           f"plantUml.jar is not up-to-date, see latest release {github_url}")
        except:
            Logger.set_info(__name__,
                           "Not able to check plantuml.jar version.")


class PlantUmlGen(PlantUmlPicoServer):
    """@ingroup plantuml_adapter
    @anchor PlantUmlGen
    Class to encode PlantUml text and get server url as .svg
    """
    def __init__(self):
        """
        @var server
        PlantUml server
        """

        # Init PicoWeb server from PlantUMLPicoServer
        # If .jar found or default online PlantUml, send it to PlantUml for encoding and HTTP handling
        super().__init__()
        # PlantUml has encoding and handling errors
        self.server = PlantUML(url=self.url,
                               basic_auth={},
                               form_auth={}, http_opts={}, request_opts={})

    def get_diagram_url(self, string, from_diagram_cell=False):
        """ Generate .svg from PlantUml text using PlantUml default server or PlantUml .jar PicoWeb
        @param[in] string PlantUml text
        @param[in] from_diagram_cell indicates if PlantUml text is coming from a notebook diagram cell
        (TRUE) or not (FALSE)
        @return diagram url
        """
        if not from_diagram_cell:
            full_string = "@startuml\nskin rose\nskinparam NoteBackgroundColor PapayaWhip\n" \
                          + string + "@enduml"
        else:
            full_string = string

        if len(string) > 15000 and self.plantuml_jar_path is None:
            Logger.set_warning(__name__,
                              f"Diagram is too large to be display with PlantUml Online Server, "
                              f"please consider download .jar at https://plantuml.com/fr/download")
            return None

        return self.server.get_url(full_string)


class StateDiagram:
    """@ingroup plantuml_adapter
    @anchor StateDiagram
    Class to encode PlantUml text for state diagram
    """

    def __init__(self):
        """
        @var string
        PlantUml text
        """

        # Initialize PlantUml text
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
        """Append *string_list to PlantUml text
        @param[in] *string_list string list
        @return None
        """
        self.string = "".join([self.string, *string_list])

    def create_state(self, state, parent=False):
        """Update the PlantUml text for a state
        @param[in] state state element
        @param[in] parent indicates if the state is a parent (TRUE) or not (FALSE)
        @return None
        """
        if parent:
            open_bracket_str = ' {'
        else:
            open_bracket_str = ''
        if state.alias:
            state_alias = state.alias
        else:
            state_alias = state.name.lower().replace(" ", "_").replace("-", "")

        if isinstance(state.type, datamodel.BaseType):
            state_type_str = str(state.type).capitalize().replace("_", " ")
        elif 'EXIT' in state.type.name:
            state_type_str = 'EXIT'
        elif 'ENTRY' in state.type.name:
            state_type_str = 'ENTRY'
        else:
            state_type_str = state.type.name
        self.append_string("'id: ", state.id, '\nstate "', state.name, '"', ' as ', state_alias,
                           ' <<', state_type_str, '>>', open_bracket_str, '\n')

    def create_transition(self, transition_list):
        """Update the PlantUml text for a list of transitions
        @param[in] transition_list list of transitions
        @return None
        """
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
    """@ingroup plantuml_adapter
    @anchor SequenceDiagram
    Class to encode PlantUml text for sequence diagram
    """

    def __init__(self):
        """
        @var string
        PlantUml text
        """

        # Allow plantuml option to put duration between 2 messages (not used yet)
        self.string = "!pragma teoz true\n"

    def append_string(self, *string_list):
        """Append *string_list to PlantUml text
        @param[in] *string_list string list
        @return None
        """
        self.string = "".join([self.string, *string_list])

    def create_sequence_message(self, message_list):
        """Update the PlantUml text for a list of message
        @param[in] message_list message list
        @return None
        """
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
        """Update the PlantUml text for a function
        @param[in] function function
        @return None
        """
        # If the string is not formatted like this, plantuml raises error
        function_name = function.name.lower().replace(" ", "_").replace("-", "")
        if isinstance(function.type, datamodel.BaseType):
            function_type_str = str(function.type).capitalize().replace("_", " ")
        else:
            function_type_str = function.type.name
        self.append_string("participant ", function_name, ' <<', function_type_str, '>>', "\n")


class ObjDiagram:
    """@ingroup plantuml_adapter
    @anchor ObjDiagram
    Class to encode PlantUml text for object diagram
    """

    def __init__(self):
        """
        @var string
        PlantUml text
        """

        self.string = ""

    def append_string(self, *string_list):
        """Append *string_list to PlantUml text
        @param[in] *string_list string list
        @return None
        """
        self.string = "".join([self.string, *string_list])

    def create_object(self, function, attribute_list):
        """Update the PlantUml text for a function
        @param[in] function function
        @param[in] attribute_list function attribute list
        @return None
        """

        # If the string is not formatted like this, plantuml raises error
        operand_str = ''
        function_name = function.name.lower().replace(" ", "_").replace("-", "")
        if isinstance(function.type, datamodel.BaseType):
            function_type_str = str(function.type).capitalize().replace("_", " ")
        else:
            function_type_str = function.type.name
        self.append_string(
            "'id: ", str(function.id), '\nobject "', function.name, '" as ', function_name,
            ' <<', function_type_str, '>>')

        if function.operand:
            operand_str = str(function.operand) + ' : ' + str(function.input_role) + '\n'
        attribute_str = self.create_object_attributes(function, attribute_list)

        if len(attribute_str) > 1 or len(operand_str) > 1:
            self.append_string(" {\n", operand_str, attribute_str, "}\n")
        else:
            self.append_string("\n")

    def create_component_attribute(self, component, attribute_list):
        """Update the PlantUml text for a component attribute list
        @param[in] component component
        @param[in] attribute_list component attribute list
        @return None
        """
        attribute_str = self.create_object_attributes(component, attribute_list)
        if attribute_str:
            component_name = component.name.lower().replace(" ", "_").replace("-", "")
            self.append_string('note bottom of ', component_name, '\n', attribute_str, 'end note\n')

    def create_port(self, flow_list, flow_direction):
        """Update the PlantUml text for a port (circle)
        @param[in] flow_list flow list
        @param[in] flow_direction flow direction
        @return None
        """
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
        """Update the PlantUml text for a component
        @param[in] component component
        @return None
        """

        # If the string is not formatted like this, plantuml raises error
        component_name = component.name.lower().replace(" ", "_").replace("-", "")
        if isinstance(component.type, datamodel.BaseType):
            component_type_str = str(component.type).capitalize().replace("_", " ")
        else:
            component_type_str = component.type.name
        self.append_string("'id: ", component.id, '\ncomponent "', component.name, '" ', 'as ',
                           component_name, ' <<', component_type_str, '>>{\n')

    def create_output_flow(self, output_flow_list):
        """Update the PlantUml text for output flows list
        @param[in] output_flow_list output flows list
        @return None
        """
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
        """Update the PlantUml text for input flows list
        @param[in] input_flow_list input flows list
        @return None
        """
        input_flow_str = ""
        for i in input_flow_list:
            relationship_str = "".join([i[0][1].replace(" ", "_").replace("-", ""), '_i', ' --> ',
                                        i[0][1].replace(" ", "_").replace("-", "")])
            if len(i[1]) > 1:
                self.string += self.create_multiple_arrow(relationship_str, input_flow_str, i)
            else:
                self.append_string(relationship_str, ' : ', i[1][0], '\n')

    def create_data_flow(self, data_flow_list):
        """Update the PlantUml text for data flows list
        @param[in] data_flow_list data flows list
        @return None
        """
        flow_str = ""
        for i in data_flow_list:
            relationship_str = "".join([i[0][0].replace(" ", "_").replace("-", ""), ' #--> ',
                                        i[0][1].replace(" ", "_").replace("-", "")])
            if len(i[1]) > 1:
                self.string += self.create_multiple_arrow(relationship_str, flow_str, i)
            else:
                self.append_string(relationship_str, ' : ', i[1][0], '\n')

    def create_interface(self, interface_list):
        """Update the PlantUml text for interface list
        @param[in] interface_list interface list
        @return None
        """
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
        """Update the PlantUml text for object attribute list
        @param[in] wanted_object object
        @param[in] attribute_list object attribute list
        @return None
        """
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
