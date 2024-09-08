""" @defgroup handler
Jarvis handler module
"""
# Libraries


# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from jarvis.query import query_object, question_answer
from tools import Logger

# Global variables
HORIZONTAL_LIST_DISPLAY = 'horizontally'


def list_object(p_str_list, **kwargs):
    """
    Gets lists from object_str : i.e. Input/Output/Child/Data
    Args:
        p_str_list ([object_string]): list of object's name from cell
        **kwargs: all xml lists

    Returns:
        answer_list: [Input_list, Output_list, Child_list, Data_list]
    """
    answer_list = []
    # elem = [type_name, object_name]
    for elem in p_str_list:
        type_name = elem[0].replace('"', "")
        object_name = elem[1].replace('"', "")

        if HORIZONTAL_LIST_DISPLAY in object_name:
            is_list_transposed = True
            object_name = object_name[0: object_name.index(HORIZONTAL_LIST_DISPLAY)].strip()
        else:
            is_list_transposed = False

        wanted_object = query_object.query_object_by_name(object_name, **kwargs)
        if wanted_object is None:
            Logger.set_error(__name__,
                             f"Object '{object_name}' does not exist")
        else:
            object_type = query_object.query_object_type(wanted_object, **kwargs)
            wanted_list = switch_object_list(type_name, wanted_object, object_type, is_list_transposed, **kwargs)
            if wanted_list:
                answer_list.append(wanted_list)
            # Else do nothing

    return answer_list


