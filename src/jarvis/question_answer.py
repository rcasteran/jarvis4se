#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import re
import pandas as pd
# Modules
import datamodel


questions = [
    (r"What is ([^\.\n]*) ", lambda matched_str, **kwargs: matched_what(matched_str, **kwargs)),

    (r"Is (.*) allocated ", lambda matched_str, **kwargs: matched_allocated(matched_str, **kwargs)),
]


def find_question(string, **kwargs):
    """Entry point from jarvis.py"""
    out = lookup_table(string, questions, **kwargs)
    return out


def lookup_table(strings, questions_table, **kwargs):
    """Method to match regex and corresponding method from [questions]"""
    answer_list = []
    for regex, method in questions_table:
        for i in strings:
            result = re.findall(regex, i, re.MULTILINE)
            if result:
                answer = method(result, **kwargs)
                if answer:
                    answer_list.append(answer)
    return answer_list


def matched_what(question_str, **kwargs):
    """Get the 'what' declaration """
    object_str = question_str[0].strip()
    wanted_object = check_get_object(object_str, **kwargs)

    if wanted_object:
        object_info = get_object_info(wanted_object, **kwargs)
        if object_info:
            return object_info


def matched_allocated(object_str, **kwargs):
    """From object_str, get object then check if allocated and returns allocation's list"""
    object_info = ""
    object_str = object_str[0]
    xml_function_name_list = get_objects_names(kwargs['xml_function_list'])
    xml_state_name_list = get_objects_names(kwargs['xml_state_list'])
    whole_objects_name_list = [*xml_function_name_list, *xml_state_name_list]
    if not any(s == object_str for s in whole_objects_name_list):
        print(f"{object_str} is not a function nor a state")
    else:
        result_function = any(s == object_str for s in xml_function_name_list)
        resul_state = any(s == object_str for s in xml_state_name_list)
        result = [result_function, False, resul_state,  False, False]
        wanted_object = match_object(object_str, result, **kwargs)
        if wanted_object:
            allocation_list = get_allocation_object(wanted_object, kwargs['xml_fun_elem_list'])
            if allocation_list:
                object_info += f'"{wanted_object.name}" is allocated to ' \
                               + ", ".join([elem.name for elem in allocation_list])
                return object_info

    return


def get_objects_name_lists(xml_str_lists, **kwargs):
    """Returns lists of objects with their names depending on kwargs"""
    whole_objects_name_list = [[] for _ in range(11)]
    for i in range(11):
        if kwargs.get(xml_str_lists[i], False):
            whole_objects_name_list[i] = get_objects_names(kwargs[xml_str_lists[i]])

    return whole_objects_name_list


# TODO: Use this method within xxxxxxx_orchestrator.py
def check_get_object(object_str, **kwargs):
    """
    Returns the desired object from object's string
    Args:
        object_str ([object_string]): list of object's name from cell
        **kwargs: xml lists

    Returns:
        wanted_object : Function/State/Data/Fun_Elem/Transition/Fun_Inter
    """
    xml_str_lists = ['xml_function_list', 'xml_data_list', 'xml_state_list', 'xml_fun_elem_list',
                     'xml_transition_list', 'xml_fun_inter_list', 'xml_phy_elem_list',
                     'xml_phy_inter_list', 'xml_attribute_list', 'xml_view_list', 'xml_type_list']
    whole_objects_name_list = get_objects_name_lists(xml_str_lists, **kwargs)
    if not any(object_str in s for s in whole_objects_name_list):
        return None
    else:
        result = [False] * 11
        for i in range(11):
            result[i] = any(a == object_str for a in whole_objects_name_list[i])

        wanted_object = match_object(object_str, result, xml_str_lists=xml_str_lists, **kwargs)
        return wanted_object


