#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module with methods relative to Diagram generation for filtering objects before passing
them to plantuml_adapter.py"""
# Libraries
import re

import plantuml_adapter
from .question_answer import check_parentality, get_objects_names, check_get_object, switch_data, \
    get_children, check_not_family, switch_fun_elem_interface
from .shared_orchestrator import childs_inheritance, reset_childs_inheritance, \
    attribute_inheritance, reset_attribute_inheritance, view_inheritance, reset_view_inheritance, \
    allocation_inheritance, reset_alloc_inheritance


def filter_show_command(diagram_name_str, **kwargs):
    """Entry point for all diagrams (i.e. 'show' command) from command_parser.py"""
    plantuml_string = None
    wanted_diagram_str = diagram_name_str.group(1)
    regex = r"(decomposition|context|chain|sequence|state|function|state sequence)\s(.*)"
    specific_diagram_str = re.search(regex, wanted_diagram_str, re.MULTILINE)
    if specific_diagram_str:
        if 'sequence' not in specific_diagram_str.group(2):
            diagram_type_str = specific_diagram_str.group(1)
            diagram_object_str = specific_diagram_str.group(2)
        else:
            diagram_type_str = specific_diagram_str.group(1) + ' sequence'
            diagram_object_str = specific_diagram_str.group(2).replace("sequence ", "")

        plantuml_string = switch_show_filter(diagram_type_str=diagram_type_str,
                                             diagram_object_str=diagram_object_str,
                                             **kwargs)
    else:
        print(f"Jarvis does not understand the command {wanted_diagram_str}")

    return plantuml_string


def switch_show_filter(**kwargs):
    """Switch case between diagram types"""
    switch = {
        "function": case_function_diagram,
        "context": case_context_diagram,
        "decomposition": case_decomposition_diagram,
        "chain": case_chain_diagram,
        "sequence": case_sequence_diagram,
        "state": case_state_diagram,
        "state sequence": case_state_sequence_diagram
    }
    get_diagram = switch.get(kwargs['diagram_type_str'], case_no_diagram)
    return get_diagram(**kwargs)


def case_function_diagram(**kwargs):
    """Case for 'show function <functional_element>'"""
    plantuml_string = None
    xml_fun_elem_name_list = get_objects_names(kwargs['xml_fun_elem_list'])
    if kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        plantuml_string = show_fun_elem_function(kwargs['diagram_object_str'],
                                                 kwargs['xml_fun_elem_list'],
                                                 kwargs['xml_function_list'],
                                                 kwargs['xml_consumer_function_list'],
                                                 kwargs['xml_producer_function_list'],
                                                 kwargs['xml_type_list'])

    else:
        print(f"Jarvis does not know the functional Element {kwargs['diagram_object_str']}")

    return plantuml_string


def case_context_diagram(**kwargs):
    """Case for 'show context <functional_element>/<function>'"""
    plantuml_string = None
    xml_function_name_list = get_objects_names(kwargs['xml_function_list'])
    xml_state_name_list = get_objects_names(kwargs['xml_state_list'])
    xml_fun_elem_name_list = get_objects_names(kwargs['xml_fun_elem_list'])

    if kwargs['diagram_object_str'] in xml_function_name_list:
        plantuml_string = show_function_context(kwargs['diagram_object_str'],
                                                kwargs['xml_function_list'],
                                                kwargs['xml_consumer_function_list'],
                                                kwargs['xml_producer_function_list'],
                                                kwargs['xml_data_list'],
                                                kwargs['xml_attribute_list'],
                                                kwargs['xml_type_list'])

    elif kwargs['diagram_object_str'] in xml_state_name_list:
        plantuml_string = show_states_chain([kwargs['diagram_object_str']],
                                            kwargs['xml_state_list'],
                                            kwargs['xml_transition_list'])

    elif kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        plantuml_string = show_fun_elem_context(kwargs['diagram_object_str'],
                                                kwargs['xml_fun_elem_list'],
                                                kwargs['xml_function_list'],
                                                kwargs['xml_consumer_function_list'],
                                                kwargs['xml_producer_function_list'],
                                                kwargs['xml_attribute_list'],
                                                kwargs['xml_fun_inter_list'],
                                                kwargs['xml_data_list'])
    else:
        print(f"Jarvis does not know the function {kwargs['diagram_object_str']} or "
              f"{kwargs['diagram_object_str']} is not a valid "
              f"Function/State/Functional Element name/alias")

    return plantuml_string


def case_decomposition_diagram(**kwargs):
    """Case for 'show decomposition <functional_element>/<function>'"""
    plantuml_string = None

    if ' at level ' in kwargs['diagram_object_str']:
        splitted_str = re.split(" at level ", kwargs['diagram_object_str'])
        diagram_object_str = splitted_str[0]
        try:
            diagram_level = int(splitted_str[1])
            if diagram_level == 0:
                print("Invalid level, please choose a valid level >= 1")
                return plantuml_string
        except ValueError:
            print("Invalid level, please choose a valid level >= 1")
            return plantuml_string
    else:
        diagram_object_str = kwargs['diagram_object_str']
        diagram_level = None

    v_inheritance = view_inheritance(kwargs['xml_view_list'],
                                     kwargs['xml_function_list'],
                                     kwargs['xml_fun_elem_list'])

    # Check view if activated and filter allocated item,
    # if not activated then no item filtered
    # if not any item under view return string for user's message
    function_list = get_object_list_from_view(diagram_object_str,
                                              kwargs['xml_function_list'],
                                              kwargs['xml_view_list'])
    if isinstance(function_list, str):
        print(function_list)
        return None

    if diagram_object_str in get_objects_names(kwargs['xml_function_list']):
        consumer_list, producer_list = get_cons_prod_from_view_allocated_data(
            kwargs['xml_data_list'],
            kwargs['xml_view_list'],
            kwargs['xml_consumer_function_list'],
            kwargs['xml_producer_function_list'],
            function_list)

        plantuml_string = show_function_decomposition(diagram_object_str,
                                                      function_list,
                                                      consumer_list,
                                                      producer_list,
                                                      kwargs['xml_attribute_list'],
                                                      kwargs['xml_type_list'],
                                                      diagram_level=diagram_level)

    elif diagram_object_str in get_objects_names(kwargs['xml_fun_elem_list']):
        fun_elem_list = get_object_list_from_view(diagram_object_str,
                                                  kwargs['xml_fun_elem_list'],
                                                  kwargs['xml_view_list'])
        consumer_list, producer_list = get_cons_prod_from_view_allocated_data(
            kwargs['xml_data_list'],
            kwargs['xml_view_list'],
            kwargs['xml_consumer_function_list'],
            kwargs['xml_producer_function_list'],
            function_list)

        plantuml_string = show_fun_elem_decomposition(diagram_object_str,
                                                      function_list,
                                                      consumer_list,
                                                      producer_list,
                                                      fun_elem_list,
                                                      kwargs['xml_attribute_list'],
                                                      kwargs['xml_data_list'],
                                                      kwargs['xml_fun_inter_list'],
                                                      diagram_level)

    else:
        print(f"Jarvis does not know the object {diagram_object_str}"
              f"(i.e. it is not a function, nor a functional element)")

    reset_view_inheritance(kwargs['xml_view_list'], v_inheritance)

    return plantuml_string


def get_cons_prod_from_view_allocated_data(xml_data_list, xml_view_list, xml_consumer_function_list,
                                           xml_producer_function_list, function_list):
    """If a view is activated, returns filtered consumer/producer lists"""
    new_consumer_list = []
    new_producer_list = []
    new_data_list = filter_allocated_item_from_view(xml_data_list, xml_view_list)

    if len(new_data_list) == len(xml_data_list):
        for prod in xml_producer_function_list:
            if any(item == prod[1] for item in function_list):
                new_producer_list.append(prod)

        for cons in xml_consumer_function_list:
            if any(item == cons[1] for item in function_list):
                new_consumer_list.append(cons)

    else:
        for cons in xml_consumer_function_list:
            if any(item.name == cons[0] for item in new_data_list) and \
                    any(item == cons[1] for item in function_list):
                new_consumer_list.append(cons)

        for prod in xml_producer_function_list:
            if any(item.name == prod[0] for item in new_data_list) and \
                    any(item == prod[1] for item in function_list):
                new_producer_list.append(prod)

    return new_consumer_list, new_producer_list


def get_object_list_from_view(obj_str, xml_obj_list, xml_view_list):
    """Returns current object's list by checking view"""
    output_list = filter_allocated_item_from_view(xml_obj_list, xml_view_list)
    if isinstance(output_list, str):
        return output_list

    if len(xml_obj_list) == len(output_list):
        return xml_obj_list

    if isinstance(obj_str, str):
        for obj in xml_obj_list:
            if obj_str in (obj.name, obj.alias) and not any(item == obj for item in output_list):
                output_list.append(obj)
    elif isinstance(obj_str, list):
        for object_name in obj_str:
            for obj in xml_obj_list:
                if object_name in (obj.name, obj.alias) and \
                        not any(item == obj for item in output_list):
                    output_list.append(obj)

    for new_obj in output_list:
        child_list = set()
        for child in new_obj.child_list:
            if child in output_list:
                child_list.add(child)
        new_obj.child_list.clear()
        new_obj.child_list = child_list

    return output_list


