#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import inspect
import sys

# Modules
from .util import MakePlantUml
sys.path.append("../xml_adapter")
import xml_adapter # noqa
sys.path.append("../datamodel")
import datamodel # noqa
sys.path.append("../jarvis")
from jarvis import question_answer # noqa


def write_function_child(function, input_flow_list, output_flow_list, xml_attribute_list):
    function_input_port = []
    function_output_port = []
    external_input_port = []
    external_output_port = []
    parent_function_port = []
    plantuml_text = ""
    count = 1
    nb_component = count_composed_component(function, count)

    for p in input_flow_list:
        if p[0][0] == function.name.lower():
            function_input_port.append(p)
        if p[0][0] is None:
            external_input_port.append(p)
            if p[0][1] == function.name.lower():
                parent_function_port.append(p)

    for q in output_flow_list:
        if q[0][0] == function.name.lower():
            function_output_port.append(q)
        if q[0][0] is None:
            external_output_port.append(q)
            if q[0][1] == function.name.lower():
                parent_function_port.append(q)

    plantuml_text += MakePlantUml.create_port(function_input_port, "in")
    plantuml_text += MakePlantUml.create_port(function_output_port, "out")
    plantuml_text += MakePlantUml.create_port(parent_function_port, "None")

    child_with_no_child_list = []
    child_with_child_list = []
    # Create a child list for each parent function
    for child_function in function.child_list:
        if child_function.child_list:
            child_with_child_list.append(child_function)
        if not child_function.child_list:
            child_with_no_child_list.append(child_function)

    # For child that has no child: create object
    for fun in child_with_no_child_list:
        if fun.operand:
            plantuml_text += MakePlantUml.create_object_with_operand(fun, xml_attribute_list)
        else:
            plantuml_text += MakePlantUml.create_object(fun, xml_attribute_list)

    for child in child_with_child_list:
        plantuml_text += MakePlantUml.create_component(child)
        plantuml_text += write_function_child(child, input_flow_list,
                                              output_flow_list, xml_attribute_list)
        nb_component -= 1

    # Close all the brackets depending on the number of component within highest parent
    for i in range(nb_component):
        plantuml_text += MakePlantUml.close_component()

    for component in child_with_child_list:
        plantuml_text += MakePlantUml.create_component_attribute(component, xml_attribute_list)

    whole_child_list = child_with_child_list + child_with_no_child_list
    for fun in whole_child_list:
        for i in input_flow_list:
            if i[0][0] == fun.name.lower():
                plantuml_text += MakePlantUml.create_port(input_flow_list, "in")
        for j in output_flow_list:
            if j[0][0] == fun.name.lower():
                plantuml_text += MakePlantUml.create_port(output_flow_list, "out")

    plantuml_text += MakePlantUml.create_port(external_input_port, "in")
    plantuml_text += MakePlantUml.create_port(external_output_port, "out")

    return plantuml_text


def count_composed_component(function, count):
    """
    Count the number of composed function within the higher function
        Parameters:
            function (Function) : Function to check
            count (int) : Number of component
        Returns:
            count (int) : Number of component
    """
    for elem in function.child_list:
        if len(elem.child_list) > 0:
            count += 1
            count_composed_component(elem, count)
            continue
    return count


def write_function_object(function, input_flow_list, output_flow_list, check, xml_attribute_list,
                          component_obj=None, compo_diagram=False):
    plantuml_text = ''
    if function.operand:
        plantuml_text += MakePlantUml.create_object_with_operand(function, xml_attribute_list)
    else:
        plantuml_text += MakePlantUml.create_object(function, xml_attribute_list)

    if check:
        plantuml_text += MakePlantUml.close_component()
        if component_obj:
            plantuml_text += MakePlantUml.create_component_attribute(component_obj,
                                                                     xml_attribute_list)

    for p in input_flow_list:
        if compo_diagram:
            if p[0][0] == function.name.lower():
                plantuml_text += MakePlantUml.create_port(input_flow_list, "in")
        else:
            if p[0][0] == function.name.lower() or p[0][1] == function.name.lower():
                plantuml_text += MakePlantUml.create_port(input_flow_list, "in")
    for q in output_flow_list:
        if compo_diagram:
            if q[0][0] == function.name.lower():
                plantuml_text += MakePlantUml.create_port(output_flow_list, "out")
        else:
            if q[0][0] == function.name.lower() or q[0][1] == function.name.lower():
                plantuml_text += MakePlantUml.create_port(output_flow_list, "out")

    return plantuml_text