def match_object(object_str, result, xml_str_lists=None, **kwargs):
    """Returns wanted_object from object_str and result matched from name lists"""
    # Because match_object() called within match_allocated() TBC/TBT if match_allocated()
    # still needed
    if not xml_str_lists:
        xml_str_lists = ['xml_function_list', 'xml_data_list', 'xml_state_list',
                         'xml_fun_elem_list', 'xml_transition_list', 'xml_fun_inter_list',
                         'xml_phy_elem_list', 'xml_phy_inter_list', 'xml_attribute_list',
                         'xml_view_list', 'xml_type_list']
    for i in range(11):
        if result[i]:
            for obj in kwargs[xml_str_lists[i]]:
                if object_str == obj.name:
                    return obj
                try:
                    if object_str == obj.alias:
                        return obj
                except AttributeError:
                    # To avoid error when there is no alias for the object
                    pass
    return None


def get_object_info(wanted_object, **kwargs):
    """From wanted_object and all lists, returns a dict with info"""
    object_info = {'Name': str(wanted_object.name),
                   'Object Class': str(type(wanted_object).__name__),
                   'Type': str(wanted_object.type), 'Id': str(wanted_object.id)}

    try:
        # Only Data() does not have these attributes and Transition() does not have parent
        if any(wanted_object.alias):
            object_info['Alias'] = str(wanted_object.alias)
        if wanted_object.parent is not None:
            object_info['Parent'] = str(wanted_object.parent.name)
    except AttributeError:
        # To avoid error when there is no such attribute for the object
        pass
    if object_info['Object Class'] == 'Function':
        get_function_info(wanted_object, object_info, **kwargs)
    elif object_info['Object Class'] == 'FunctionalElement':
        get_fun_elem_info(wanted_object, object_info, **kwargs)
    elif object_info['Object Class'] == 'State':
        if any(wanted_object.child_list):
            object_info['Child List'] = get_child_name_list(wanted_object, kwargs['xml_state_list'])
    elif object_info['Object Class'] == 'Transition':
        get_transition_info(wanted_object, kwargs['xml_state_list'], object_info)
    elif object_info['Object Class'] == 'Data':
        get_data_info(wanted_object, object_info, **kwargs)

    if object_info:
        return object_info

    return


def get_function_info(wanted_object, object_info, **kwargs):
    """Get Function info"""
    if any(wanted_object.child_list):
        object_info['Child List'] = get_child_name_list(wanted_object, kwargs['xml_function_list'])
    if wanted_object.input_role is not None:
        object_info['Input Role'] = str(wanted_object.input_role)
    if wanted_object.operand is not None:
        object_info['Operand'] = str(wanted_object.operand)
    if any(wanted_object.port_list):
        object_info['Port List'] = str(wanted_object.port_list)

    object_info['Consumption List'] = \
        get_consumes_produces_info(wanted_object, kwargs['xml_consumer_function_list'])
    object_info['Production List'] = \
        get_consumes_produces_info(wanted_object, kwargs['xml_producer_function_list'])
    return object_info


def get_consumes_produces_info(wanted_object, relationship_list):
    """Get consumes/produces info"""
    object_relationship = set()
    for elem in relationship_list:
        if elem[1].id == wanted_object.id:
            object_relationship.add(elem[0])
        if elem[0] == wanted_object.name:
            object_relationship.add(elem[1].name)
    if object_relationship:
        return object_relationship


def get_child_name_list(parent_object, object_list):
    """Get child's name list"""
    child_list = set()
    for child in object_list:
        if child in parent_object.child_list:
            child_list.add((child.name, "Child"))
    return list(child_list)


def get_allocated_object_name_list(wanted_object, object_list):
    """From Functional Element object and list (State/Function) get the allocated objects"""
    allocation_list = set()
    for allocated_object in object_list:
        if any(s == allocated_object.id for s in wanted_object.allocated_state_list):
            allocation_list.add(allocated_object.name)
        if any(s == allocated_object.id for s in wanted_object.allocated_function_list):
            allocation_list.add(allocated_object.name)
    return allocation_list