def case_chain_diagram(**kwargs):
    """Case for 'show chain <states>/<functions>'"""
    plantuml_string = None
    xml_function_name_list = get_objects_names(kwargs['xml_function_list'])
    xml_state_name_list = get_objects_names(kwargs['xml_state_list'])
    object_list_str = re.split(r',(?![^[]*\])', kwargs['diagram_object_str'].replace(" ", ""))
    if len(object_list_str) > 0:
        result_function = all(t in xml_function_name_list for t in object_list_str)
        result_state = all(t in xml_state_name_list for t in object_list_str)
        if not result_function and not result_state:
            for i in object_list_str:
                if len(i) > 0:
                    if not any(i in s for s in [*xml_function_name_list,
                                                *xml_state_name_list]):
                        print(f"The object {i} does not exist, "
                              f"not a function/state's name nor an alias")
                else:
                    print(f"{kwargs['diagram_object_str']} is not a valid chain")

        elif result_function or result_state:
            if result_function:
                # Check view if activated and filter allocated item,
                # if not activated then no item filtered
                # if not any item under view return string
                function_list = get_object_list_from_view(object_list_str,
                                                          kwargs['xml_function_list'],
                                                          kwargs['xml_view_list'])
                if isinstance(function_list, str):
                    print(function_list)
                    return None
                consumer_list, producer_list = get_cons_prod_from_view_allocated_data(
                    kwargs['xml_data_list'],
                    kwargs['xml_view_list'],
                    kwargs['xml_consumer_function_list'],
                    kwargs['xml_producer_function_list'],
                    function_list)
                plantuml_string = show_functions_chain(object_list_str,
                                                       function_list,
                                                       consumer_list,
                                                       producer_list,
                                                       kwargs['xml_type_list'])
            elif result_state:
                # See above after "if result_function"
                state_list = get_object_list_from_view(object_list_str,
                                                       kwargs['xml_state_list'],
                                                       kwargs['xml_view_list'])
                if isinstance(state_list, str):
                    print(state_list)
                    return None
                transition_list = filter_allocated_item_from_view(kwargs['xml_transition_list'],
                                                                  kwargs['xml_view_list'])
                plantuml_string = show_states_chain(object_list_str, state_list, transition_list)
        else:
            print(f"{kwargs['diagram_object_str']} is not a valid chain")

    return plantuml_string