def switch_object_list(type_list_str, wanted_object, object_type, is_list_transposed, **kwargs):
    """Switch depending on list's type and object's type """
    object_list = {}
    if object_type in (datamodel.BaseType.STATE,
                       datamodel.BaseType.FUNCTION,
                       datamodel.BaseType.FUNCTIONAL_ELEMENT):
        if object_type == datamodel.BaseType.STATE and type_list_str in ("input", "output"):
            report_no_list_available(wanted_object, object_type)
        elif object_type != datamodel.BaseType.STATE and type_list_str in ("function", "transition"):
            report_no_list_available(wanted_object, object_type)
        elif object_type != datamodel.BaseType.FUNCTIONAL_ELEMENT and type_list_str == "interface":
            report_no_list_available(wanted_object, object_type)
        else:
            switch_type_list = {
                "input": get_input_list,
                "output": get_output_list,
                "child": get_child_list,
                "function": get_state_function,
                "transition": get_state_transition,
                "interface": get_fun_elem_interface,
            }
            type_list = switch_type_list.get(type_list_str, None)
            if type_list:
                object_list = type_list(wanted_object, object_type, is_list_transposed, **kwargs)

                if not object_list:
                    Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
                # Else do nothing
            else:
                report_no_list_available(wanted_object, object_type)
    elif object_type == datamodel.BaseType.FUNCTIONAL_INTERFACE and type_list_str == "data":
        object_list = question_answer.get_fun_intf_data(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    else:
        report_no_list_available(wanted_object, object_type)

    return object_list


def get_input_list(wanted_object, object_type, is_list_transposed, **kwargs):
    """Case 'list input Function/Functional ELement' """
    input_dict = {}
    input_list = question_answer.get_input_or_output_fun_and_fun_elem(wanted_object, direction='input', **kwargs)

    if wanted_object.derived:
        for input_derived in question_answer.get_input_or_output_fun_and_fun_elem(wanted_object.derived,
                                                                                  direction='input',
                                                                                  **kwargs):
            input_list.append(input_derived)
    # Else do nothing

    if input_list:
        if is_list_transposed:
            input_dict = {'title': f"Input list for {wanted_object.name}:",
                          'data': input_list,
                          'columns': ["Data name", "Producer"],
                          'transpose': 'y'}
        else:
            input_dict = {'title': f"Input list for {wanted_object.name}:",
                          'data': input_list,
                          'columns': ["Data name", "Producer"]}

    return input_dict


def get_output_list(wanted_object, object_type, is_list_transposed, **kwargs):
    """Case 'list output Function/Functional ELement' """
    output_dict = {}
    output_list = question_answer.get_input_or_output_fun_and_fun_elem(wanted_object, direction='output', **kwargs)

    if wanted_object.derived:
        for output_derived in question_answer.get_input_or_output_fun_and_fun_elem(wanted_object.derived,
                                                                                   direction='output',
                                                                                   **kwargs):
            output_list.append(output_derived)
    # Else do nothing
    
    if output_list:
        if is_list_transposed:
            output_dict = {'title': f"Output list for {wanted_object.name}:",
                           'data': output_list,
                           'columns': ["Data name", "Consumer"],
                           'transpose': 'y'}
        else:
            output_dict = {'title': f"Output list for {wanted_object.name}:",
                           'data': output_list,
                           'columns': ["Data name", "Consumer"]}
    return output_dict


def get_child_list(wanted_object, object_type, is_list_transposed, **kwargs):
    """Case 'list child Function/State/Functional ELement' """
    child_dict = {}
    child_list = None
    if object_type == "function":
        child_list = question_answer.get_child_name_list(wanted_object, kwargs[XML_DICT_KEY_1_FUNCTION_LIST])
        if wanted_object.derived:
            child_list += [e for e in question_answer.get_child_name_list(wanted_object.derived,
                                                                          kwargs[XML_DICT_KEY_1_FUNCTION_LIST])]
    elif object_type == "state":
        child_list = question_answer.get_child_name_list(wanted_object, kwargs[XML_DICT_KEY_6_STATE_LIST])

    elif object_type == "Functional element":
        child_list = question_answer.get_child_name_list(wanted_object, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])

        child_list.extend(question_answer.get_fun_elem_function_state_allocation(wanted_object,
                                                                                 kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                                                 kwargs[XML_DICT_KEY_6_STATE_LIST]))
        if wanted_object.derived:
            child_list += [e for e in question_answer.get_child_name_list(wanted_object.derived,
                                                                          kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])]
            child_list += [e for e in question_answer.get_fun_elem_function_state_allocation(
                wanted_object.derived, kwargs[XML_DICT_KEY_1_FUNCTION_LIST], kwargs[XML_DICT_KEY_6_STATE_LIST])]

    if child_list:
        if is_list_transposed:
            child_dict = {'title': f"Child list for {wanted_object.name}:",
                          'data': list(tuple(sorted(child_list))),
                          'columns': ["Object's name", "Relationship's type"],
                          'transpose': 'y'}
        else:
            child_dict = {'title': f"Child list for {wanted_object.name}:",
                          'data': list(tuple(sorted(child_list))),
                          'columns': ["Object's name", "Relationship's type"]}

    return child_dict


def get_state_function(wanted_object, object_type, is_list_transposed, **kwargs):
    """Case 'list function State' """
    function_dict = {}
    function_list = []
    for allocated_fun in wanted_object.allocated_function_list:
        for fun in kwargs[XML_DICT_KEY_1_FUNCTION_LIST]:
            if fun.id == allocated_fun:
                function_list.append((fun.name, "Function allocation"))

    if function_list:
        if is_list_transposed:
            function_dict = {'title': f"Function list for {wanted_object.name}:",
                             'data': list(tuple(sorted(function_list))),
                             'columns': ["Object's name", "Relationship's type"],
                             'transpose': 'y'}
        else:
            function_dict = {'title': f"Function list for {wanted_object.name}:",
                             'data': list(tuple(sorted(function_list))),
                             'columns': ["Object's name", "Relationship's type"]}

    return function_dict