def get_transition_info(wanted_object, state_list, object_info):
    """Get transition's info"""
    for state in state_list:
        if state.id == wanted_object.source:
            object_info['Source'] = str(state.name)
        if state.id == wanted_object.destination:
            object_info['Destination'] = str(state.name)
    if wanted_object.condition_list:
        object_info['Condition List'] = wanted_object.condition_list
    return object_info


def get_fun_elem_info(wanted_object, object_info, **kwargs):
    """Get functional element info, i.e. child_list, allocated Function/State"""
    if any(wanted_object.child_list):
        object_info['Child List'] = get_child_name_list(wanted_object, kwargs['xml_fun_elem_list'])
    if any(wanted_object.allocated_state_list):
        object_info['Allocated State List'] = \
            get_allocated_object_name_list(wanted_object, kwargs['xml_state_list'])
    if any(wanted_object.allocated_function_list):
        object_info['Allocated Function List'] = \
            get_allocated_object_name_list(wanted_object, kwargs['xml_function_list'])
    return object_info


def get_data_info(wanted_object, object_info, **kwargs):
    """Get what consumes/produces for a specific Data object"""
    pred_list = set()
    object_info['Consumer List'] = \
        get_consumes_produces_info(wanted_object, kwargs['xml_consumer_function_list'])
    object_info['Producer List'] = \
        get_consumes_produces_info(wanted_object, kwargs['xml_producer_function_list'])
    if any(wanted_object.predecessor_list):
        for pred in wanted_object.predecessor_list:
            pred_list.add(pred.name)
    object_info['Predecessor List'] = pred_list
    return object_info


def get_allocation_object(wanted_object, object_list):
    """Get current allocation for an object"""
    allocation_list = set()
    object_type = get_object_type(wanted_object)

    if object_type == 'function':
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.allocated_function_list):
                allocation_list.add(fun_elem)
    elif object_type == 'state':
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.allocated_state_list):
                allocation_list.add(fun_elem)
    elif object_type == 'data':
        for fun_inter in object_list:
            if any(s == wanted_object.id for s in fun_inter.allocated_data_list):
                allocation_list.add(fun_inter)
    elif object_type == 'Functional interface':
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.exposed_interface_list):
                allocation_list.add(fun_elem)
    elif object_type == 'Functional element':
        for function in object_list:
            if any(s == function.id for s in wanted_object.allocated_function_list):
                allocation_list.add(function)
    if allocation_list:
        return allocation_list

    return


def switch_objects_lists(type_list_str, wanted_object, object_type, **kwargs):
    """Switch depending on list's type and object's type """
    if object_type in ("state", "function", "Functional element"):
        switch_type_list = {
            "input": switch_in,
            "output": switch_out,
            "child": switch_child,
            "function": switch_state_function,
            "transition": switch_state_transition,
            "interface": switch_fun_elem_interface,
        }
        if object_type == "state" and type_list_str in ("input", "output"):
            return case_no_list(wanted_object, object_type, **kwargs)
        elif object_type != "state" and type_list_str in ("function", "transition"):
            return case_no_list(wanted_object, object_type, **kwargs)
        elif object_type != "Functional element" and type_list_str == "interface":
            return case_no_list(wanted_object, object_type, **kwargs)
        else:
            type_list = switch_type_list.get(type_list_str, case_no_list)
            return type_list(wanted_object, object_type, **kwargs)

    elif object_type == "Functional interface" and type_list_str == "data":
        return switch_data(wanted_object, object_type, **kwargs)

    else:
        return case_no_list(wanted_object, object_type, **kwargs)


def switch_in(wanted_object, _, **kwargs):
    """Case 'list input Function/Functional ELement' """
    input_list = get_input_or_output_fun_and_fun_elem(wanted_object, direction='input', **kwargs)
    if wanted_object.derived:
        input_list.append(*get_input_or_output_fun_and_fun_elem(wanted_object.derived,
                                                                direction='input', **kwargs))
    if input_list:
        input_dict = {'title': f"Input list for {wanted_object.name}:",
                      'data': input_list,
                      'columns': ["Data name", "Producer"]}
        return input_dict


