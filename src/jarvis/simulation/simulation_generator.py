"""@defgroup simulation
Jarvis simulation module
"""
# Libraries
import re

# Modules
import open_modelica_adapter
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from jarvis.diagram import util as diagram_util
from jarvis.query import query_object, question_answer
from tools import Logger


def filter_simulate_command(p_simulation_type_str, p_simulation_object_str, **kwargs):
    kwargs['simulation_type_str'] = p_simulation_type_str
    kwargs['simulation_object_str'] = p_simulation_object_str

    switch = {
        "function": case_function_simulation,
        "state": case_state_simulation
    }

    get_diagram = switch.get(kwargs['simulation_type_str'], case_no_simulation)
    open_modelica_text = get_diagram(**kwargs)

    return open_modelica_text


def case_function_simulation(**kwargs):
    # TODO
    return None


def case_state_simulation(**kwargs):
    open_modelica_text = None

    xml_fun_elem_name_list = query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
    if kwargs['simulation_object_str'] in xml_fun_elem_name_list:
        open_modelica_text = simulate_fun_elem_state_machine(kwargs['simulation_object_str'], **kwargs)
    else:
        Logger.set_error(__name__,
                         f"Jarvis does not know the functional element {kwargs['simulation_object_str']}")

    return open_modelica_text


def case_no_simulation(**kwargs):
    Logger.set_warning(__name__,
                       f"Jarvis does not understand the command {kwargs['simulation_type_str']}")
    return None


def simulate_fun_elem_state_machine(fun_elem_str, **kwargs):
    xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
    xml_state_list = kwargs[XML_DICT_KEY_6_STATE_LIST]
    xml_transition_list = kwargs[XML_DICT_KEY_7_TRANSITION_LIST]
    new_fun_elem_list = set()
    open_modelica_text = None

    main_fun_elem = query_object.query_object_by_name(fun_elem_str, **{XML_DICT_KEY_2_FUN_ELEM_LIST: xml_fun_elem_list})
    if main_fun_elem:
        if main_fun_elem.allocated_state_list:
            new_fun_elem_list.add(main_fun_elem)

            new_state_list = {s for s in xml_state_list if s.id in main_fun_elem.allocated_state_list}

            new_transition_list = diagram_util.get_transition_list(new_state_list, xml_transition_list)

            open_modelica_text = open_modelica_adapter.get_state_machine_model(fun_elem_str,
                                                                               new_state_list,
                                                                               new_transition_list,
                                                                               **kwargs)

            Logger.set_info(__name__,
                            f"Simulation for {fun_elem_str} generated")
        else:
            Logger.set_error(__name__,
                             f"No state allocated to {main_fun_elem.name} (no simulation)")
    else:
        Logger.set_error(__name__,
                         f"Element {fun_elem_str} is not a functional element (no simulation)")

    return open_modelica_text