def case_sequence_diagram(**kwargs):
    """Case for 'show sequence <functional_elements>/<functions>/<functional_interface>'"""
    plantuml_string = None
    object_list_str = re.split(r',(?![^[]*\])', kwargs['diagram_object_str'].replace(", ", ","))
    object_list_str = [s.rstrip() for s in object_list_str]
    if object_list_str:
        if len(object_list_str) == 1 and \
                any(s == object_list_str[0] for s in get_objects_names(kwargs['xml_fun_inter_list'])):
            plantuml_string = get_fun_inter_sequence_diagram(object_list_str.pop(), **kwargs)
        elif len(object_list_str) >= 1:
            # Check view if activated and filter allocated item,
            # if not activated then no item filtered
            # if not any item under view return string
            xml_data_list = filter_allocated_item_from_view(kwargs['xml_data_list'],
                                                            kwargs['xml_view_list'])
            if isinstance(xml_data_list, str):
                print(xml_data_list)
                return None
            if all(i in get_objects_names(kwargs['xml_function_list']) for i in object_list_str):

                if len(xml_data_list) != len(kwargs['xml_data_list']):
                    xml_cons = [i for i in kwargs['xml_consumer_function_list']
                                if any(a == i[0] for a in [d.name for d in xml_data_list])]
                    xml_prod = [i for i in kwargs['xml_producer_function_list']
                                if any(a == i[0] for a in [d.name for d in xml_data_list])]
                else:
                    xml_cons = kwargs['xml_consumer_function_list']
                    xml_prod = kwargs['xml_producer_function_list']
                plantuml_string = show_functions_sequence(object_list_str,
                                                          kwargs['xml_function_list'],
                                                          xml_cons,
                                                          xml_prod,
                                                          xml_data_list)

            elif all(i in get_objects_names(kwargs['xml_fun_elem_list']) for i in object_list_str):
                if len(xml_data_list) != len(kwargs['xml_data_list']):
                    kwargs['xml_consumer_function_list'] = \
                        [i for i in kwargs['xml_consumer_function_list']
                         if any(a == i[0] for a in [d.name for d in xml_data_list])]
                    kwargs['xml_producer_function_list'] = \
                        [i for i in kwargs['xml_producer_function_list']
                         if any(a == i[0] for a in [d.name for d in xml_data_list])]
                kwargs['xml_data_list'] = xml_data_list
                plantuml_string = get_fun_elem_sequence_diagram(object_list_str, **kwargs)

            else:
                print(f"{kwargs['diagram_object_str']} is not a valid sequence, availabe sequences "
                      f"are:\n"
                      f"- show sequence Function_A, Function_B, ...\n"
                      f"- show sequence Functional_element_A, Functional_element_B, ...\n"
                      f"- show sequence Functional_interface\n")
    return plantuml_string


def case_state_diagram(**kwargs):
    """Case for 'show state <functional_element>'"""
    plantuml_string = None
    xml_fun_elem_name_list = get_objects_names(kwargs['xml_fun_elem_list'])
    if kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        plantuml_string = show_fun_elem_state_machine(kwargs['diagram_object_str'],
                                                      kwargs['xml_state_list'],
                                                      kwargs['xml_transition_list'],
                                                      kwargs['xml_fun_elem_list'])
    else:
        print(f"Jarvis does not know the functional Element {kwargs['diagram_object_str']}")

    return plantuml_string


def case_state_sequence_diagram(**kwargs):
    """Case for 'show state sequence <state>'"""
    plantuml_string = None
    xml_state_name_list = get_objects_names(kwargs['xml_state_list'])
    if kwargs['diagram_object_str'] in xml_state_name_list:
        plantuml_string = show_state_allocated_function(kwargs['diagram_object_str'],
                                                        kwargs['xml_state_list'],
                                                        kwargs['xml_function_list'],
                                                        kwargs['xml_consumer_function_list'],
                                                        kwargs['xml_producer_function_list'],
                                                        kwargs['xml_data_list'])
        return plantuml_string
    else:
        print(f"Jarvis does not know the State {kwargs['diagram_object_str']}")

    return plantuml_string


def case_no_diagram(**kwargs):
    """Default Case when no command has been found"""
    print(f"Jarvis does not understand the command {kwargs['diagram_type_str']}")


def check_level_0_allocated_child(fun_elem, function):
    """Returns True if the function can be "shown" by the functional element (i.e. no function
    children allocated to fun_elem children => TODO: Clean 2 above methods"""
    check = False
    if fun_elem.child_list == set():
        check = True
        return check
    if function.child_list == set() and function.parent.id not in fun_elem.allocated_function_list:
        check = True
        return check

    allocated_function_id_list = []
    for fun_elem_child in fun_elem.child_list:
        for elem in fun_elem_child.allocated_function_list:
            allocated_function_id_list.append(elem)
    child_list, _ = get_children(function)
    child_id_list = [elem.id for elem in child_list]
    if any(t in child_id_list for t in allocated_function_id_list) or not child_id_list:
        check = False
        return check

    if function.parent is not None:
        if function.parent.id not in fun_elem.allocated_function_list:
            check = True
            return check
    else:
        check = True

    return check


def get_level_0_function(fun_elem, function_list, allocated_function_list=None):
    """Recursively get functions allocated to main_fun_elem and its descendant"""
    if allocated_function_list is None:
        allocated_function_list = set()
        if fun_elem.child_list == set():
            return allocated_function_list
    for function_id in fun_elem.allocated_function_list:
        for function in function_list:
            if function.id == function_id and function not in allocated_function_list:
                if check_level_0_allocated_child(fun_elem, function) is True:
                    allocated_function_list.add(function)
                if fun_elem.child_list != set():
                    for child in fun_elem.child_list:
                        get_level_0_function(child, function_list, allocated_function_list)

    return allocated_function_list


def show_fun_elem_decomposition(fun_elem_str, xml_function_list, xml_consumer_function_list,
                                xml_producer_function_list, xml_fun_elem_list, xml_attribute_list,
                                xml_data_list, xml_fun_inter_list, diagram_level=None):
    """Creates lists with desired objects for <functional_element> decomposition, send them to
    plantuml_adapter.py then returns plantuml_text"""
    plantuml_text = None
    main_fun_elem = check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
    if not main_fun_elem:
        return plantuml_text
    main_fun_elem.parent = None

    c_inheritance = childs_inheritance(xml_function_list, xml_fun_elem_list, level=diagram_level)
    attrib_inheritance = attribute_inheritance(xml_attribute_list,
                                               xml_function_list,
                                               xml_fun_elem_list,
                                               xml_fun_inter_list)
    print([[elem.name, elem.allocated_function_list] for elem in xml_fun_elem_list])
    alloc_inheritance = allocation_inheritance(xml_fun_elem_list, xml_function_list)
    print([[elem.name, elem.allocated_function_list] for elem in xml_fun_elem_list])

    if diagram_level:
        xml_function_list, xml_fun_elem_list = filter_fun_elem_with_level(main_fun_elem,
                                                                          diagram_level,
                                                                          xml_function_list,
                                                                          xml_fun_elem_list)

    allocated_function_list = get_level_0_function(main_fun_elem, xml_function_list)

    if allocated_function_list:
        external_function_list, new_consumer_list, new_producer_list = \
            get_cons_prod_from_allocated_functions(
                allocated_function_list,
                xml_producer_function_list,
                xml_consumer_function_list)

        for fun in external_function_list:
            for child in fun.child_list.copy():
                if not any(t == child for t in external_function_list):
                    fun.child_list.remove(child)
    else:
        external_function_list, xml_fun_elem_list = set(), set()
        new_consumer_list, new_producer_list = [], []

    plantuml_text = plantuml_adapter.get_fun_elem_decomposition(main_fun_elem, xml_fun_elem_list,
                                                                allocated_function_list,
                                                                new_consumer_list,
                                                                new_producer_list,
                                                                external_function_list,
                                                                xml_attribute_list,
                                                                xml_data_list,
                                                                xml_fun_inter_list)

    reset_childs_inheritance(xml_function_list, xml_fun_elem_list, derived_child_id=c_inheritance[2])
    reset_attribute_inheritance(xml_attribute_list, attrib_inheritance)
    #reset_alloc_inheritance(alloc_inheritance)
    print([[elem.name, elem.allocated_function_list] for elem in xml_fun_elem_list])

    print(f"Decomposition Diagram for {fun_elem_str} generated")
    return plantuml_text


