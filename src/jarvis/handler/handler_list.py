""" @defgroup handler
Jarvis handler module
"""
# Libraries


# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
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
    # List child [Function/State/Functional element]
    if type_list_str == "child" and object_type in (datamodel.BaseType.STATE,
                       datamodel.BaseType.FUNCTION,
                       datamodel.BaseType.FUNCTIONAL_ELEMENT):
        object_list = get_child_list(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    # List input [Function/Functional element]
    elif type_list_str == "input" and object_type in (datamodel.BaseType.FUNCTION,
                                                      datamodel.BaseType.FUNCTIONAL_ELEMENT):
        object_list = get_input_list(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    # List output [Function/Functional element]
    elif type_list_str == "output" and object_type in (datamodel.BaseType.FUNCTION,
                                                      datamodel.BaseType.FUNCTIONAL_ELEMENT):
        object_list = get_output_list(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    # List function [Functional element / State]
    elif type_list_str == "function" and object_type in (datamodel.BaseType.STATE,
                                                         datamodel.BaseType.FUNCTIONAL_ELEMENT):
        object_list = get_allocated_function_table(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    # List transition [State]
    elif type_list_str == "transition" and object_type == datamodel.BaseType.STATE:
        object_list = get_state_transition(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    # List interface [Functional element]
    elif type_list_str == "interface" and object_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
        object_list = get_fun_elem_interface(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    # List activity [Physical element]
    elif type_list_str == "activity" and object_type == datamodel.BaseType.PHYSICAL_ELEMENT:
        object_list = get_phy_elem_allocated_activity_table(wanted_object, object_type, is_list_transposed, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    # List data [Functional interface]
    elif type_list_str == "data" and object_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
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


def get_allocated_function_table(wanted_object, object_type, is_list_transposed, **kwargs):
    """Case 'list function State' """
    function_dict = {}
    function_list = []

    allocated_function_list = query_object.query_object_allocated_object_list(wanted_object,
                                                                              kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                                              **kwargs)

    if not allocated_function_list:
        Logger.set_warning(__name__, f"No function allocated to {wanted_object.__class__.__name__} "
                                     f"{wanted_object.name}")
    else:
        for allocated_function in allocated_function_list:
            allocated_activity_name_list = '-'
            for allocated_activity_id in allocated_function.allocated_activity_list:
                for activity in kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]:
                    if activity.id == allocated_activity_id:
                        allocated_activity_name_list = allocated_activity_name_list + activity.name + '\n'
                    # Else do nothing

            if len(allocated_activity_name_list) > 1:
                allocated_activity_name_list = allocated_activity_name_list[1:-1]
            # Else do nothing

            function_list.append([allocated_function.name, allocated_activity_name_list])

        if function_list:
            if is_list_transposed:
                function_dict = {'title': f"Function list for {wanted_object.name}:",
                                 'data': list(tuple(sorted(function_list))),
                                 'columns': ["Name", "Allocated activity(ies)"],
                                 'transpose': 'y'}
            else:
                function_dict = {'title': f"Function list for {wanted_object.name}:",
                                 'data': list(tuple(sorted(function_list))),
                                 'columns': ["Name", "Allocated activity(ies)"]}
        # Else do nothing

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


def get_phy_elem_allocated_activity_table(wanted_object, _, is_list_transposed, **kwargs):
    activity_dict = {}
    activity_list = []

    allocated_activity_list = query_object.query_object_allocated_object_list(wanted_object,
                                                                              kwargs[XML_DICT_KEY_10_ACTIVITY_LIST],
                                                                              **kwargs)
    if wanted_object.derived:
        derived_allocated_activity_list = \
            query_object.query_object_allocated_object_list(wanted_object.derived,
                                                            kwargs[XML_DICT_KEY_10_ACTIVITY_LIST],
                                                            **kwargs)
        if derived_allocated_activity_list and allocated_activity_list:
            allocated_activity_list = allocated_activity_list.union(derived_allocated_activity_list)
        # Else do nothing
    # Else do nothing

    if not allocated_activity_list:
        Logger.set_warning(__name__, f"No activity allocated to physical element {wanted_object.name}")
    else:
        for allocated_activity in allocated_activity_list:
            allocated_goal_name_list = '-'
            for allocated_goal_id in allocated_activity.allocated_goal_list:
                for goal in kwargs[XML_DICT_KEY_9_GOAL_LIST]:
                    if goal.id == allocated_goal_id:
                        allocated_goal_name_list = allocated_goal_name_list + goal.name + '\n'
                    # Else do nothing

            if len(allocated_goal_name_list) > 1:
                allocated_goal_name_list = allocated_goal_name_list[1:-1]
            # Else do nothing

            activity_list.append([allocated_activity.name, allocated_goal_name_list])

        if activity_list:
            if is_list_transposed:
                activity_dict = {'title': f"Activity list for {wanted_object.name}:",
                             'data': list(tuple(sorted(activity_list))),
                             'columns': ['Name', 'Allocated goal(s)'],
                             'transpose': 'y'}
            else:
                activity_dict = {'title': f"Activity list for {wanted_object.name}:",
                             'data':list(tuple(sorted(activity_list))),
                             'columns': ['Name', 'Allocated goal(s)']}
        # Else do nothing

    return activity_dict

def report_no_list_available(wanted_object, object_type):
    """Case when there is incompatible list's type with object's type """
    Logger.set_error(__name__, f"No list available for object '{wanted_object.name}' "
                               f"of type '{str(object_type).capitalize()}', possible lists are:\n"
                               f"- List child [Function/State/Functional element]\n"
                               f"- List input/output [Function/Functional element]\n"
                               f"- List function [Functional element]\n"
                               f"- List function/transition [State]\n"
                               f"- List interface [Functional element]\n"
                               f"- List data [Functional interface]\n"
                               f"- List activity [Physical element]")
