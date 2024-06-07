"""@defgroup simulation
Jarvis simulation module
"""
# Libraries
import re

# Modules
import open_modelica_adapter
from jarvis.query import question_answer
from tools import Logger
from jarvis.diagram import util as diagram_util


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

    xml_fun_elem_name_list = question_answer.get_objects_names(kwargs['xml_fun_elem_list'])
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
    xml_fun_elem_list = kwargs['xml_fun_elem_list']
    xml_state_list = kwargs['xml_state_list']
    xml_transition_list = kwargs['xml_transition_list']
    new_fun_elem_list = set()
    open_modelica_text = None

    main_fun_elem = question_answer.check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
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