def get_function_diagrams(function_list, consumer_function_list, producer_function_list,
                          parent_child_dict, data_list, xml_attribute_list=None):
    plantuml_text = ""
    interface_list = None

    # Filter output flows
    output_flow_list = get_output_flows(consumer_function_list, producer_function_list,
                                        concatenate=True)
    # Filter input flows
    input_flow_list = get_input_flows(consumer_function_list, producer_function_list,
                                      concatenate=True)
    # Filter consumers and producers list in order to create data flow
    data_flow_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                         parent_child_dict, concatenate=True)

    if data_list:
        per_message_data_flow_list = get_exchanged_flows(consumer_function_list,
                                                         producer_function_list,
                                                         parent_child_dict)
        if len(data_list) == len(per_message_data_flow_list):
            ordered_function_list, ordered_message_list = order_list(per_message_data_flow_list,
                                                                     data_list)
            if per_message_data_flow_list != ordered_message_list:
                for idx, i in enumerate(ordered_message_list):
                    for j in data_flow_list:
                        for k in j[1]:
                            if i[2] == k and i[3]:
                                new = str(idx+1) + ":" + k
                                j[1].remove(k)
                                j[1].append(new)

    # Loop in order to filter functions and write in output's file, see write_function_child()
    if not parent_child_dict:
        for function in function_list:
            plantuml_text += write_function_object(function, input_flow_list,
                                                   output_flow_list, False,
                                                   xml_attribute_list)

    if parent_child_dict:
        for function in function_list:
            if function.id in parent_child_dict.values() and \
                    function.id not in parent_child_dict.keys():
                if function.type in datamodel.FunctionType.get_parent_function_type_list():

                    plantuml_text += MakePlantUml.create_component(function)
                    plantuml_text += write_function_child(function,
                                                          input_flow_list,
                                                          output_flow_list,
                                                          xml_attribute_list)

            if function.id not in parent_child_dict.keys() \
                    and function.id not in parent_child_dict.values():
                plantuml_text += write_function_object(function, input_flow_list, output_flow_list,
                                                       False, xml_attribute_list,
                                                       compo_diagram=True)

    plantuml_text += MakePlantUml.create_input_flow(input_flow_list)
    plantuml_text += MakePlantUml.create_output_flow(output_flow_list)
    plantuml_text += MakePlantUml.create_data_flow(data_flow_list)

    if interface_list:
        plantuml_text += MakePlantUml.create_interface(interface_list)

    diagram_url = MakePlantUml.get_url_from_local(plantuml_text)

    return plantuml_text, diagram_url


def get_fun_elem_context_diagram(function_list, consumer_function_list, producer_function_list,
                                 data_list, xml_attribute_list, fun_elem_list, fun_inter_list,
                                 fun_elem_inter_list):

    plantuml_text = ""

    if fun_inter_list:

        unmerged_data_list = get_exchanged_flows(consumer_function_list, producer_function_list, {})
        interface_list, data_flow_list = get_interface_list(fun_inter_list,
                                                            data_list,
                                                            unmerged_data_list,
                                                            function_list,
                                                            fun_elem_list)

        data_flow_list = concatenate_flows(data_flow_list)

    else:

        # Filter consumers and producers list in order to create data flow
        data_flow_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                             {}, concatenate=True)

    # Filter output flows
    output_flow_list = get_output_flows(consumer_function_list, producer_function_list,
                                        concatenate=True)
    # Filter input flows
    input_flow_list = get_input_flows(consumer_function_list, producer_function_list,
                                      concatenate=True)

    for fun_elem in fun_elem_list:
        plantuml_text += MakePlantUml.create_component(fun_elem)
        check_function = False
        for f in function_list:
            if any(a == f.id for a in fun_elem.allocated_function_list):
                if len(fun_elem.allocated_function_list) > 1:
                    check_function = False
                else:
                    check_function = True
                plantuml_text += write_function_object(f, input_flow_list,
                                                       output_flow_list, check_function,
                                                       xml_attribute_list, component_obj=fun_elem)
        if not check_function:
            plantuml_text += MakePlantUml.close_component()
            plantuml_text += MakePlantUml.create_component_attribute(fun_elem,
                                                                     xml_attribute_list)
    plantuml_text += MakePlantUml.create_input_flow(input_flow_list)
    plantuml_text += MakePlantUml.create_output_flow(output_flow_list)
    plantuml_text += MakePlantUml.create_data_flow(data_flow_list)

    if fun_elem_inter_list:
        plantuml_text += MakePlantUml.create_interface(fun_elem_inter_list)

    diagram_url = MakePlantUml.get_url_from_local(plantuml_text)

    return plantuml_text, diagram_url


