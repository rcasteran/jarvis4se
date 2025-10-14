"""@defgroup plantuml_adapter
Plantuml adapter module
"""
# Libraries
import inspect


# Modules
import datamodel


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
            state_ref = normalize_element_reference(state.alias)
        else:
            state_ref = normalize_element_reference(state.name)

        if isinstance(state.type, datamodel.BaseType):
            state_type_str = str(state.type).capitalize().replace("_", " ")
        elif datamodel.ExitStateLabel in state.type.name.lower():
            state_type_str = 'EXIT'
        elif datamodel.EntryStateLabel in state.type.name.lower():
            state_type_str = 'ENTRY'
        else:
            state_type_str = state.type.name
        self.append_string("'id: ", state.id, '\nstate "', state.name, '"', ' as ', state_ref,
                           ' <<', state_type_str, '>>', open_bracket_str, '\n')

    def create_transition(self, transition_list):
        """Update the PlantUml text for a list of transitions
        @param[in] transition_list list of transitions
        @return None
        """
        for transition in transition_list:
            if transition[0].alias:
                source_ref = normalize_element_reference(transition[0].alias)
            else:
                source_ref = normalize_element_reference(transition[0].name)

            if transition[1].alias:
                destination_ref = normalize_element_reference(transition[1].alias)
            else:
                destination_ref = normalize_element_reference(transition[1].name)

            self.append_string(source_ref, " --> ", destination_ref, " : ")
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
                    self.append_string("activate ", normalize_element_reference(val[i]), "\n")

            relationship_str = normalize_element_reference(val[0]) + ' -> ' + normalize_element_reference(val[1])
            if val[3]:
                seq_number = str(idx + 1) + "- "
            else:
                seq_number = ""
            self.append_string(relationship_str, ' : ', seq_number + val[2], '\n')
            for i in range(2):
                if val[i] in activate_list and \
                        not any(val[i] in sub for sub in message_list[idx + 1:]):
                    deactivate_list.append(val[i])
                    self.append_string("deactivate ", normalize_element_reference(val[i]), "\n")

    def create_participant(self, function):
        """Update the PlantUml text for a function
        @param[in] function function
        @return None
        """
        function_ref = normalize_element_reference(function.name)
        if isinstance(function.type, datamodel.BaseType):
            function_type_str = str(function.type).capitalize().replace("_", " ")
        else:
            function_type_str = function.type.name

        if function_type_str.lower() == 'actor':
            self.append_string('actor "', function.name, '" as ', function_ref, "\n")
        else:
            self.append_string('participant "', function.name, '" as ', function_ref, ' <<',
                               function_type_str, '>>', "\n")


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
        function_ref = normalize_element_reference(function.name)
        if isinstance(function.type, datamodel.BaseType):
            function_type_str = str(function.type).capitalize().replace("_", " ")
        else:
            function_type_str = function.type.name

        if function_type_str.lower() == 'actor' and len(function.child_list) == 0 and not function.operand:
            self.append_string(
                "'id: ", str(function.id), '\nactor "', function.name, '" as ', function_ref)
        else:
            self.append_string(
                "'id: ", str(function.id), '\nobject "', function.name, '" as ', function_ref,
                ' <<', function_type_str, '>>')

        if hasattr(function, "operand"):
            if function.operand:
                operand_str = str(function.operand) + ' : ' + str(function.input_role) + '\n'

        attribute_str = self.create_object_attributes(function, attribute_list)

        if len(attribute_str) > 1 or len(operand_str) > 1:
            if function_type_str.lower() == 'actor':
                # TODO
                self.append_string("\n")
            else:
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
            component_name = normalize_element_reference(component.name)
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
            self.append_string('circle ', normalize_element_reference(i[0][1]), end)

    def create_component(self, component):
        """Update the PlantUml text for a component
        @param[in] component component
        @return None
        """

        # If the string is not formatted like this, plantuml raises error
        component_ref = normalize_element_reference(component.name)
        if isinstance(component.type, datamodel.BaseType):
            component_type_str = str(component.type).capitalize().replace("_", " ")
        else:
            component_type_str = component.type.name
        self.append_string("'id: ", component.id, '\ncomponent "', component.name, '" ', 'as ',
                           component_ref, ' <<', component_type_str, '>>{\n')

    def create_output_flow(self, output_flow_list):
        """Update the PlantUml text for output flows list
        @param[in] output_flow_list output flows list
        @return None
        """
        output_flow_str = ""
        for i in output_flow_list:
            if i[0][0] is not None:
                middle_arrow = ' #--> '
            else:
                middle_arrow = ' --> '

            is_digit = False
            last_underscore_position = i[0][1].rfind('_')
            if 0 < last_underscore_position < len(i[0][1])-1:
                is_digit = i[0][1][last_underscore_position+1:].isdigit()
            # Else do nothing

            if is_digit:
                name = i[0][1]
                relationship_str = "".join([normalize_element_reference(name),
                                            middle_arrow,
                                            normalize_element_reference(name[0:name.index('_')]),
                                            '_o '])
            else:
                name = normalize_element_reference(i[0][1])
                relationship_str = "".join([name, middle_arrow, name, '_o '])
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
            is_digit = False
            last_underscore_position = i[0][1].rfind('_')
            if 0 < last_underscore_position < len(i[0][1])-1:
                is_digit = i[0][1][last_underscore_position+1:].isdigit()
            # Else do nothing

            if is_digit:
                name = i[0][1]
                relationship_str = "".join([normalize_element_reference(name[0:name.index('_')]),
                                            '_i',
                                            ' --> ',
                                            normalize_element_reference(name)])
            else:
                name = normalize_element_reference(i[0][1])
                relationship_str = "".join([name, '_i', ' --> ', name])
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
            relationship_str = "".join([normalize_element_reference(i[0][0]), ' #--> ',
                                        normalize_element_reference(i[0][1])])
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
                relationship_str = normalize_element_reference(i[0].name) + ' -- ' \
                                   + normalize_element_reference(i[1].name)
            elif not i[0] and i[1]:
                circle_name = normalize_element_reference(i[1].name) + '_o'
                relationship_str = 'circle ' + circle_name + '\n'
                relationship_str += normalize_element_reference(i[1].name) + ' -- ' + circle_name
            elif i[0] and not i[1]:
                circle_name = normalize_element_reference(i[0].name) + '_o'
                relationship_str = 'circle ' + circle_name + '\n'
                relationship_str += circle_name + ' -- ' + normalize_element_reference(i[0].name)

            self.append_string(relationship_str, ' : ', i[2].name, '\n')

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


def normalize_element_reference(p_element_name):
    return p_element_name.lower()\
        .replace(" ", "_")\
        .replace("-", "")\
        .replace("'s", "")\
        .replace("(", "_")\
        .replace(")", "_")\
        .replace(",", "_")\
        .replace("'", "")\
        .replace("<", "_")\
        .replace(">", "_")\
        .replace("&", "")\
        .replace("/", "")