def switch_out(wanted_object, _, **kwargs):
    """Case 'list output Function/Functional ELement' """
    output_list = get_input_or_output_fun_and_fun_elem(wanted_object, direction='output', **kwargs)
    if wanted_object.derived:
        output_list.append(*get_input_or_output_fun_and_fun_elem(wanted_object.derived,
                                                                 direction='output', **kwargs))
    if output_list:
        output_dict = {'title': f"Output list for {wanted_object.name}:",
                       'data': output_list,
                       'columns': ["Data name", "Consumer"]}
        return output_dict


def switch_child(wanted_object, object_type, **kwargs):
    """Case 'list child Function/State/Functional ELement' """
    child_list = None
    if object_type == "function":
        child_list = get_child_name_list(wanted_object, kwargs['xml_function_list'])
        if wanted_object.derived:
            child_list += [e for e in get_child_name_list(wanted_object.derived,
                                                          kwargs['xml_function_list'])]
    elif object_type == "state":
        child_list = get_child_name_list(wanted_object, kwargs['xml_state_list'])

    elif object_type == "Functional element":
        child_list = get_child_name_list(wanted_object, kwargs['xml_fun_elem_list'])

        child_list.extend(get_fun_elem_function_state_allocation(wanted_object,
                                                                 kwargs['xml_function_list'],
                                                                 kwargs['xml_state_list']))
        if wanted_object.derived:
            child_list += [e for e in get_child_name_list(wanted_object.derived,
                                                          kwargs['xml_fun_elem_list'])]
            child_list += [e for e in get_fun_elem_function_state_allocation(
                wanted_object.derived, kwargs['xml_function_list'], kwargs['xml_state_list'])]

    if child_list:
        child_dict = {'title': f"Child list for {wanted_object.name}:",
                      'data': list(tuple(sorted(child_list))),
                      'columns': ["Object's name", "Relationship's type"]}
        return child_dict


def get_fun_elem_function_state_allocation(wanted_object, xml_function_list, xml_state_list):
    """Returns a list for allocations with:
    [(function.name, "Function allocation"), (state.name, "State allocation"), ...]
    """
    allocation_list = []
    for allocated_fun in wanted_object.allocated_function_list:
        for fun in xml_function_list:
            if fun.id == allocated_fun:
                allocation_list.append((fun.name, "Function allocation"))
    for allocated_state in wanted_object.allocated_state_list:
        for state in xml_state_list:
            if state.id == allocated_state:
                allocation_list.append((state.name, "State allocation"))

    return allocation_list


def switch_state_function(wanted_object, _, **kwargs):
    """Case 'list function State' """
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


def switch_state_transition(wanted_object, _, **kwargs):
    """Case 'list transition State' """
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


def switch_fun_elem_interface(wanted_object, _, **kwargs):
    """Case for 'list interface Functional element'"""
    id_list = wanted_object.exposed_interface_list
    main_fun_elem_child_list, _ = get_children(wanted_object)
    if wanted_object.derived:
        id_list = id_list.union(wanted_object.derived.exposed_interface_list)
        main_fun_elem_child_list = main_fun_elem_child_list.union(
            get_children(wanted_object.derived)[0])

    fun_inter_list = get_objects_from_id_list(id_list,
                                              kwargs['xml_fun_inter_list'])

    if not fun_inter_list:
        return f"Not any exposed interface for {wanted_object.name}"

    exposing_fun_elem = set()
    for interface in fun_inter_list:
        for fun_elem in kwargs['xml_fun_elem_list']:
            if fun_elem not in main_fun_elem_child_list and \
                    interface.id in fun_elem.exposed_interface_list and \
                    check_not_family(fun_elem, wanted_object):
                exposing_fun_elem.add((interface, fun_elem))

    interface_list = set()
    for k in exposing_fun_elem:
        child_list, _ = get_children(k[1])
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