def get_interface_list(fun_inter_list, data_list, data_flow_list, function_list, fun_elem_list):
    """Get [fun_elem_1, fun_elem_2, fun_inter] when data allocated to fun_inter
    and pop according data from data_flow_list"""
    interface_list = []
    removed_data_flow_list = []
    initial_data = list(data_flow_list)
    idx = 0
    # Get all fun_inter with allocated data within data_flow_list and create interface list
    # [[producer, consumer, fun_inter]...]
    for fun_inter in fun_inter_list:
        for data_id in fun_inter.allocated_data_list:
            for data in data_list:
                if data_id == data.id:
                    for elem in data_flow_list.copy():
                        if data.name == elem[2]:
                            first = None
                            second = None
                            for fun in function_list:
                                if elem[0] == fun.name.lower():
                                    first = fun
                                if elem[1] == fun.name.lower():
                                    second = fun
                            if not (not first and not second):
                                # if not any(fun_inter in s for s in interface_list):
                                interface_list.insert(idx, [first, second, fun_inter])
                                removed_data_flow_list.insert(idx, elem)
                                data_flow_list.remove(elem)
                                idx += 1

    output_list, interface_list = get_fun_elem_from_fun_inter(interface_list, fun_elem_list)

    if not output_list:
        return None, initial_data
    else:
        # (re)Add [producer, consumer, data_name] to data_flow_list if no interface exposed
        if any(isinstance(s, list) for s in interface_list):
            for idx, rest_inter in enumerate(interface_list):
                if isinstance(rest_inter, list):
                    data_flow_list.append(removed_data_flow_list[idx])

        return output_list, data_flow_list


def get_fun_elem_from_fun_inter(interface_list, fun_elem_list):
    """Get output_list = [[fun_elem_1, fun_elem_2, fun_inter]...] list from interface_list =
    [[producer, consumer, fun_inter]...] and put value to False if (first, second, interface)
    have been added to output_list (i.e. fun_elem_1/fun_elem_2 have been found for a fun_inter)"""
    output_list = []
    for ix, (first, second, interface) in enumerate(interface_list):
        fun_elem_1 = None
        fun_elem_2 = None
        if first:
            for elem_1 in fun_elem_list:
                if any(s == interface.id for s in elem_1.exposed_interface_list):
                    if not elem_1.child_list:
                        fun_elem_1 = elem_1
                    else:
                        check = True
                        for child in elem_1.child_list:
                            if any(s == interface.id for s in child.exposed_interface_list):
                                check = False
                        if check:
                            fun_elem_1 = elem_1

        if second:
            for elem_2 in fun_elem_list:
                if not first:
                    if any(s == interface.id for s in elem_2.exposed_interface_list):
                        if not elem_2.child_list:
                            fun_elem_2 = elem_2
                        else:
                            check = True
                            for child in elem_2.child_list:
                                if any(s == interface.id for s in child.exposed_interface_list):
                                    check = False
                            if check:
                                fun_elem_2 = elem_2
                else:
                    if any(s == interface.id for s in elem_2.exposed_interface_list) and \
                            elem_2 != fun_elem_1:
                        if not elem_2.child_list:
                            fun_elem_2 = elem_2
                        else:
                            check = True
                            for child in elem_2.child_list:
                                if any(s == interface.id for s in child.exposed_interface_list):
                                    check = False

                            if check:
                                fun_elem_2 = elem_2

        if not (not fun_elem_1 and not fun_elem_2):
            if [fun_elem_1, fun_elem_2, interface] not in output_list:
                output_list.append([fun_elem_1, fun_elem_2, interface])
            interface_list[ix] = False

    return output_list, interface_list


