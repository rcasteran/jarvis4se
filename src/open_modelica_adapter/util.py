"""@defgroup open_modelica_adapter
Open modelica adapter module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_ATTRIBUTE_LIST, XML_DICT_KEY_11_VIEW_LIST, \
    XML_DICT_KEY_12_TYPE_LIST, XML_DICT_KEY_13_FUN_CONS_LIST, XML_DICT_KEY_14_FUN_PROD_LIST
from jarvis.query import query_object, question_answer
from tools import Logger


class StateModel:
    """@ingroup open_modelica_adapter
    @anchor StateModel
    Class to encode open modelica text for state model
    """

    def __init__(self, p_obj_name):
        """
        @var string_begin
        Open modelica text for declaration beginning

        @var string_global
        Open modelica text for global declaration

        @var string_equation
        Open modelica text for equation

        @var string_algorithm
        Open modelica text for algorithm

        @var string_end
        Open modelica text for declaration end

        @var string_state_name_list
        Open modelica text for state name list

        @var string_state_initial
        Open modelica text for initial state
        """

        # Initialize OpenModelica text
        self.string_begin = f'model {p_obj_name}\n'
        self.string_global = f'Boolean clock;\n'
        self.string_equation = 'equation\nclock = sample(0,1);\n'
        self.string_algorithm = 'algorithm\nwhen clock then\n'
        self.string_end = 'end when;\nend system;\n'

        self.string_state_name_list = 'type State = enumeration();\n'
        self.string_state_initial = ''

        # Initialize global data list
        self.global_data_list = []

    def create_data(self, p_data, p_initial_value, **kwargs):
        data_attribute = query_object.query_object_by_name(datamodel.DesignAttributeLabel,
                                                           **{XML_DICT_KEY_10_ATTRIBUTE_LIST: kwargs[XML_DICT_KEY_10_ATTRIBUTE_LIST]})
        if p_data not in self.global_data_list:
            if data_attribute:
                for described_item in data_attribute.described_item_list:
                    if described_item[0] == p_data.id:
                        self.string_global = self.string_global + described_item[1] + ' ' \
                                             + p_data.name \
                                             + f'(start={p_initial_value});\n'
                        break
                    # Else do nothing
            else:
                self.string_global = self.string_global + p_data.name \
                                     + f'(start={p_initial_value});\n'

            self.global_data_list.append(p_data)
        # Else do nothing

    def create_state(self, p_state, p_is_initial=False, **kwargs):
        xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
        xml_producer_function_list = kwargs[XML_DICT_KEY_14_FUN_PROD_LIST]

        if p_is_initial:
            self.string_state_initial = f'State state(start = State.{p_state.name});\n'
        # Else do nothing

        # Update state name list text
        if self.string_state_name_list[-4] == '(':
            self.string_state_name_list = self.string_state_name_list[:-3] + p_state.name + ');\n'
        else:
            self.string_state_name_list = self.string_state_name_list[:-3] + ', ' + p_state.name + ');\n'

        # Update algorithm
        self.string_algorithm = self.string_algorithm + f'if state == state.{p_state.name} then\n'
        state_function_list = sort_state_function_list(p_state.allocated_function_list, **kwargs)
        for state_function in state_function_list:
            design_attribute = query_object.query_object_by_name(datamodel.DesignAttributeLabel,
                                                                 **{XML_DICT_KEY_10_ATTRIBUTE_LIST: kwargs[
                                                                    XML_DICT_KEY_10_ATTRIBUTE_LIST]})
            if design_attribute:
                for described_item in design_attribute.described_item_list:
                    if described_item[0] == state_function.id:
                        self.string_algorithm = self.string_algorithm + described_item[1] + ';\n'
                        break
                    # Else do nothing
            else:
                self.string_algorithm = self.string_algorithm + ';\n'

            for xml_producer_function in xml_producer_function_list:
                if xml_producer_function[1].id == state_function.id:
                    initial_value_attribute = query_object.query_object_by_name(
                        datamodel.InitialValueAttributeLabel,
                        **{XML_DICT_KEY_10_ATTRIBUTE_LIST: kwargs[
                            XML_DICT_KEY_10_ATTRIBUTE_LIST]})
                    is_initial_value = False
                    if initial_value_attribute:
                        for described_item in initial_value_attribute.described_item_list:
                            if described_item[0] == xml_producer_function[0].id:
                                is_initial_value = True
                                self.create_data(xml_producer_function[0], described_item[1], **kwargs)
                                break
                            # Else do nothing

                        if not is_initial_value:
                            Logger.set_error(__name__,
                                             f'No attribute "initial value" found for the data '
                                             f'"{xml_producer_function[0].name}"')
                    else:
                        Logger.set_error(__name__,
                                         f'No attribute "initial value" found for the data '
                                         f'"{xml_producer_function[0].name}"')
                # Else do nothing

        self.string_algorithm = self.string_algorithm + f'end if;\n'

    def create_transition(self, p_transition, **kwargs):
        xml_state_list = kwargs[XML_DICT_KEY_6_STATE_LIST]
        for xml_state in xml_state_list:
            if xml_state.id == p_transition.destination:
                data_attribute = query_object.query_object_by_name(datamodel.DesignAttributeLabel,
                                                                   **{XML_DICT_KEY_10_ATTRIBUTE_LIST: kwargs[
                                                                       XML_DICT_KEY_10_ATTRIBUTE_LIST]})
                if data_attribute:
                    for described_item in data_attribute.described_item_list:
                        if described_item[0] == p_transition.id:
                            self.string_algorithm = self.string_algorithm + 'if ' + described_item[1] + ' then\n' \
                                        + f'state := state.{xml_state.name};\n' \
                                        + 'end if;\n'
                            break
                        # Else do nothing
                else:
                    self.string_algorithm = self.string_algorithm + 'if then\n' \
                                            + f'state := state.{xml_state.name};\n' \
                                            + 'end if;\n'

                break
            # Else do nothing

    def get_model(self):
        return self.string_begin \
            + self.string_global \
            + self.string_state_name_list \
            + self.string_state_initial \
            + self.string_equation \
            + self.string_algorithm \
            + self.string_end


def sort_state_function_list(p_function_id_list, **kwargs):
    xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
    xml_producer_function_list = kwargs[XML_DICT_KEY_14_FUN_PROD_LIST]
    state_function_list = []

    for function_id in p_function_id_list:
        for xml_function in xml_function_list:
            if xml_function.id == function_id:
                state_function_list.append(xml_function)
            # Else do nothing

    if len(state_function_list) > 1:
        state_producer_function_list = []
        for state_function in state_function_list:
            for xml_producer_function in xml_producer_function_list:
                if xml_producer_function[1].id == state_function.id:
                    state_producer_function_list.append([xml_producer_function[0], xml_producer_function[1]])
                # Else do nothing

        sorted_state_producer_function_dict = dict()
        last_index = 0
        for state_producer_function in state_producer_function_list:
            if state_producer_function not in sorted_state_producer_function_dict.values():
                last_index = last_index + 1
                current_index = last_index
                sorted_state_producer_function_dict[current_index] = state_producer_function
            else:
                current_index = list(sorted_state_producer_function_dict.keys())[
                    list(sorted_state_producer_function_dict.values()).index(state_producer_function)]

            for predecessor in state_producer_function[0].predecessor_list:
                for predecessor_producer_function in state_producer_function_list:
                    if predecessor_producer_function[0] == predecessor:
                        if [predecessor_producer_function[0], predecessor_producer_function[1]] not in \
                                sorted_state_producer_function_dict.values():
                            current_index = current_index + 1
                            if last_index > current_index:
                                for i in range(0, last_index - current_index):
                                    sorted_state_producer_function_dict[last_index - i + 1] = \
                                        sorted_state_producer_function_dict[last_index - i]
                                last_index = last_index + 1
                            else:
                                last_index = current_index
                            sorted_state_producer_function_dict[current_index] = [state_producer_function[0],
                                                                                  state_producer_function[1]]
                            sorted_state_producer_function_dict[current_index - 1] = [predecessor_producer_function[0],
                                                                                      predecessor_producer_function[1]]
                        # Else do nothing
                    # Else do nothing

        # Reconstruct ordered state function list
        sorted_state_producer_function_dict = sorted(sorted_state_producer_function_dict.items())
        state_function_list = []
        for key, value in sorted_state_producer_function_dict:
            state_function_list.append(value[1])
    # Else do nothing

    return state_function_list
