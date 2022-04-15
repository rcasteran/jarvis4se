#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import re
# Modules
from . import orchestrator

question_type = [
    (r"What is ([^\.\n]*) ", lambda matched_str, **kwargs: matched_what(matched_str, **kwargs)),

    (r"Is (.*) allocated ", lambda matched_str, **kwargs: matched_allocated(matched_str, **kwargs)),
]


def lookup(strings, questions, **kwargs):
    answer_list = []
    for pattern, values in questions:
        for i in strings:
            result = re.findall(pattern, i, re.MULTILINE)
            if result:
                answer = values(result, **kwargs)
                if answer:
                    answer_list.append(answer)
    return answer_list


def find_question(string, **kwargs):
    out = lookup(string, question_type, **kwargs)
    return out


def check_get_object(object_str, **kwargs):
    """
    Returns the desired object from object's string
    Args:
        object_str ([object_string]): list of object's name from cell
        **kwargs: all xml lists

    Returns:
        wanted_object : Function/State/Data/Fun_Elem/Transition
    """
    # Create object names/aliases lists
    xml_function_name_list = orchestrator.get_object_name(kwargs['xml_function_list'])
    xml_data_name_list = orchestrator.get_object_name(kwargs['xml_data_list'])
    xml_state_name_list = orchestrator.get_object_name(kwargs['xml_state_list'])
    xml_fun_elem_name_list = orchestrator.get_object_name(kwargs['xml_fun_elem_list'])
    xml_transition_name_list = orchestrator.get_object_name(kwargs['xml_transition_list'])
    whole_objects_name_list = [*xml_function_name_list, *xml_data_name_list, *xml_state_name_list,
                               *xml_fun_elem_name_list, *xml_transition_name_list]
    if not [object_str in whole_objects_name_list]:
        print(f"{object_str} does not exist")
    else:
        result_function = [object_str in xml_function_name_list]
        resul_state = [object_str in xml_state_name_list]
        result_data = [object_str in xml_data_name_list]
        result_fun_elem = [object_str in xml_fun_elem_name_list]
        result_transition = [object_str in xml_transition_name_list]
        result = [*result_function, *result_data, *resul_state,  *result_fun_elem,
                  *result_transition]
        wanted_object = match_object(object_str, result, **kwargs)
        return wanted_object


def matched_what(question_str, **kwargs):
    # TODO: Handle multiple questions ? => TBC
    object_str = question_str[0].strip()
    wanted_object = check_get_object(object_str, **kwargs)

    if wanted_object:
        object_info = get_object_info(wanted_object, **kwargs)
        if object_info:
            return object_info


def match_object(object_str, result, **kwargs):
    if result[0]:
        for function in kwargs['xml_function_list']:
            if object_str in (function.name, function.alias):
                return function
    elif result[1]:
        for data in kwargs['xml_data_list']:
            if object_str == data.name:
                return data
    elif result[2]:
        for state in kwargs['xml_state_list']:
            if object_str in (state.name, state.alias):
                return state
    elif result[3]:
        for fun_elem in kwargs['xml_fun_elem_list']:
            if object_str in (fun_elem.name, fun_elem.alias):
                return fun_elem
    elif result[4]:
        for transition in kwargs['xml_transition_list']:
            if object_str in (transition.name, transition.alias):
                return transition


def get_object_info(wanted_object, **kwargs):
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
    object_relationship = set()
    for elem in relationship_list:
        if elem[1].id == wanted_object.id:
            object_relationship.add(elem[0])
        if elem[0] == wanted_object.name:
            object_relationship.add(elem[1].name)
    if object_relationship:
        return object_relationship


def get_child_name_list(parent_object, object_list):
    child_list = set()
    for child in object_list:
        if child in parent_object.child_list:
            child_list.add((child.name, "Child"))
    return child_list


def get_allocated_object_name_list(wanted_object, object_list):
    allocation_list = set()
    for allocated_object in object_list:
        if any(allocated_object.id in s for s in wanted_object.allocated_state_list):
            allocation_list.add(allocated_object.name)
        if any(allocated_object.id in s for s in wanted_object.allocated_function_list):
            allocation_list.add(allocated_object.name)
    return allocation_list


def get_transition_info(wanted_object, state_list, object_info):
    for state in state_list:
        if state.id == wanted_object.source:
            object_info['Source'] = str(state.name)
        if state.id == wanted_object.destination:
            object_info['Destination'] = str(state.name)
    if wanted_object.condition_list:
        object_info['Condition List'] = wanted_object.condition_list
    return object_info


def get_fun_elem_info(wanted_object, object_info, **kwargs):
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


def matched_allocated(object_str, **kwargs):
    object_info = ""
    object_str = object_str[0]
    xml_function_name_list = orchestrator.get_object_name(kwargs['xml_function_list'])
    xml_state_name_list = orchestrator.get_object_name(kwargs['xml_state_list'])
    whole_objects_name_list = [*xml_function_name_list, *xml_state_name_list]
    if not any(object_str in s for s in whole_objects_name_list):
        print(f"{object_str} is not a function nor a state")
    else:
        result_function = any(object_str in s for s in xml_function_name_list)
        resul_state = any(object_str in s for s in xml_state_name_list)
        result = [result_function, False, resul_state,  False, False]
        wanted_object = match_object(object_str, result, **kwargs)
        if wanted_object:
            allocation_list = get_allocation_object(wanted_object, kwargs['xml_fun_elem_list'])
            if allocation_list:
                object_info += f'"{wanted_object.name}" is allocated to ' \
                               + ", ".join([elem.name for elem in allocation_list])
                return object_info

    return