def filter_fun_elem_with_level(main_fun_elem, diagram_level, xml_function_list, xml_fun_elem_list):
    """Clean unwanted fun_elem and functions from xml_lists then returns them"""
    main_fun_elem_list, _ = get_children(main_fun_elem, level=diagram_level)
    # Remove (child) elements from xml lists that are below the level asked
    for unwanted_fun_elem in xml_fun_elem_list.symmetric_difference(main_fun_elem_list):
        if not check_not_family(unwanted_fun_elem, main_fun_elem):
            for fun in xml_function_list.copy():
                if fun.id in unwanted_fun_elem.allocated_function_list:
                    xml_function_list.remove(fun)
            xml_fun_elem_list.remove(unwanted_fun_elem)
    # Remove (child) elements from external fun_elem (main_fun_elem point of view)
    for unwanted_fun_elem in xml_fun_elem_list.symmetric_difference(main_fun_elem_list):
        if check_not_family(unwanted_fun_elem, main_fun_elem) and \
                unwanted_fun_elem.parent is None:
            curr_fun_elem_list, _ = get_children(unwanted_fun_elem, level=diagram_level)
            for un_fun_elem in xml_fun_elem_list.symmetric_difference(curr_fun_elem_list):
                if not check_not_family(unwanted_fun_elem, un_fun_elem):
                    xml_fun_elem_list.remove(un_fun_elem)

    return xml_function_list, xml_fun_elem_list


def get_cons_prod_from_allocated_functions(allocated_function_list,
                                           xml_producer_function_list,
                                           xml_consumer_function_list):
    """Get consumers/producers from function's allocated to main_fun_elem (and its descendant)"""
    new_producer_list = []
    new_consumer_list = []
    for allocated_function in allocated_function_list:
        allocated_function.child_list.clear()
        allocated_function.parent = None
        for elem in xml_producer_function_list:
            if allocated_function in elem:
                new_producer_list.append(elem)
        for elem in xml_consumer_function_list:
            if allocated_function in elem:
                new_consumer_list.append(elem)

    external_function_list, new_consumer_list, new_producer_list = get_ext_cons_prod(
        new_producer_list,
        new_consumer_list,
        xml_producer_function_list,
        xml_consumer_function_list)

    return external_function_list, new_consumer_list, new_producer_list


def get_ext_cons_prod(producer_list, consumer_list, xml_producer_function_list,
                      xml_consumer_function_list):
    """Get external cons/prod associated to main_fun_elem allocated functions"""
    external_function_list = set()
    for elem in consumer_list:
        if not any(elem[0] in s for s in producer_list):
            for prod in xml_producer_function_list:
                if prod[0] == elem[0] and prod[1].parent is None:
                    external_function_list.add(prod[1])
                    if prod not in producer_list:
                        producer_list.append(prod)

    for elem in producer_list:
        if not any(elem[0] in s for s in consumer_list):
            for cons in xml_consumer_function_list:
                if cons[0] == elem[0] and cons[1].parent is None:
                    external_function_list.add(cons[1])
                    if cons not in consumer_list:
                        consumer_list.append(cons)

    return external_function_list, consumer_list, producer_list


def show_state_allocated_function(state_str, state_list, function_list, xml_consumer_function_list,
                                  xml_producer_function_list, xml_data_list):
    """Creates lists with desired objects for <state> function's allocation, send them to
    plantuml_adapter.py then returns plantuml_text"""
    allocated_function_id_list = set()
    state_name = ''
    for state in state_list:
        if state_str in (state.name, state.alias):
            if not state.allocated_function_list:
                print(f"No function allocated to {state.name} (no display)")
                return None
            state_name = state.name
            for fun_id in state.allocated_function_list:
                allocated_function_id_list.add(fun_id)
    for function in function_list:
        if function.id in allocated_function_id_list.copy():
            allocated_function_id_list.remove(function.id)
            allocated_function_id_list.add(function.name)

    diagram_str = show_functions_sequence(allocated_function_id_list, function_list,
                                          xml_consumer_function_list, xml_producer_function_list,
                                          xml_data_list, True)

    diagram_str = f'box "{state_name}"\n{diagram_str}end box\n'
    print(f"Function Sequence Diagram for {state_str} generated")
    return diagram_str


def show_fun_elem_function(fun_elem_str, xml_fun_elem_list, xml_function_list,
                           xml_consumer_function_list, xml_producer_function_list, xml_type_list):
    """Creates lists with desired objects for <functional_element> function's allocation,
    send them to plantuml_adapter.py then returns plantuml_text"""
    plantuml_text = None

    main_fun_elem = check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
    if not main_fun_elem:
        return plantuml_text

    if not main_fun_elem.allocated_function_list:
        print(f"No function allocated to {main_fun_elem.name} (no display)")
        return plantuml_text

    main_fun_elem.parent = None
    main_fun_elem.child_list.clear()
    new_function_list = {f for f in xml_function_list
                         if f.id in main_fun_elem.allocated_function_list and f.parent is None}
    if not new_function_list:
        print(f"No parent function allocated to {main_fun_elem.name} (no display)")
        return plantuml_text

    new_consumer_list = get_cons_or_prod_paired(new_function_list,
                                                xml_consumer_function_list,
                                                xml_producer_function_list)

    new_producer_list = get_cons_or_prod_paired(new_function_list,
                                                xml_producer_function_list,
                                                xml_consumer_function_list)

    plantuml_text = plantuml_adapter.get_function_diagrams(new_function_list,
                                                           new_consumer_list,
                                                           new_producer_list,
                                                           {}, None, xml_type_list)

    print(f"Function Diagram for {fun_elem_str} generated")
    return plantuml_text