def check_child_allocation(fun_elem, function_list, xml_attribute_list, out_str=None):
    """
    Check for each function allocated to fun_elem if not allocated to any fun_elem child: in that
    case => write function object string.

        Parameters:
            fun_elem (Functional Element) : Functional element to check
            function_list ([Function]) : Functions list
            out_str (string) : Current string
            xml_attribute_list ([Attributes]) : Xml list of attributes
        Returns:
            out_str (string) : Function object(s) string
    """
    if not out_str:
        out_str = ''
    for t in function_list:
        if t.id in fun_elem.allocated_function_list:
            child_allocated_function_list = []
            for c in fun_elem.child_list:
                for j in c.allocated_function_list:
                    child_allocated_function_list.append(j)
            if not any(s == t.id for s in child_allocated_function_list):
                out_str += write_function_object(t, [], [], False, xml_attribute_list)

    return out_str


def recursive_decomposition(main_fun_elem, function_list, xml_attribute_list, out_str=None):
    """ Creates Functional Elements as plantuml 'component' recursively """
    if out_str is None:
        out_str = ''
        out_str += MakePlantUml.create_component(main_fun_elem)
        out_str += check_child_allocation(main_fun_elem, function_list, xml_attribute_list)
        if main_fun_elem.child_list:
            out_str = recursive_decomposition(main_fun_elem, function_list, xml_attribute_list,
                                              out_str)
    else:
        for c in main_fun_elem.child_list:
            out_str += MakePlantUml.create_component(c)
            out_str += check_child_allocation(c, function_list, xml_attribute_list)
            if c.child_list:
                out_str = recursive_decomposition(c, function_list, xml_attribute_list, out_str)
            out_str += MakePlantUml.close_component()
            out_str += MakePlantUml.create_component_attribute(c, xml_attribute_list)
        out_str += MakePlantUml.create_component_attribute(main_fun_elem, xml_attribute_list)
    return out_str


def get_fun_elem_decomposition(main_fun_elem, fun_elem_list, allocated_function_list, consumer_list,
                               producer_list, external_function_list, xml_attribute_list,
                               data_list, fun_inter_list):
    """
    Parses input lists in order to create dedicated functional element decomposition
    diagram by: Creating the whole string plantuml_text, retrieve url and return it.

        Parameters:
            main_fun_elem (Functional Element) : Main functional element
            fun_elem_list ([Functional Element]) : Functional element list from xml parsing
            allocated_function_list ([Function]) : Allocated function list to Main functional Elem.
            consumer_list ([data_name, Function]) : Filtered consumers list
            producer_list ([data_name, Function]) : Filtered producers list
            external_function_list ([Function]) : Filtered external(i.e. "outside" Main) functions
                                                    list
            xml_attribute_list ([Attributes]) : Xml list of attributes
            data_list ([Data]) : Data list from xml
            fun_inter_list ([Functional Interface]) : Functional interface list from xml
        Returns:
            diagram_url (url_str) : Url can be local(big diagram) or visible via plantuml server
    """
    interface_list = None

    if fun_inter_list:
        unmerged_data_list = get_exchanged_flows(consumer_list, producer_list, {})
        interface_list, data_flow_list = get_interface_list(fun_inter_list,
                                                            data_list,
                                                            unmerged_data_list,
                                                            allocated_function_list.
                                                            union(external_function_list),
                                                            fun_elem_list)

        data_flow_list = concatenate_flows(data_flow_list)

    else:
        # Filter consumers and producers list in order to create data flow
        data_flow_list = get_exchanged_flows(consumer_list, producer_list, {}, concatenate=True)

    # Write functional element decompo recursively and add allocated functions
    plantuml_text = recursive_decomposition(main_fun_elem, allocated_function_list,
                                            xml_attribute_list)
    plantuml_text += MakePlantUml.close_component()
    plantuml_text += MakePlantUml.create_component_attribute(main_fun_elem, xml_attribute_list)
    # Write external(consumer or producer) functions and highest level functional
    # element allocated to it
    for function in external_function_list:
        check, fun_elem_txt, fun_elem = check_write_fun_elem(function, fun_elem_list)
        plantuml_text += fun_elem_txt
        plantuml_text += write_function_object(function, [], [], check,
                                               xml_attribute_list, component_obj=fun_elem)

    # Write data flows
    plantuml_text += MakePlantUml.create_data_flow(data_flow_list)
    if interface_list:
        plantuml_text += MakePlantUml.create_interface(interface_list)

    diagram_url = MakePlantUml.get_url_from_local(plantuml_text)

    return diagram_url, plantuml_text