def get_allocation_object(wanted_object, object_list):
    """Get current allocation for an object Fun_elem with State/Function OR Fun_inter with data"""
    allocation_list = set()

    object_type = orchestrator.get_object_type(wanted_object)

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
    if allocation_list:
        return allocation_list

    return


def get_object_list(object_str, **kwargs):
    """
    Gets lists from object_str : i.e. Input/Output/child
    Args:
        object_str ([object_string]): list of object's name from cell
        **kwargs: all xml lists

    Returns:
        answer_list: [Input_list, Output_list, Child_list]
    """
    answer_list = []
    for elem in object_str:
        wanted_object = check_get_object(elem[1], **kwargs)
        object_type = orchestrator.get_object_type(wanted_object)
        if object_type in ("state", "function", "Functional element"):
            if elem[0] == "input":
                list_name = f"Input list for {wanted_object.name}:"
                input_list = get_input(wanted_object, **kwargs)
                if input_list:
                    input_list.insert(0, list_name)
                    answer_list.append(input_list)
            elif elem[0] == "output":
                list_name = f"Output list for {wanted_object.name}:"
                output_list = get_output(wanted_object, **kwargs)
                if output_list:
                    output_list.insert(0, list_name)
                    answer_list.append(output_list)
            elif elem[0] == "child":
                list_name = f"Child list for {wanted_object.name}:"
                child_list = None
                if object_type == "function":
                    child_list = list(get_child_name_list(wanted_object,
                                                          kwargs['xml_function_list']))
                elif object_type == "state":
                    child_list = list(get_child_name_list(wanted_object,
                                                          kwargs['xml_state_list']))
                    for allocated_fun in wanted_object.allocated_function_list:
                        for fun in kwargs['xml_function_list']:
                            if fun.id == allocated_fun:
                                child_list.append((fun.name, "Function allocation"))
                elif object_type == "Functional element":
                    child_list = list(get_child_name_list(wanted_object,
                                                          kwargs['xml_fun_elem_list']))
                    for allocated_fun in wanted_object.allocated_function_list:
                        for fun in kwargs['xml_function_list']:
                            if fun.id == allocated_fun:
                                child_list.append((fun.name, "Function allocation"))
                    for allocated_state in wanted_object.allocated_state_list:
                        for state in kwargs['xml_state_list']:
                            if state.id == allocated_state:
                                child_list.append((state.name, "State allocation"))

                child_list = list(tuple(sorted(child_list)))
                child_list.insert(0, list_name)
                answer_list.append(child_list)

        else:
            if wanted_object is None:
                print(f"Object '{elem[1]}' does not exist")
            else:
                print(f"No list available for object '{wanted_object.name}' of type "
                      f"'{object_type.capitalize()}', possible types are: Function, "
                      f"State and Functional element.")

    return answer_list


def get_input(wanted_object, unmerged=False, **kwargs):
    """
    Gets inputs for object (Function or Functional Element): i.e. what is consumed by wanted object.
    Args:
        wanted_object: current object
        unmerged (bool: default=false): used by functional elements
        **kwargs: all xml lists

    Returns:
        Input's list
    """
    object_type = orchestrator.get_object_type(wanted_object)
    if object_type == "state":
        print(f"No input list available for object's type "
              f"{object_type.capitalize()}({wanted_object.name}).")
    elif object_type == "Functional element":
        input_list = []
        for fun in wanted_object.allocated_function_list:
            for xml_fun in kwargs['xml_function_list']:
                if fun == xml_fun.id:
                    current_fun_list = get_input(xml_fun, True, **kwargs)
                    for sub in current_fun_list:
                        if sub:
                            input_list.append(sub)
        return merge_list_per_cons_prod(input_list)
    else:
        input_list = get_in_out_function(wanted_object,
                                         kwargs['xml_consumer_function_list'],
                                         kwargs['xml_producer_function_list'])
        if unmerged:
            return input_list
        else:
            return merge_list_per_cons_prod(input_list)


def get_output(wanted_object, unmerged=False, **kwargs):
    """
    Gets outputs for object (Function or Functional Element): i.e. what is produced by wanted object.
    Args:
        wanted_object: current object
        unmerged (bool: default=false): used by functional elements
        **kwargs: all xml lists

    Returns:
        Output's list
    """
    object_type = orchestrator.get_object_type(wanted_object)
    if object_type == "state":
        print(f"No output list available for object's type "
              f"{object_type.capitalize()}({wanted_object.name}).")
    elif object_type == "Functional element":
        output_list = []
        for fun in wanted_object.allocated_function_list:
            for xml_fun in kwargs['xml_function_list']:
                if fun == xml_fun.id:
                    current_fun_list = get_output(xml_fun, True, **kwargs)
                    for sub in current_fun_list:
                        if sub:
                            output_list.append(sub)
        return merge_list_per_cons_prod(output_list)
    else:
        output_list = get_in_out_function(wanted_object,
                                          kwargs['xml_producer_function_list'],
                                          kwargs['xml_consumer_function_list'])
        if unmerged:
            return output_list
        else:
            return merge_list_per_cons_prod(output_list)


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