def get_cons_or_prod_paired(function_list, xml_flow_list, xml_opposite_flow_list):
    """Get flow list if opposite flow is existing: e.g. if flow A is consumed and produced by
    function within function_list => Add it"""
    new_flow_list = []
    for func in function_list:
        # Flow = [Data_name, Function]
        for flow in xml_flow_list:
            if func in flow and flow not in new_flow_list:
                # Oppo = [Data_name, Function]
                for oppo in xml_opposite_flow_list:
                    if oppo[0] == flow[0] and oppo[1] in function_list:
                        new_flow_list.append(flow)
                        break
    return new_flow_list


def show_fun_elem_context(fun_elem_str, xml_fun_elem_list, xml_function_list,
                          xml_consumer_function_list, xml_producer_function_list,
                          xml_attribute_list, xml_fun_inter_list, xml_data_list):
    """Creates lists with desired objects for <functional_element> context, send them to
    plantuml_adapter.py then returns plantuml_text"""

    main_fun_elem = check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
    if not main_fun_elem:
        return None

    # Get allocated function to main_fun_elem
    allocated_function_list = {f for f in xml_function_list
                               if f.id in main_fun_elem.allocated_function_list}

    new_function_list, cons, prod = get_allocated_function_context_lists(
        allocated_function_list,
        xml_consumer_function_list,
        xml_producer_function_list)

    fun_elem_list, interface_list, fun_elem_inter_list = get_fun_inter_for_fun_elem_context(
        main_fun_elem, xml_fun_inter_list, xml_fun_elem_list)

    for fun in new_function_list:
        for elem in xml_fun_elem_list:
            if any(z == fun.id for z in elem.allocated_function_list) and elem not in fun_elem_list:
                fun_elem_list.add(elem)

    for elem in fun_elem_list.copy():
        for str_id in elem.allocated_function_list.copy():
            if str_id not in [i.id for i in new_function_list]:
                elem.allocated_function_list.remove(str_id)
        if any(a == elem for a in main_fun_elem.child_list):
            fun_elem_list.remove(elem)

    plantuml_text = plantuml_adapter.get_fun_elem_context_diagram(new_function_list,
                                                                  cons,
                                                                  prod,
                                                                  xml_data_list,
                                                                  xml_attribute_list,
                                                                  fun_elem_list,
                                                                  interface_list,
                                                                  fun_elem_inter_list)
    print(f"Context Diagram for {fun_elem_str} generated")
    return plantuml_text


def get_allocated_function_context_lists(allocated_function_list,
                                         xml_consumer_function_list,
                                         xml_producer_function_list):
    """For each function within allocated_function_list, asks the context of the function then
    adds returned list from show_function_context() to current lists"""
    new_function_list = set()
    cons = []
    prod = []
    for fun in allocated_function_list:
        if fun.parent is None:
            returned_list = show_function_context(fun.name, allocated_function_list,
                                                  xml_consumer_function_list,
                                                  xml_producer_function_list, set(),
                                                  set(), set(), list_out=True)
            for k in returned_list[0]:
                new_function_list.add(k)
            for i in returned_list[1]:
                if i not in cons:
                    cons.append(i)
            for j in returned_list[2]:
                if j not in prod:
                    prod.append(j)

    return new_function_list, cons, prod


def get_fun_inter_for_fun_elem_context(main_fun_elem, xml_fun_inter_list, xml_fun_elem_list):
    """Get functional interfaces and associated functional elements"""
    fun_elem_list = set()
    interface_list = set()
    fun_elem_inter_list = []

    # Add main_fun_elem to filtered fun_elem_list and remove it from xml_fun_elem_list
    fun_elem_list.add(main_fun_elem)
    xml_fun_elem_list.remove(main_fun_elem)

    # Get exposed interfaces of fun_elem
    for interface in xml_fun_inter_list:
        if any(i == interface.id for i in main_fun_elem.exposed_interface_list):
            interface_list.add(interface)

    # Get fun_elem pair for fun_inter
    for fun_inter in interface_list:
        for fun_elem in xml_fun_elem_list:
            if any(i == fun_inter.id for i in fun_elem.exposed_interface_list):
                if get_highest_fun_elem_exposing_fun_inter(fun_inter, fun_elem) and \
                        check_not_family(main_fun_elem, fun_elem):
                    fun_elem_list.add(fun_elem)
                    if [main_fun_elem, fun_elem, fun_inter] not in fun_elem_inter_list:
                        fun_elem_inter_list.append([main_fun_elem, fun_elem, fun_inter])

    return fun_elem_list, interface_list, fun_elem_inter_list


def get_highest_fun_elem_exposing_fun_inter(fun_inter, fun_elem):
    """Retruns True if it's highest fun_elem exposing fun_inter"""
    check = False
    if not fun_elem.parent:
        check = True
    elif not any(a == fun_inter.id for a in fun_elem.parent.exposed_interface_list):
        check = True

    return check


def show_fun_elem_state_machine(fun_elem_str, xml_state_list, xml_transition_list,
                                xml_fun_elem_list):
    """Creates lists with desired objects for <functional_element> state, send them to
    plantuml_adapter.py then returns plantuml_text"""
    new_fun_elem_list = set()

    main_fun_elem = check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
    if not main_fun_elem:
        return None
    if not main_fun_elem.allocated_state_list:
        print(f"No state allocated to {main_fun_elem.name} (no display)")
        return None

    new_fun_elem_list.add(main_fun_elem)

    new_state_list = {s for s in xml_state_list if s.id in main_fun_elem.allocated_state_list}

    new_transition_list = get_transitions(new_state_list, xml_transition_list)

    plantuml_text = plantuml_adapter.get_state_machine_diagram(new_state_list,
                                                               new_transition_list,
                                                               xml_fun_elem_list)
    print(f"State Machine Diagram for {fun_elem_str} generated")
    return plantuml_text