def switch_data(wanted_object, _, **kwargs):
    """Case for 'list data Functional Interface' """
    data_list = []
    fun_elem_exposing = get_allocation_object(wanted_object, kwargs['xml_fun_elem_list'])
    if wanted_object.derived:
        derived_fun_elem_exposing = get_allocation_object(wanted_object.derived,
                                                          kwargs['xml_fun_elem_list'])
        if derived_fun_elem_exposing and fun_elem_exposing:
            fun_elem_exposing = fun_elem_exposing.union(derived_fun_elem_exposing)

    if not fun_elem_exposing:
        return f"Not any functional element exosing {wanted_object.name}"
    last_fun_elem_exposing = [check_latest(j, fun_elem_exposing) for j in fun_elem_exposing
                              if check_latest(j, fun_elem_exposing)]

    for allocated_id in wanted_object.allocated_data_list:
        for data in kwargs['xml_data_list']:
            if allocated_id == data.id:
                data_list.append(get_latest_obj_interface(data, last_fun_elem_exposing, **kwargs))

    if wanted_object.derived:
        for allocated_id in wanted_object.derived.allocated_data_list:
            for data in kwargs['xml_data_list']:
                if allocated_id == data.id:
                    data_list.append(
                        get_latest_obj_interface(data, last_fun_elem_exposing, **kwargs))

    if data_list:
        data_dict = {'title': f"Data list for {wanted_object.name}:",
                     'data': data_list}
        return data_dict


def case_no_list(wanted_object, object_type, _):
    """Case when there is incompatible list's type with object's type """
    return f"No list available for object '{wanted_object.name}' " \
           f"of type '{object_type.capitalize()}', possible lists are:\n" \
           f"- List child [Function/State/Functional element]\n" \
           f"- List input/output [Function/Functional element]\n" \
           f"- List function/transition [State]\n" \
           f"- List interface [Functional element]\n" \
           f"- List data [Functional interface]"


def get_latest_obj_interface(data, last_fun_elem_exposing, **kwargs):
    """For a data, find last producer and consumer if they are allocated to last fun_elem
    exposing the functional interface asked"""
    data_dict = {'Data': data.name,
                 'Last consumer Function(s)': [],
                 'Last consumer Functional element(s)': [],
                 'Last producer Function(s)': [],
                 'Last producer Functional element(s)': []}
    for prod in kwargs['xml_producer_function_list']:
        if prod[0] == data.name and \
                check_latest(prod[1], kwargs['xml_function_list']) == prod[1].name:
            for cons in kwargs['xml_consumer_function_list']:
                cons_last_fun_elem = None
                prod_last_fun_elem = None
                if cons[0] == prod[0] and \
                        check_latest(cons[1], kwargs['xml_function_list']) == cons[1].name:
                    cons_fun_elem_list = get_allocation_object(cons[1], kwargs['xml_fun_elem_list'])
                    if cons_fun_elem_list:
                        for fun_elem in cons_fun_elem_list:
                            if fun_elem.name in last_fun_elem_exposing:
                                cons_last_fun_elem = fun_elem
                    prod_fun_elem_list = get_allocation_object(prod[1], kwargs['xml_fun_elem_list'])
                    if prod_fun_elem_list:
                        for fun_elem in prod_fun_elem_list:
                            if fun_elem.name in last_fun_elem_exposing:
                                prod_last_fun_elem = fun_elem

                if not cons_last_fun_elem == prod_last_fun_elem:
                    if not any(c == prod[1].name for c in data_dict['Last producer Function(s)']):
                        if prod_last_fun_elem and \
                                prod[1].id in prod_last_fun_elem.allocated_function_list:
                            data_dict['Last producer Function(s)'].append(prod[1].name)
                            data_dict['Last producer Functional element(s)'].append(
                                prod_last_fun_elem.name)
                    if not any(c == cons[1].name for c in data_dict['Last consumer Function(s)']):
                        if cons_last_fun_elem and \
                                cons[1].id in cons_last_fun_elem.allocated_function_list:
                            data_dict['Last consumer Function(s)'].append(cons[1].name)
                            data_dict['Last consumer Functional element(s)'].append(
                                cons_last_fun_elem.name)

    return data_dict