def check_write_fun_elem(function, fun_elem_list):
    """
    Check if "function" is alloacted to a functional element. If allocated, returns new component
    string with functional element and check = True (used later on to close component bracket)

        Parameters:
            function (Function) : Function to check
            fun_elem_list ([Functional Element]) : Functional element list from xml parsing
        Returns:
            check (Bool) : True if function is allocated to a highest level(i.e. no parent)
                            Fun. Elem.
            plantuml_text (string) : Functional Element string for plantuml
    """
    plantuml_text = ''
    check = False
    fun_elem = None
    if fun_elem_list:
        for fun_elem in fun_elem_list:
            if function.id in fun_elem.allocated_function_list:
                if fun_elem.parent is None:
                    check = True
                    plantuml_text += MakePlantUml.create_component(fun_elem)
    return check, plantuml_text, fun_elem


def get_url_from_string(diagram_str):
    """
    Return diagram url from its string.
        Parameters:
            diagram_str (string) : Plantuml diagram string
        Returns:
            diagram_url (string) : Url can be local(big diagram) or hosted by plantuml server
    """
    diagram_url = MakePlantUml.get_url_from_local(diagram_str)
    return diagram_url


def get_sequence_diagram(function_list, consumer_function_list, producer_function_list,
                         parent_child_dict, data_list, str_out=False):
    """ Generates plantuml string and url for sequence diagrams """
    # Allow plantuml option to put duration between 2 messages
    sequence_text = "!pragma teoz true\n"

    message_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                       parent_child_dict)
    ordered_function_list, ordered_message_list = order_list(message_list, data_list)

    if ordered_function_list:
        for fun_name in ordered_function_list:
            for f in function_list:
                if fun_name == f.name.lower():
                    sequence_text += MakePlantUml.create_participant(f)
    else:
        for f in function_list:
            sequence_text += MakePlantUml.create_participant(f)

    sequence_text += MakePlantUml.create_sequence_message(ordered_message_list)

    if str_out:
        return sequence_text, ''
    else:
        diagram_url = MakePlantUml.get_url_from_local(sequence_text)
        return sequence_text, diagram_url


def get_predecessor_list(data):
    """ Get the predecessor's list for a Data object"""
    predecessor_list = set()
    if data.predecessor_list:
        for predecessor in data.predecessor_list:
            predecessor_list.add(predecessor)

    return predecessor_list


def check_sequence(predecessor_list, sequence):
    """ Checks if predecessors are in the sequence"""
    check = False
    if predecessor_list == set():
        check = None
        return check
    else:
        pred_set = set()
        seq_set = set()
        for pred in predecessor_list:
            pred_set.add(pred.name)
        for elem in sequence:
            seq_set.add(elem[2].name)
        if pred_set.issubset(seq_set):
            check = True
            return check
        else:
            return check