def get_transitions(state_list, xml_transition_list):
    """Get transitions if state(s) from state_list are source/destination"""
    new_transition_list = set()
    for new_state in state_list:
        for transition in xml_transition_list:
            if new_state.id == transition.source:
                new_transition_list.add(transition)
            if new_state.id == transition.destination:
                new_transition_list.add(transition)

    return new_transition_list


def show_states_chain(state_list_str, xml_state_list, xml_transition_list):
    """Creates lists with desired objects for <states> chain, send them to plantuml_adapter.py
    then returns plantuml_text"""
    new_state_list = set()
    for state_str in state_list_str:
        for state in xml_state_list:
            if state_str in (state.name, state.alias):
                state.child_list.clear()
                state.set_parent(None)
                new_state_list.add(state)

    new_transition_list = get_transitions(new_state_list, xml_transition_list)

    plantuml_text = plantuml_adapter.get_state_machine_diagram(new_state_list,
                                                               new_transition_list)
    spaced_state_list = ", ".join(state_list_str)
    if len(state_list_str) == 1:
        print(f"Context Diagram {str(spaced_state_list)} generated")
    else:
        print(f"Chain Diagram {str(spaced_state_list)} generated")
    return plantuml_text


def show_functions_sequence(function_list_str, xml_function_list, xml_consumer_function_list,
                            xml_producer_function_list, xml_data_list, str_out=False):
    """Creates lists with desired objects for <functions> sequence, send them to plantuml_adapter.py
    then returns plantuml_text"""
    new_function_list = set()

    for i in function_list_str:
        fun = check_get_object(i, **{'xml_function_list': xml_function_list})
        if not fun:
            continue
        fun.child_list.clear()
        new_function_list.add(fun)

    new_consumer_list = get_cons_or_prod_paired(new_function_list,
                                                xml_consumer_function_list,
                                                xml_producer_function_list)

    new_producer_list = get_cons_or_prod_paired(new_function_list,
                                                xml_producer_function_list,
                                                xml_consumer_function_list)
    # (Re)Filter data_list with only produced(same data in consumed since paired) and functions
    # asked for sequence i.e. new_function_list used in get_cons_or_prod_paired()
    # => TBC/TBT
    new_data_list = {s for s in xml_data_list if any(s.name in j for j in new_producer_list)}

    for new_data in new_data_list:
        for pred in new_data.predecessor_list.copy():
            if pred not in new_data_list:
                new_data.predecessor_list.remove(pred)

    plantuml_text = plantuml_adapter.get_sequence_diagram(new_function_list,
                                                          new_consumer_list,
                                                          new_producer_list,
                                                          {},
                                                          new_data_list, str_out)
    if not str_out:
        print("Sequence Diagram " + str(", ".join(function_list_str)) + " generated")

    return plantuml_text


def show_functions_chain(function_list_str, xml_function_list, xml_consumer_function_list,
                         xml_producer_function_list, xml_type_list):
    new_function_list = set()
    new_parent_dict = {}
    new_producer_list = []
    new_consumer_list = []
    for i in function_list_str:
        for fun in xml_function_list:
            if i == fun.name or i == fun.alias:
                new_function_list.add(fun)
                if fun.parent:
                    new_parent_dict[fun.id] = fun.parent.id
                    if fun.parent not in new_function_list:
                        new_function_list.add(fun.parent)
                        fun.parent.child_list.clear()
                    fun.parent.add_child(fun)
                for xml_consumer_flow, xml_consumer in xml_consumer_function_list:
                    if fun == xml_consumer:
                        fun.child_list.clear()
                        if [xml_consumer_flow, fun] not in new_consumer_list and \
                                [xml_consumer_flow, fun] not in xml_producer_function_list:
                            new_consumer_list.append([xml_consumer_flow, fun])
                for xml_producer_flow, xml_producer in xml_producer_function_list:
                    if fun == xml_producer:
                        fun.child_list.clear()
                        if [xml_producer_flow, fun] not in new_producer_list and \
                                [xml_producer_flow, fun] not in xml_consumer_function_list:
                            new_producer_list.append([xml_producer_flow, fun])

    plantuml_text = plantuml_adapter.get_function_diagrams(new_function_list,
                                                           new_consumer_list,
                                                           new_producer_list,
                                                           new_parent_dict,
                                                           None,
                                                           xml_type_list)

    print(f'Chain Diagram {str(", ".join(function_list_str))} generated')
    return plantuml_text


# TODO: Clean-up once inheritance has been validated (Create method for Function and others
#  objects?)
def show_function_decomposition(diagram_function_str, xml_function_list, xml_consumer_function_list,
                                xml_producer_function_list, xml_attribute_list, xml_type_list,
                                diagram_level=None):
    """Create necessary lists then returns plantuml text for decomposition of function"""
    main_fun = check_get_object(diagram_function_str, **{'xml_function_list': xml_function_list})
    if not main_fun:
        return
    main_parent = main_fun.parent

    c_inheritance = childs_inheritance(xml_function_list, level=diagram_level)
    a_inheritance = attribute_inheritance(xml_attribute_list, xml_function_list)

    if diagram_level:
        full_fun_list, _ = get_children(main_fun)
        main_function_list, main_parent_dict = get_children(main_fun, level=diagram_level)
        # derived = childs_inheritance(main_fun, level=diagram_level)
        # if derived:
        #     main_function_list = main_function_list.union(derived[0])
        #     main_parent_dict.update(derived[1])

        for k in full_fun_list.symmetric_difference(main_function_list):
            for cons in xml_consumer_function_list.copy():
                if k in cons:
                    xml_consumer_function_list.remove(cons)

            for prod in xml_producer_function_list.copy():
                if k in prod:
                    xml_producer_function_list.remove(prod)
    else:
        main_function_list, main_parent_dict = get_children(main_fun)
        # derived = childs_inheritance(main_fun)
        # if derived:
        #     main_function_list = main_function_list.union(derived[0])
        #     main_parent_dict.update(derived[1])

    main_consumer_list = check_get_child_flows(main_function_list, xml_consumer_function_list)
    main_producer_list = check_get_child_flows(main_function_list, xml_producer_function_list)

    ext_prod_fun_list, ext_producer_list, ext_prod_parent_dict = get_external_flow_with_level(
        main_consumer_list, main_function_list, main_fun, xml_producer_function_list, diagram_level)

    ext_cons_fun_list, ext_consumer_list, ext_cons_parent_dict = get_external_flow_with_level(
        main_producer_list, main_function_list, main_fun, xml_consumer_function_list, diagram_level)

    new_function_list = main_function_list.union(ext_prod_fun_list).union(ext_cons_fun_list)
    new_consumer_list = main_consumer_list + ext_consumer_list
    new_producer_list = main_producer_list + ext_producer_list
    new_parent_dict = {**main_parent_dict, **ext_cons_parent_dict, **ext_prod_parent_dict}

    for function in new_function_list:
        if main_parent and function.parent is main_parent:
            function.parent = None
        if function.child_list:
            for j in function.child_list.copy():
                if j not in new_function_list:
                    function.child_list.remove(j)

    plantuml_text = plantuml_adapter.get_function_diagrams(new_function_list,
                                                           new_consumer_list,
                                                           new_producer_list,
                                                           new_parent_dict,
                                                           None,
                                                           xml_type_list,
                                                           xml_attribute_list=xml_attribute_list)

    reset_childs_inheritance(xml_function_list, derived_child_id=c_inheritance[2])
    reset_attribute_inheritance(xml_attribute_list, a_inheritance)

    print(f"Decomposition Diagram {diagram_function_str} generated")
    return plantuml_text