def check_latest(wanted_object, check_list):
    """Checks and returns latest object = last one decomposed"""
    if not wanted_object.child_list:
        return wanted_object.name
    else:
        check_child = [c for c in wanted_object.child_list]
        if not any(j in check_child for j in check_list):
            return wanted_object.name


def get_object_list(object_str, **kwargs):
    """
    Gets lists from object_str : i.e. Input/Output/Child/Data
    Args:
        object_str ([object_string]): list of object's name from cell
        **kwargs: all xml lists

    Returns:
        answer_list: [Input_list, Output_list, Child_list, Data_list]
    """
    answer_list = []
    for elem in object_str:
        wanted_object = check_get_object(elem[1], **kwargs)
        if wanted_object is None:
            print(f"Object '{elem[1]}' does not exist")
        else:
            object_type = get_object_type(wanted_object)
            wanted_list = switch_objects_lists(elem[0], wanted_object, object_type, **kwargs)
            if isinstance(wanted_list, (list, dict)):
                answer_list.append(wanted_list)
            elif isinstance(wanted_list, str):
                print(wanted_list)
            else:
                print(f"Nothing to display for {elem[0]} list of '{wanted_object.name}'")

    return answer_list


def get_input_or_output_fun_and_fun_elem(wanted_object, direction='input', unmerged=False,
                                         **kwargs):
    """
    Gets inputs/outputs for object (Function or Functional Element):
    i.e. what is consumed/produces by wanted object or object allocated functions.
    Args:
        wanted_object: current object
        direction (str: default=input): i.e. input or output asked
        unmerged (bool: default=false): used by functional elements
        **kwargs: all xml lists

    Returns:
        input or output list
    """
    object_type = get_object_type(wanted_object)
    if object_type == "Functional element":
        in_or_out_list = []
        allocated_fun_list = set()
        for fun in wanted_object.allocated_function_list:
            for xml_fun in kwargs['xml_function_list']:
                if fun == xml_fun.id:
                    allocated_fun_list.add(xml_fun)
        for func in allocated_fun_list:
            current_fun_list = get_input_or_output_fun_and_fun_elem(func, direction, True, **kwargs)
            for sub in current_fun_list:
                if sub and sub[1] not in [f.name for f in allocated_fun_list]:
                    in_or_out_list.append(sub)
        return merge_list_per_cons_prod(in_or_out_list)
    else:
        if direction == 'output':
            in_or_out_list = get_in_out_function(wanted_object,
                                                 kwargs['xml_producer_function_list'],
                                                 kwargs['xml_consumer_function_list'])
        else:
            in_or_out_list = get_in_out_function(wanted_object,
                                                 kwargs['xml_consumer_function_list'],
                                                 kwargs['xml_producer_function_list'])
        if unmerged:
            return in_or_out_list
        else:
            return merge_list_per_cons_prod(in_or_out_list)


def merge_list_per_cons_prod(input_list):
    """
    Sorts data's name in alphabetical order and merges list by producer or consumer
    Args:
        input_list ([Data_name, funcion_name]): List of consumer/producer with data per Function

    Returns:
        Sorted + merged list
    """
    input_list = sorted(input_list)
    output_list = []
    empty_dict = {}
    for data, obj_name in input_list:
        if data not in empty_dict:
            output_list.append([data, obj_name])
            empty_dict[data] = len(empty_dict)
        else:
            if obj_name:
                if obj_name not in output_list[empty_dict[data]][1]:
                    output_list[empty_dict[data]][1] += '\\n' + obj_name

    return output_list