def clean_predecessor_list(message_object_list):
    """ Deletes predecessor if not in the message's list """
    for message in message_object_list:
        pred_list = get_predecessor_list(message[2])
        for pred in pred_list:
            if not any(pred in s for s in message_object_list):
                message[2].predecessor_list.remove(pred)

    return message_object_list


def get_sequence(message, message_object_list, sequence_list, sequence=None, index=None):
    if not sequence:
        sequence = []
        index = 0
    if message not in sequence and not any(message in s for s in sequence_list) is True:
        message[3] = True
        sequence.insert(index, message)
        index += 1
        for mess in message_object_list:
            if message[2] in mess[2].predecessor_list:
                get_sequence(mess, message_object_list, sequence_list, sequence, index)

    return sequence


def get_sequences(message_object_list):
    sequence_list = []
    for message in message_object_list:
        if not message[2].predecessor_list:
            sequence = get_sequence(message, message_object_list, sequence_list)
            sequence_list.append(sequence)

    return sequence_list


def post_check_sequence(sequence_list):

    for (idx, i) in enumerate(sequence_list):
        pred = i[2].predecessor_list
        if check_sequence(pred, sequence_list[:idx]) is True:
            pass
        elif check_sequence(pred, sequence_list[:idx]) is False:
            for (index, elem) in enumerate(sequence_list.copy()):
                curr_pred = elem[2].predecessor_list
                if check_sequence(curr_pred, sequence_list[:index]) is True:
                    sequence_list.remove(i)
                    sequence_list.insert(index+1, i)
                    index += 1
                else:
                    continue
        elif check_sequence(pred, sequence_list[:idx]) is None:
            pass
        idx += 1

    for (new_idx, message) in enumerate(sequence_list):
        new_pred = message[2].predecessor_list
        if check_sequence(new_pred, sequence_list[:new_idx]) is False:
            post_check_sequence(sequence_list)

    return sequence_list


def get_sequence_list(message_object_list):
    sequence_list = get_sequences(message_object_list)

    sequence_list = sorted(sequence_list, key=lambda x: len(x), reverse=True)
    # Could be possible ot implement this part within post_check_sequence()
    for (index, i) in enumerate(sequence_list):
        main_list = sequence_list[0]
        if index > 0:
            start = 0
            for j in i.copy():
                if not j[2].predecessor_list:
                    i.remove(j)
                    main_list.insert(start, j)
                    start += 1

    sequence_list = [item for sub in sequence_list for item in sub]
    sequence_list = post_check_sequence(sequence_list)

    return sequence_list


def order_list(message_list, data_list):
    ordered_message_list = []
    ordered_function_list = []
    message_object_list = []

    for i in message_list:
        for data in data_list:
            if i[2] == data.name:
                message_object_list.append([i[0], i[1], data, False])

    message_object_list = clean_predecessor_list(message_object_list)
    ordored_message_object_list = get_sequence_list(message_object_list)

    # Add index for each item within the list
    for idx, t in enumerate(ordored_message_object_list):
        ordered_message_list.insert(idx, [t[0], t[1], t[2].name, t[3]])

    # Create the ordered(from ordered message list) function's list
    # Starting with producers
    for idx, m in enumerate(ordered_message_list):
        if m[0] not in ordered_function_list:
            ordered_function_list.insert(idx, m[0])
    # Finishing with consumers
    for j in message_list:
        if j[1] not in ordered_function_list:
            ordered_function_list.append(j[1])

    return ordered_function_list, ordered_message_list


def get_exchanged_flows(consumer_function_list, producer_function_list, parent_child_dict,
                        concatenate=False):
    output_list = []

    for producer_flow, producer_function in producer_function_list:
        if not producer_function.child_list:
            for cons_flow, consumer_function in consumer_function_list:
                if cons_flow == producer_flow:
                    if consumer_function.id in parent_child_dict.keys() \
                            and not consumer_function.child_list:
                        output_list.append(
                            [producer_function.name.lower(), consumer_function.name.lower(),
                             producer_flow])
                    elif not consumer_function.child_list:
                        output_list.append(
                            [producer_function.name.lower(), consumer_function.name.lower(),
                             producer_flow])

    if concatenate:
        output_list = concatenate_flows(output_list)

    return output_list