def get_external_flow_with_level(main_flow_list, main_function_list, main_fun, xml_flow_list,
                                 level):
    """Returns external functions list, flow lists and parent dict"""
    ext_flow_fun_list = set()
    ext_flow_list = []
    ext_flow_parent_dict = {}
    for flow, _ in main_flow_list:
        for xml_flow, xml_fun in xml_flow_list:
            if flow == xml_flow and xml_fun.parent == main_fun.parent:
                ext_flow_fun_list.add(xml_fun)
            elif flow == xml_flow and check_not_family(main_fun, xml_fun) and \
                    xml_fun.parent is None:
                ext_flow_fun_list.add(xml_fun)
            elif flow == xml_flow and not check_parentality(xml_fun, main_fun) and \
                    [xml_flow, xml_fun.parent] not in xml_flow_list:
                ext_flow_fun_list.add(xml_fun)

    for fun in ext_flow_fun_list.copy():
        if fun.child_list:
            function_list_dict = get_children(fun, level=level)
            ext_flow_fun_list.update(function_list_dict[0])
            ext_flow_parent_dict.update(function_list_dict[1])

    for flow, _ in main_flow_list:
        for xml_flow, xml_fun in xml_flow_list:
            if flow == xml_flow and xml_fun in ext_flow_fun_list and \
                    xml_fun not in main_function_list:
                # ext_flow_list.append([xml_flow, xml_fun])
                if not xml_fun.child_list:
                    if [xml_flow, xml_fun] not in ext_flow_list:
                        ext_flow_list.append([xml_flow, xml_fun])
                else:
                    temp = []
                    for k in xml_fun.child_list:
                        temp.append([xml_flow, k])
                    if not any(t in temp for t in xml_flow_list):
                        if [xml_flow, xml_fun] not in ext_flow_list:
                            ext_flow_list.append([xml_flow, xml_fun])

    for fun in ext_flow_fun_list.copy():
        if not any(a == fun for a in [i[1] for i in ext_flow_list]) and not fun.child_list:
            ext_flow_fun_list.remove(fun)
    for fun in ext_flow_fun_list.copy():
        if not any(a == fun for a in [i[1] for i in ext_flow_list]) and \
                not any(i in fun.child_list for i in ext_flow_fun_list) and \
                fun != main_fun:
            ext_flow_fun_list.remove(fun)

    return ext_flow_fun_list, ext_flow_list, ext_flow_parent_dict


def check_get_child_flows(function_list, xml_flow_list, new_flow_list=None):
    """Get flow_list associated with function_list and xml_flow_list"""
    if new_flow_list is None:
        new_flow_list = []
    for f in function_list:
        for xml_flow, xml_function in xml_flow_list:
            if f == xml_function:
                if not xml_function.child_list:
                    if [xml_flow, xml_function] not in new_flow_list:
                        new_flow_list.append([xml_flow, xml_function])
                else:
                    temp_list = []
                    for c in xml_function.child_list:
                        if [xml_flow, c] in xml_flow_list:
                            temp_list.append([xml_flow, c])

                    if not any(xml_flow in s for s in temp_list):
                        if [xml_flow, xml_function] not in new_flow_list:
                            new_flow_list.append([xml_flow, xml_function])

    return new_flow_list


def show_function_context(diagram_function_str, xml_function_list, xml_consumer_function_list,
                          xml_producer_function_list, xml_data_list, xml_attribute_list,
                          xml_type_list, list_out=False):
    """Create necessary lists then returns plantuml text for context of function"""
    new_function_list = set()
    new_parent_dict = {}
    new_producer_list = []
    new_consumer_list = []
    main = None

    c_inheritance = childs_inheritance(xml_function_list)
    a_inheritance = attribute_inheritance(xml_attribute_list, xml_function_list)

    for fun in xml_function_list:
        if diagram_function_str in (fun.name, fun.alias):
            new_function_list.add(fun)
            main = fun
            for xml_producer_flow, xml_producer in xml_producer_function_list:
                if fun == xml_producer:
                    check = False
                    for flow, consumer in xml_consumer_function_list:
                        if xml_producer_flow == flow:
                            if consumer.parent is None:
                                current_func, current_dict = get_children(fun)
                                parent_check = check_parentality(consumer, main)
                                if consumer not in current_func and parent_check is False:
                                    new_consumer_list.append([xml_producer_flow, consumer])
                                    new_function_list.add(consumer)
                                    check = True
                            elif main.parent == consumer.parent and consumer != main:
                                new_consumer_list.append([flow, consumer])
                                new_function_list.add(consumer)
                                check = True
                    if check:
                        if [xml_producer_flow, xml_producer] not in new_producer_list:
                            new_producer_list.append([xml_producer_flow, xml_producer])

                    if not any(xml_producer_flow in s for s in xml_consumer_function_list):
                        if [xml_producer_flow, xml_producer] not in new_producer_list:
                            new_producer_list.append([xml_producer_flow, xml_producer])

    if main is not None:
        for xml_consumer_flow, xml_consumer in xml_consumer_function_list:
            if xml_consumer == main:
                check = False
                for flow, producer in xml_producer_function_list:
                    if flow == xml_consumer_flow:
                        if producer.parent is None:
                            current_func, current_dict = get_children(producer)
                            if main not in current_func:
                                new_producer_list.append([flow, producer])
                                new_function_list.add(producer)
                                check = True
                        elif main.parent == producer.parent and producer != main:
                            new_producer_list.append([flow, producer])
                            new_function_list.add(producer)
                            check = True
                if check:
                    if [xml_consumer_flow, xml_consumer] not in new_consumer_list:
                        new_consumer_list.append([xml_consumer_flow, xml_consumer])

                if not any(xml_consumer_flow in s for s in xml_producer_function_list):
                    if [xml_consumer_flow, xml_consumer] not in new_consumer_list:
                        new_consumer_list.append([xml_consumer_flow, xml_consumer])

    for f in new_function_list:
        f.child_list.clear()

    if list_out:
        out = new_function_list, new_consumer_list, new_producer_list
    else:
        plantuml_text = plantuml_adapter.get_function_diagrams(
            new_function_list,
            new_consumer_list,
            new_producer_list,
            new_parent_dict,
            xml_data_list,
            xml_type_list,
            xml_attribute_list=xml_attribute_list)

        out = plantuml_text
        print(f"Context Diagram {diagram_function_str} generated")

    reset_childs_inheritance(xml_function_list, derived_child_id=c_inheritance[2])
    reset_attribute_inheritance(xml_attribute_list, a_inheritance)

    return out


