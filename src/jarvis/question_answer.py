#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import re
# Modules
import orchestrator

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


def matched_what(question_str, **kwargs):
    # Create object names/aliases lists
    xml_function_name_list = orchestrator.get_object_name(kwargs['xml_function_list'])
    xml_data_name_list = orchestrator.get_object_name(kwargs['xml_data_list'])
    xml_state_name_list = orchestrator.get_object_name(kwargs['xml_state_list'])
    xml_fun_elem_name_list = orchestrator.get_object_name(kwargs['xml_fun_elem_list'])
    xml_transition_name_list = orchestrator.get_object_name(kwargs['xml_transition_list'])
    whole_objects_name_list = [*xml_function_name_list, *xml_data_name_list, *xml_state_name_list,
                               *xml_fun_elem_name_list, *xml_transition_name_list]
    object_str = question_str[0].strip()

    if not any(str(object_str) in s for s in whole_objects_name_list):
        print(f"{object_str} does not exist")

    result_function = any(object_str in s for s in xml_function_name_list)
    resul_state = any(object_str in s for s in xml_state_name_list)
    result_data = any(object_str in s for s in xml_data_name_list)
    result_fun_elem = any(object_str in s for s in xml_fun_elem_name_list)
    result_transition = any(object_str in s for s in xml_transition_name_list)
    result = [result_function, result_data, resul_state,  result_fun_elem, result_transition]
    wanted_object = match_object(object_str, result, **kwargs)
    if wanted_object:
        object_info = get_object_info(wanted_object, **kwargs)
        if object_info:
            return object_info

    return None


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
    return None


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

    return None


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

    return None


def get_child_name_list(parent_object, object_list):
    child_list = set()
    for child in object_list:
        if child in parent_object.child_list:
            child_list.add(child.name)
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
                               + ", ".join(list(allocation_list))
                return object_info

    return None


def get_allocation_object(wanted_object, fun_elem_list):
    allocation_list = set()

    object_type = orchestrator.get_object_type(wanted_object)

    if object_type == 'function':
        for fun_elem in fun_elem_list:
            if any(wanted_object.id in s for s in fun_elem.allocated_function_list):
                allocation_list.add(fun_elem.name)
    elif object_type == 'state':
        for fun_elem in fun_elem_list:
            if any(wanted_object.id in s for s in fun_elem.allocated_state_list):
                allocation_list.add(fun_elem.name)
    if allocation_list:
        return allocation_list

    return None