def get_state_transition(wanted_object, object_type, is_list_transposed, **kwargs):
    """Case 'list transition State' """
    transition_dict = {}
    transition_list = []
    for transition in kwargs[XML_DICT_KEY_7_TRANSITION_LIST]:
        if wanted_object.id == transition.source:
            for state in kwargs[XML_DICT_KEY_6_STATE_LIST]:
                if transition.destination == state.id:
                    transition_list.append({
                        'Transition name': transition.name,
                        'Source state': wanted_object.name,
                        'Destination state': state.name,
                        'Condition(s)': transition.condition_list
                    })
        elif wanted_object.id == transition.destination:
            for state in kwargs[XML_DICT_KEY_6_STATE_LIST]:
                if transition.source == state.id:
                    transition_list.append({
                        'Transition name': transition.name,
                        'Source state': state.name,
                        'Destination state': wanted_object.name,
                        'Condition(s)': transition.condition_list
                    })

    if transition_list:
        if is_list_transposed:
            transition_dict = {'title': f"Transition list for {wanted_object.name}:",
                               'data': transition_list,
                               'columns': ["Transition name", "Source state", "Destination state", "Condition(s)"],
                               'transpose': 'y'
                               }
        else:
            transition_dict = {'title': f"Transition list for {wanted_object.name}:",
                               'data': transition_list,
                               'columns': ["Transition name", "Source state", "Destination state", "Condition(s)"]
                               }

    return transition_dict


def get_fun_elem_interface(wanted_object, object_type, is_list_transposed, **kwargs):
    """Case for 'list interface Functional element'"""
    interface_dict = {}
    id_list = wanted_object.exposed_interface_list
    main_fun_elem_child_list, _ = query_object.query_object_children_recursively(wanted_object)
    if wanted_object.derived:
        id_list = id_list.union(wanted_object.derived.exposed_interface_list)
        main_fun_elem_child_list = main_fun_elem_child_list.union(
            query_object.query_object_children_recursively(wanted_object.derived)[0])

    fun_inter_list = question_answer.get_objects_from_id_list(id_list,
                                                              kwargs[XML_DICT_KEY_3_FUN_INTF_LIST])

    if not fun_inter_list:
        Logger.set_warning(__name__, f"Not any exposed interface for {format(wanted_object.name)}")
    else:
        exposing_fun_elem = set()
        for interface in fun_inter_list:
            for fun_elem in kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]:
                if fun_elem not in main_fun_elem_child_list and \
                        interface.id in fun_elem.exposed_interface_list and \
                        query_object.query_object_is_not_family(fun_elem, wanted_object):
                    exposing_fun_elem.add((interface, fun_elem))

        interface_list = set()
        for k in exposing_fun_elem:
            child_list, _ = query_object.query_object_children_recursively(k[1])
            child_list.remove(k[1])
            if child_list:
                check = True
                for p in exposing_fun_elem:
                    if p[0] == k[0] and any(a == p[1] for a in child_list):
                        check = False
                        break
                if check:
                    interface_list.add((k[0].name, k[1].name))
            else:
                interface_list.add((k[0].name, k[1].name))

        if interface_list:
            if is_list_transposed:
                interface_dict = {'title': f"Interface list for {wanted_object.name}:",
                                  'data': list(tuple(sorted(interface_list))),
                                  'columns': ["Interface ", "Last connected functional element"],
                                  'transpose': 'y'}
            else:
                interface_dict = {'title': f"Interface list for {wanted_object.name}:",
                                  'data': list(tuple(sorted(interface_list))),
                                  'columns': ["Interface ", "Last connected functional element"]}

    return interface_dict


def report_no_list_available(wanted_object, object_type):
    """Case when there is incompatible list's type with object's type """
    Logger.set_error(__name__, f"No list available for object '{wanted_object.name}' "
                               f"of type '{object_type.capitalize()}', possible lists are:\n"
                               f"- List child [Function/State/Functional element]\n"
                               f"- List input/output [Function/Functional element]\n"
                               f"- List function/transition [State]\n"
                               f"- List interface [Functional element]\n"
                               f"- List data [Functional interface]")