def get_fun_inter_sequence_diagram(fun_inter_str, **kwargs):
    """
    Check and get all "show sequence Fun_inter" strings, find Fun_inter obj and then get/filter
    needed lists for plantuml_adapter.
    Args:
        fun_inter_str: functional interface name/alias from input cell
        **kwargs: whole lists

    Returns:
        plantuml_text (str) : plantuml text
    """
    new_consumer_list = []
    new_producer_list = []
    new_fun_elem_list = set()
    fun_inter = check_get_object(
        fun_inter_str, **{'xml_fun_inter_list': kwargs['xml_fun_inter_list']})

    if fun_inter:
        data_list_fun_inter = switch_data(fun_inter, None, **kwargs)['data']
        for elem in data_list_fun_inter:
            fun_elem_cons = check_get_object(
                elem['Last consumer Functional element(s)'].pop(),
                **{'xml_fun_elem_list': kwargs['xml_fun_elem_list']})
            fun_elem_prod = check_get_object(
                elem['Last producer Functional element(s)'].pop(),
                **{'xml_fun_elem_list': kwargs['xml_fun_elem_list']})
            if fun_elem_cons and fun_elem_prod:
                new_consumer_list.append([elem['Data'], fun_elem_cons])
                new_producer_list.append([elem['Data'], fun_elem_prod])
                new_fun_elem_list.add(fun_elem_cons)
                new_fun_elem_list.add(fun_elem_prod)

    if new_consumer_list and new_producer_list:
        plantuml_text = plantuml_adapter.get_sequence_diagram(new_fun_elem_list,
                                                              new_consumer_list,
                                                              new_producer_list,
                                                              {},
                                                              kwargs['xml_data_list'])

        return plantuml_text

    else:
        print(f"No data found for {fun_inter.name}")


def get_fun_elem_sequence_diagram(fun_elem_str, **kwargs):
    """
    Check and get all "show sequence Fun_elem_A, Fun_elem_B, ..." strings, find objects and
    then get/filter needed lists for plantuml_adapter.
    Args:
        fun_elem_str: functional elements name/alias from input cell
        **kwargs: whole lists

    Returns:
        plantuml_text (str) : plantuml_text
    """
    new_consumer_list = []
    new_producer_list = []
    global_interface_list = set()
    new_fun_elem_list = [check_get_object(i, **{'xml_fun_elem_list': kwargs['xml_fun_elem_list']})
                         for i in fun_elem_str]
    kwargs['xml_fun_elem_list'] = new_fun_elem_list
    for fun_elem in new_fun_elem_list:
        fun_elem.child_list.clear()
        fun_elem.parent = None
        global_interface_list.update(switch_fun_elem_interface(fun_elem, None, **kwargs)[1:])

    for item in global_interface_list:
        if any(n == item[1] for n in [f.name for f in new_fun_elem_list]):
            interface = check_get_object(
                item[0], **{'xml_fun_inter_list': kwargs['xml_fun_inter_list']})

            data_list_fun_inter = switch_data(interface, None, **kwargs)['data']
            if not data_list_fun_inter:
                print(f"No data allocated to {interface.name}")
            for elem in data_list_fun_inter:
                fun_elem_cons = check_get_object(
                    elem['Last consumer Functional element(s)'].pop(),
                    **{'xml_fun_elem_list': kwargs['xml_fun_elem_list']})
                fun_elem_prod = check_get_object(
                    elem['Last producer Functional element(s)'].pop(),
                    **{'xml_fun_elem_list': kwargs['xml_fun_elem_list']})
                if fun_elem_cons and fun_elem_prod:
                    if [elem['Data'], fun_elem_cons] not in new_consumer_list:
                        new_consumer_list.append([elem['Data'], fun_elem_cons])
                    if [elem['Data'], fun_elem_prod] not in new_producer_list:
                        new_producer_list.append([elem['Data'], fun_elem_prod])

    if new_consumer_list and new_producer_list:
        plantuml_text = plantuml_adapter.get_sequence_diagram(new_fun_elem_list,
                                                              new_consumer_list,
                                                              new_producer_list,
                                                              {},
                                                              kwargs['xml_data_list'])

        return plantuml_text

    else:
        print(f"Not any data allocated to interfaces exposed by {', '.join(fun_elem_str)}")


def filter_allocated_item_from_view(xml_item_list, xml_view_list):
    """For a type of item from xml, check if a View is activated and if the item is in its
    allocated item's list"""
    if not any(j.activated for j in xml_view_list):
        return xml_item_list

    filtered_items_list = []
    activated_view = ''
    for view in xml_view_list:
        if view.activated:
            activated_view = view.name
            for item in xml_item_list:
                if item.id in view.allocated_item_list:
                    filtered_items_list.append(item)

    if filtered_items_list:
        return filtered_items_list

    return f"View {activated_view} does not contain any elements"