def get_output_flows(consumer_function_list, producer_function_list, concatenate=False):
    flow_consumer_name_list = []
    flow_child_consumer_list = []
    temp_input_list = []
    output_list = []

    for flow, cons in consumer_function_list:
        flow_consumer_name_list.append([flow, cons.name.lower()])
        if cons.child_list is not None:
            for child in cons.child_list:
                flow_child = [flow, child.name.lower()]
                if [flow, child] in consumer_function_list:
                    flow_child_consumer_list.append(flow_child)

    for consumer_flow, consumer_function in consumer_function_list:
        if len(consumer_function.child_list) > 0:
            if len(flow_child_consumer_list) > 0:
                if not any(consumer_flow in sublist for sublist in flow_child_consumer_list):
                    temp_input_list.append([consumer_function.name.lower(), consumer_flow])
            if len(flow_child_consumer_list) == 0:
                temp_input_list.append([consumer_function.name.lower(), consumer_flow])

    for producer_flow, producer_function in producer_function_list:
        for name, flow in temp_input_list:
            if producer_flow == flow:
                flow_child_consumer_list = [name, producer_function.name.lower(), producer_flow]
                output_list.append(flow_child_consumer_list)
        # Looking for outputs (i.e. flow with only producer's function)
        if not any(producer_flow in sublist for sublist in flow_consumer_name_list):
            if not any(producer_flow in sub for sub in output_list):
                output_list.append([None, producer_function.name.lower(), producer_flow])

    if concatenate:
        output_list = concatenate_flows(output_list)
    return output_list


def get_input_flows(consumer_function_list, producer_function_list, concatenate=False):
    flow_producer_name_list = []
    flow_child_producer_list = []
    temp_input_list = []
    output_list = []

    for flow, prod in producer_function_list:
        flow_producer_name_list.append([flow, prod.name.lower()])
        if prod.child_list is not None:
            for child in prod.child_list:
                flow_child = [flow, child.name.lower()]
                if [flow, child] in producer_function_list:
                    flow_child_producer_list.append(flow_child)

    for producer_flow, producer_function in producer_function_list:
        if len(producer_function.child_list) > 0:
            if len(flow_child_producer_list) > 0:
                if not any(producer_flow in sublist for sublist in flow_child_producer_list):
                    temp_input_list.append([producer_function.name.lower(), producer_flow])
            if len(flow_child_producer_list) == 0:
                temp_input_list.append([producer_function.name.lower(), producer_flow])

    for cons_flow, consumer_fun in consumer_function_list:
        for name, flow in temp_input_list:
            if cons_flow == flow:
                flow_child_producer_list = [name, consumer_fun.name.lower(), cons_flow]
                output_list.append(flow_child_producer_list)
        if not any(cons_flow in sublist for sublist in flow_producer_name_list):
            if not any(cons_flow in sublist for sublist in output_list):
                output_list.append([None, consumer_fun.name.lower(), cons_flow])

    if concatenate:
        output_list = concatenate_flows(output_list)
    return output_list


# Concatenate with same consumer and producer the flows :
# from [[cons=A, prod=B, flow_1], [cons=A, prod=B, flow_2]] to
# [[cons=A, prod=B, [flow_1, flow_2]]. Adaptation for flow notation in plantuml
def concatenate_flows(input_list):
    output_list = []
    per_function_name_filtered_list = set(map(lambda x: (x[0], x[1]), input_list))
    per_flow_filtered_list = [[y[2] for y in input_list if y[0] == x and y[1] == z] for x, z in
                              per_function_name_filtered_list]
    for idx, function in enumerate(per_function_name_filtered_list):
        output_list.append([function, per_flow_filtered_list[idx]])

    return output_list


