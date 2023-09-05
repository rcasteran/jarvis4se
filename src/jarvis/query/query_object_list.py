# Libraries


# Modules
from . import question_answer
from tools import Logger


def get_object_list(p_str_list, **kwargs):
    """
    Gets lists from object_str : i.e. Input/Output/Child/Data
    Args:
        p_str_list ([object_string]): list of object's name from cell
        **kwargs: all xml lists

    Returns:
        answer_list: [Input_list, Output_list, Child_list, Data_list]
    """
    answer_list = []
    for elem in p_str_list:
        wanted_object = question_answer.check_get_object(elem[1], **kwargs)
        if wanted_object is None:
            Logger.set_error(__name__,
                             f"Object '{elem[1]}' does not exist")
        else:
            object_type = question_answer.get_object_type(wanted_object)
            wanted_list = switch_object_list(elem[0], wanted_object, object_type, **kwargs)
            if wanted_list:
                answer_list.append(wanted_list)
            # Else do nothing

    return answer_list


def switch_object_list(type_list_str, wanted_object, object_type, **kwargs):
    """Switch depending on list's type and object's type """
    object_list = {}
    if object_type in ("state", "function", "Functional element"):
        if object_type == "state" and type_list_str in ("input", "output"):
            report_no_list_available(wanted_object, object_type, **kwargs)
        elif object_type != "state" and type_list_str in ("function", "transition"):
            report_no_list_available(wanted_object, object_type, **kwargs)
        elif object_type != "Functional element" and type_list_str == "interface":
            report_no_list_available(wanted_object, object_type, **kwargs)
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
                object_list = type_list(wanted_object, object_type, **kwargs)

                if not object_list:
                    Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
                # Else do nothing
            else:
                report_no_list_available(wanted_object, object_type, **kwargs)
    elif object_type == "Functional interface" and type_list_str == "data":
        object_list = get_fun_intf_data(wanted_object, object_type, **kwargs)

        if not object_list:
            Logger.set_info(__name__, f"Nothing to display for {type_list_str} list of '{wanted_object.name}'")
        # Else do nothing
    else:
        report_no_list_available(wanted_object, object_type, **kwargs)

    return object_list


def get_input_list(wanted_object, _, **kwargs):
    """Case 'list input Function/Functional ELement' """
    input_dict = {}
    input_list = question_answer.get_input_or_output_fun_and_fun_elem(wanted_object, direction='input', **kwargs)

    if wanted_object.derived:
        input_list.append(*question_answer.get_input_or_output_fun_and_fun_elem(wanted_object.derived,
                                                                                direction='input', **kwargs))
    if input_list:
        input_dict = {'title': f"Input list for {wanted_object.name}:",
                      'data': input_list,
                      'columns': ["Data name", "Producer"]}
    return input_dict


def get_output_list(wanted_object, _, **kwargs):
    """Case 'list output Function/Functional ELement' """
    output_dict = {}
    output_list = question_answer.get_input_or_output_fun_and_fun_elem(wanted_object, direction='output', **kwargs)

    if wanted_object.derived:
        output_list.append(*question_answer.get_input_or_output_fun_and_fun_elem(wanted_object.derived,
                                                                                 direction='output', **kwargs))
    if output_list:
        output_dict = {'title': f"Output list for {wanted_object.name}:",
                       'data': output_list,
                       'columns': ["Data name", "Consumer"]}

    return output_dict


def get_child_list(wanted_object, object_type, **kwargs):
    """Case 'list child Function/State/Functional ELement' """
    child_dict = {}
    child_list = None
    if object_type == "function":
        child_list = question_answer.get_child_name_list(wanted_object, kwargs['xml_function_list'])
        if wanted_object.derived:
            child_list += [e for e in question_answer.get_child_name_list(wanted_object.derived,
                                                                          kwargs['xml_function_list'])]
    elif object_type == "state":
        child_list = question_answer.get_child_name_list(wanted_object, kwargs['xml_state_list'])

    elif object_type == "Functional element":
        child_list = question_answer.get_child_name_list(wanted_object, kwargs['xml_fun_elem_list'])

        child_list.extend(question_answer.get_fun_elem_function_state_allocation(wanted_object,
                                                                                 kwargs['xml_function_list'],
                                                                                 kwargs['xml_state_list']))
        if wanted_object.derived:
            child_list += [e for e in question_answer.get_child_name_list(wanted_object.derived,
                                                                          kwargs['xml_fun_elem_list'])]
            child_list += [e for e in question_answer.get_fun_elem_function_state_allocation(
                wanted_object.derived, kwargs['xml_function_list'], kwargs['xml_state_list'])]

    if child_list:
        child_dict = {'title': f"Child list for {wanted_object.name}:",
                      'data': list(tuple(sorted(child_list))),
                      'columns': ["Object's name", "Relationship's type"]}

    return child_dict