def get_in_out_function(wanted_object, wanted_relationship, opposite_wanted_relationship):
    """
    Return the list of Input/Output for Function's objects.
    Args:
        wanted_object (Function): Object's wanted
        wanted_relationship ([Xml_list]): For Output (producer's list) and Input (consumer's list)
        opposite_wanted_relationship ([Xml_list]): slef-explained
    Returns:
        output_list ([Data, prod/cons])
    """
    output_list = []
    flow_list = get_consumes_produces_info(wanted_object, wanted_relationship)
    if not flow_list:
        return output_list
    for data in flow_list:
        if not any(data in s for s in opposite_wanted_relationship):
            output_list.append([data, None])
        else:
            for elem in opposite_wanted_relationship:
                check = True
                if elem[0] == data:
                    for child in elem[1].child_list:
                        if [elem[0], child] in opposite_wanted_relationship:
                            check = False
                    if check:
                        output_list.append([elem[0], elem[1].name])

    return output_list


def get_objects_from_id_list(id_list, object_list):
    """From a list of id (from same type) returns list of corresponding objects"""
    output_list = set()
    if not id_list:
        return output_list

    for wanted_object in object_list:
        if wanted_object.id in id_list:
            output_list.add(wanted_object)

    return output_list


def get_objects_names(xml_object_list):
    """
    Method that returns a list with all object aliases/names from object's list

    """
    object_name_list = []
    # Create the xml [object_name (and object_alias)] list
    for xml_object in xml_object_list:
        object_name_list.append(xml_object.name)
        try:
            if len(xml_object.alias) > 0:
                object_name_list.append(xml_object.alias)
        except AttributeError:
            # To avoid error when there is no alias attribute for the object
            pass

    return object_name_list


def check_parentality(object_a, object_b):
    """Check recursively if object 'a' is not parent of object 'b'"""
    if object_b.parent:
        if object_a == object_b.parent:
            return True
        else:
            return check_parentality(object_a, object_b.parent)
    else:
        return False


def get_children(element, function_list=None, parent_dict=None, count=None, level=None):
    """Get children recursively, adds them to function_list and create parend_dict"""
    if function_list is None:
        function_list = set()
    if parent_dict is None:
        parent_dict = {}
    if not count:
        count = 0

    function_list.add(element)
    if element.child_list:
        count += 1
        if level:
            if (count - 1) == level:
                element.child_list.clear()
                return function_list, parent_dict
        for child in element.child_list:
            parent_dict[child.id] = element.id
            get_children(child, function_list, parent_dict, count, level)

    return function_list, parent_dict


def check_not_family(object_a, object_b):
    """Returns True if object_a and object_b are not in the same family"""
    if not check_parentality(object_a, object_b) and not check_parentality(object_b, object_a):
        return True
    else:
        return False


def get_object_type(object_to_check):
    """From an object, returns its type as string"""
    obj_type_list = [(datamodel.State, 'state'), (datamodel.Function, 'function'),
                     (datamodel.Data, 'data'), (datamodel.FunctionalElement, 'Functional element'),
                     (datamodel.View, 'View'), (datamodel.Transition, 'Transition'),
                     (datamodel.Attribute, 'Attribute'),
                     (datamodel.FunctionalInterface, 'Functional interface'),
                     (datamodel.PhysicalElement, 'Physical element'),
                     (datamodel.PhysicalInterface, 'Physical interface')]
    object_type = ''
    for elem in obj_type_list:
        if isinstance(object_to_check, elem[0]):
            object_type = elem[1]
            return object_type
    return object_type


def get_pandas_table(data_dict):
    """Returns pandas data frame called from command_parser.matched_list()
    with data_dict as list of ..."""
    if 'columns' in data_dict.keys():
        data_frame = pd.DataFrame(data_dict['data'], columns=data_dict['columns'])
    else:
        data_frame = pd.DataFrame(data_dict['data'])
    data_frame = data_frame.T
    if 'Data' in data_dict['title'] or 'Transition' in data_dict['title']:
        if 'Data' in data_dict['title']:
            first = 1
            last = 5
        else:
            first = 3
            last = 4
        for idx in range(first, last):
            data_frame.iloc[idx] = data_frame.iloc[idx].str.join("\\n")
    data_frame = data_frame.style \
        .set_caption(data_dict['title']) \
        .set_properties(**{'white-space': 'nowrap'})

    return data_frame.to_html().replace("\\n", "<br>")