def get_state_machine_diagram(xml_state_list, xml_transition_list, fun_elem_list=None):

    state_machine_text = inspect.cleandoc("""skinparam useBetaStyle true
                                            hide empty description
                                            <style>
                                                 .Entry{
                                                    FontColor white
                                                    BackgroundColor black
                                                 }
                                                 .Exit{
                                                    FontColor white
                                                    BackgroundColor black
                                                 }
                                            </style>""") + "\n"

    objects_conditions_list = get_objects_conditions_list(xml_state_list, xml_transition_list)
    already_added_state_id_list = []
    for state in xml_state_list:
        if not state.parent and state.child_list:
            check = False
            if fun_elem_list:
                for fun_elem in fun_elem_list:
                    if state.id in fun_elem.allocated_state_list:
                        if fun_elem.parent is None:
                            check = True
                            state_machine_text += MakePlantUml.create_state(fun_elem, True)

            state_machine_text += write_composed_state(state, already_added_state_id_list,
                                                       objects_conditions_list)
            if check:
                state_machine_text += MakePlantUml.close_component()

    for s in xml_state_list:
        if s.id not in already_added_state_id_list:
            check = False
            if fun_elem_list:
                for fun_elem in fun_elem_list:
                    if s.id in fun_elem.allocated_state_list:
                        if fun_elem.parent is None:
                            check = True
                            state_machine_text += MakePlantUml.create_state(fun_elem, True)
            state_machine_text += write_state(s, already_added_state_id_list,
                                              objects_conditions_list)
            if check:
                state_machine_text += MakePlantUml.close_component()

    for p in objects_conditions_list:
        if (p[0].id and not p[1].id) or (not p[0].id and p[1].id):
            state_machine_text += MakePlantUml.create_transition([p])
            objects_conditions_list.remove(p)

    diagram_url = MakePlantUml.get_url_from_local(state_machine_text)

    return state_machine_text, diagram_url


def get_objects_conditions_list(xml_state_list, xml_transition_list):
    objects_conditions_list = []
    formatted_transition_list = []
    # Create transition's list [src_id, dest_id, [conditions]]
    for i in xml_transition_list:
        formatted_transition_list.append([i.source, i.destination, i.condition_list])

    # Create transition's list [src_state_obj, dest_state_obj, [conditions]]
    for j in formatted_transition_list:
        result = match_transition_states(j, xml_state_list)
        if result:
            objects_conditions_list.append(result)

    return objects_conditions_list


def write_state(state, new, objects_conditions_list, output_str=''):

    if not state.parent and not state.child_list:
        output_str += MakePlantUml.create_state(state)
        new.append(state.id)

    for j in objects_conditions_list:
        if all(x in new for x in [j[0].id, j[1].id]):
            output_str += MakePlantUml.create_transition([j])
            objects_conditions_list.remove(j)

    return output_str


def write_composed_state(state, new, objects_conditions_list, output_str='', count=0):
    output_str += MakePlantUml.create_state(state, parent=True)
    new.insert(count, state.id)
    count += 1
    for i in state.child_list:
        if not i.child_list:
            output_str += MakePlantUml.create_state(i)
            new.insert(count+1, i.id)
        else:
            return write_composed_state(i, new, objects_conditions_list, output_str, count)

    for j in objects_conditions_list:
        if all(x in new for x in [j[0].id, j[1].id]):
            output_str += MakePlantUml.create_transition([j])
            objects_conditions_list.remove(j)

    output_str += "}\n"*count
    return output_str


def match_transition_states(transition, xml_state_list):
    source_state = None
    destination_state = None
    out = None
    for a in xml_state_list:
        if transition[0] == a.id:
            source_state = a
    for b in xml_state_list:
        if transition[1] == b.id:
            destination_state = b

    if source_state is not None and destination_state is not None:
        out = [source_state, destination_state, transition[2]]
    elif source_state is not None and destination_state is None:
        n = datamodel.State()
        n.set_type(datamodel.StateType.EXIT)
        n.set_name('EXIT')
        xml_state_list.add(n)
        out = [source_state, n, transition[2]]
    elif source_state is None and destination_state is not None:
        n = datamodel.State()
        n.set_type(datamodel.StateType.ENTRY)
        n.set_name('ENTRY')
        xml_state_list.add(n)
        out = [n, destination_state, transition[2]]

    return out