def get_state_function(wanted_object, _, **kwargs):
    """Case 'list function State' """
    function_dict = {}
    function_list = []
    for allocated_fun in wanted_object.allocated_function_list:
        for fun in kwargs['xml_function_list']:
            if fun.id == allocated_fun:
                function_list.append((fun.name, "Function allocation"))

    if function_list:
        function_dict = {'title': f"Function list for {wanted_object.name}:",
                         'data': list(tuple(sorted(function_list))),
                         'columns': ["Object's name", "Relationship's type"]}

    return function_dict


def get_state_transition(wanted_object, _, **kwargs):
    """Case 'list transition State' """
    transition_dict = {}
    transition_list = []
    for transition in kwargs['xml_transition_list']:
        if wanted_object.id == transition.source:
            for state in kwargs['xml_state_list']:
                if transition.destination == state.id:
                    transition_list.append({
                        'Transition name': transition.name,
                        'Source state': wanted_object.name,
                        'Destination state': state.name,
                        'Condition(s)': transition.condition_list
                    })
        elif wanted_object.id == transition.destination:
            for state in kwargs['xml_state_list']:
                if transition.source == state.id:
                    transition_list.append({
                        'Transition name': transition.name,
                        'Source state': state.name,
                        'Destination state': wanted_object.name,
                        'Condition(s)': transition.condition_list
                    })

    if transition_list:
        transition_dict = {'title': f"Transition list for {wanted_object.name}:",
                           'data': transition_list}

    return transition_dict


def get_fun_elem_interface(wanted_object, _, **kwargs):
    """Case for 'list interface Functional element'"""
    interface_dict = {}
    id_list = wanted_object.exposed_interface_list
    main_fun_elem_child_list, _ = question_answer.get_children(wanted_object)
    if wanted_object.derived:
        id_list = id_list.union(wanted_object.derived.exposed_interface_list)
        main_fun_elem_child_list = main_fun_elem_child_list.union(
            question_answer.get_children(wanted_object.derived)[0])

    fun_inter_list = question_answer.get_objects_from_id_list(id_list,
                                                              kwargs['xml_fun_inter_list'])

    if not fun_inter_list:
        Logger.set_warning(__name__, f"Not any exposed interface for {format(wanted_object.name)}")
    else:
        exposing_fun_elem = set()
        for interface in fun_inter_list:
            for fun_elem in kwargs['xml_fun_elem_list']:
                if fun_elem not in main_fun_elem_child_list and \
                        interface.id in fun_elem.exposed_interface_list and \
                        question_answer.check_not_family(fun_elem, wanted_object):
                    exposing_fun_elem.add((interface, fun_elem))

        interface_list = set()
        for k in exposing_fun_elem:
            child_list, _ = question_answer.get_children(k[1])
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
            interface_dict = {'title': f"Interface list for {wanted_object.name}:",
                              'data': list(tuple(sorted(interface_list))),
                              'columns': ["Interface ", "Last connected functional element"]}

    return interface_dict


def get_fun_intf_data(wanted_object, _, **kwargs):
    """Case for 'list data Functional Interface' """
    data_dict = {}
    data_list = []
    fun_elem_exposing = question_answer.get_allocation_object(wanted_object, kwargs['xml_fun_elem_list'])
    if wanted_object.derived:
        derived_fun_elem_exposing = question_answer.get_allocation_object(wanted_object.derived,
                                                                          kwargs['xml_fun_elem_list'])
        if derived_fun_elem_exposing and fun_elem_exposing:
            fun_elem_exposing = fun_elem_exposing.union(derived_fun_elem_exposing)

    if not fun_elem_exposing:
        Logger.set_warning(__name__, f"Not any functional element exposing {wanted_object.name}")
    else:
        last_fun_elem_exposing = [question_answer.check_latest(j, fun_elem_exposing) for j in fun_elem_exposing
                                  if question_answer.check_latest(j, fun_elem_exposing)]

        for allocated_id in wanted_object.allocated_data_list:
            for data in kwargs['xml_data_list']:
                if allocated_id == data.id:
                    data_list.append(question_answer.get_latest_obj_interface(data, last_fun_elem_exposing, **kwargs))

        if wanted_object.derived:
            for allocated_id in wanted_object.derived.allocated_data_list:
                for data in kwargs['xml_data_list']:
                    if allocated_id == data.id:
                        data_list.append(
                            question_answer.get_latest_obj_interface(data, last_fun_elem_exposing, **kwargs))

        if data_list:
            data_dict = {'title': f"Data list for {wanted_object.name}:",
                         'data': data_list}

    return data_dict


def report_no_list_available(wanted_object, object_type, _):
    """Case when there is incompatible list's type with object's type """
    Logger.set_error(__name__, f"No list available for object '{wanted_object.name}' "
                               f"of type '{object_type.capitalize()}', possible lists are:\n"
                               f"- List child [Function/State/Functional element]\n"
                               f"- List input/output [Function/Functional element]\n"
                               f"- List function/transition [State]\n"
                               f"- List interface [Functional element]\n"
                               f"- List data [Functional interface]")
