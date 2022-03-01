#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import inspect
import sys
import os
import tkinter as tk
import tkinter.filedialog

# Modules
from . import util
sys.path.append("../xml_adapter")
import xml_adapter # noqa
sys.path.append("../datamodel")
import datamodel # noqa


def write_function_child(function, input_flow_list, output_flow_list):
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

    plantuml_text += util.MakePlantUml.create_port(function_input_port, "in")
    plantuml_text += util.MakePlantUml.create_port(function_output_port, "out")
    plantuml_text += util.MakePlantUml.create_port(parent_function_port, "None")

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
            plantuml_text += util.MakePlantUml.create_object_with_operand(fun)
        else:
            plantuml_text += util.MakePlantUml.create_object(fun)

    for child in child_with_child_list:
        plantuml_text += util.MakePlantUml.create_component(child)
        plantuml_text += write_function_child(child, input_flow_list,
                                output_flow_list)
        nb_component -= 1

    # Close all the brackets depending on the number of component within highest parent
    for i in range(nb_component):
        plantuml_text += util.MakePlantUml.close_component()

    whole_child_list = child_with_child_list + child_with_no_child_list
    for fun in whole_child_list:
        for i in input_flow_list:
            if i[0][0] == fun.name.lower():
                plantuml_text += util.MakePlantUml.create_port(input_flow_list, "in")
        for j in output_flow_list:
            if j[0][0] == fun.name.lower():
                plantuml_text += util.MakePlantUml.create_port(output_flow_list, "out")

    plantuml_text += util.MakePlantUml.create_port(external_input_port, "in")
    plantuml_text += util.MakePlantUml.create_port(external_output_port, "out")

    return plantuml_text


# Method to count the number of composed function within the higher function
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


def write_function_object(function, input_flow_list, output_flow_list, check, compo_diagram=False):
    plantuml_text = ''
    if function.operand:
        plantuml_text += util.MakePlantUml.create_object_with_operand(function)
    else:
        plantuml_text += util.MakePlantUml.create_object(function)
    if check:
        plantuml_text += util.MakePlantUml.close_component()
    for p in input_flow_list:
        if compo_diagram:
            if p[0][0] == function.name.lower():
                plantuml_text += util.MakePlantUml.create_port(input_flow_list, "in")
        else:
            if p[0][0] == function.name.lower() or p[0][1] == function.name.lower():
                plantuml_text += util.MakePlantUml.create_port(input_flow_list, "in")
    for q in output_flow_list:
        if compo_diagram:
            if q[0][0] == function.name.lower():
                plantuml_text += util.MakePlantUml.create_port(output_flow_list, "out")
        else:
            if q[0][0] == function.name.lower() or q[0][1] == function.name.lower():
                plantuml_text += util.MakePlantUml.create_port(output_flow_list, "out")

    return plantuml_text


def plantuml_binder(function_list, consumer_function_list, producer_function_list,
                    parent_child_dict, data_list, fun_elem_list=None):
    plantuml_text = ""
    # Filter output flows
    output_flow_list = get_output_flows(consumer_function_list, producer_function_list)
    # Filter input flows
    input_flow_list = get_input_flows(consumer_function_list, producer_function_list)
    # Filter consumers and producers list in order to create data flow
    data_flow_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                         parent_child_dict, 1)
    if data_list:
        per_message_data_flow_list = get_exchanged_flows(consumer_function_list,
                                                         producer_function_list,
                                                         parent_child_dict, 0)
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
            check, fun_elem_txt = check_write_fun_elem(function, fun_elem_list)
            plantuml_text += fun_elem_txt
            plantuml_text += write_function_object(function, input_flow_list, output_flow_list,
                                                   check)

    if parent_child_dict:
        for function in function_list:
            if function.id in parent_child_dict.values() and \
                    function.id not in parent_child_dict.keys():
                if function.type in datamodel.FunctionType.get_parent_function_type_list():
                    check, fun_elem_txt = check_write_fun_elem(function, fun_elem_list)
                    plantuml_text += fun_elem_txt
                    plantuml_text += util.MakePlantUml.create_component(function)
                    plantuml_text += write_function_child(function,
                                                          input_flow_list,
                                                          output_flow_list)
                    if check:
                        plantuml_text += util.MakePlantUml.close_component()
            if function.id not in parent_child_dict.keys() \
                    and function.id not in parent_child_dict.values():
                check, fun_elem_txt = check_write_fun_elem(function, fun_elem_list)
                plantuml_text += fun_elem_txt
                plantuml_text += write_function_object(function, input_flow_list, output_flow_list,
                                                       check, True)
    # Write in output file and close it
    plantuml_text += util.MakePlantUml.create_input_flow(input_flow_list)
    plantuml_text += util.MakePlantUml.create_output_flow(output_flow_list)
    plantuml_text += util.MakePlantUml.create_data_flow(data_flow_list)

    diagram_url = util.MakePlantUml.get_url_from_local(plantuml_text)

    return plantuml_text, diagram_url


def check_child_allocation(fun_elem, function_list, out_str=None):
    """
    Check for each function allocated to fun_elem if not allocated to any fun_elem child: in that
    case => write function object string.

        Parameters:
            fun_elem (Functional Element) : Functional element to check
            function_list ([Function]) : Functions list
            out_str (string) : Current string
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
            if not any(t.id in s for s in child_allocated_function_list):
                out_str += write_function_object(t, [], [], False)
    return out_str


def recursive_decomposition(main_fun_elem, function_list, input_flow_list, output_flow_list,
                            out_str=None):
    if out_str is None:
        out_str = ''
        out_str += util.MakePlantUml.create_component(main_fun_elem)
        out_str += check_child_allocation(main_fun_elem, function_list)
        if main_fun_elem.child_list:
            out_str = recursive_decomposition(main_fun_elem, function_list,
                                              input_flow_list, output_flow_list, out_str)

    else:
        for c in main_fun_elem.child_list:
            out_str += util.MakePlantUml.create_component(c)
            out_str += check_child_allocation(c, function_list)
            if c.child_list:
                out_str = recursive_decomposition(c, function_list, input_flow_list,
                                                  output_flow_list,
                                                  out_str)
            out_str += util.MakePlantUml.close_component()

    return out_str


def get_fun_elem_decomposition(main_fun_elem, fun_elem_list, allocated_function_list, consumer_list,
                               producer_list, external_function_list):
    """
    Method that parsed input lists in order to create dedicated functional element decomposition
    diagram by: Creating the whole string plantuml_text, retrieve url and return it.

        Parameters:
            main_fun_elem (Functional Element) : Main functional element
            fun_elem_list ([Functional Element]) : Functional element list from xml parsing
            allocated_function_list ([Function]) : Allocated function list to Main functional Elem.
            consumer_list ([data_name, Function]) : Filtered consumers list
            producer_list ([data_name, Function]) : Filtered producers list
            external_function_list ([Function]) : Filtered external(i.e. "outside" Main) functions
                                                    list

        Returns:
            diagram_url (url_str) : Url can be local(big diagram) or hosted by plantuml server
    """
    # Filter output flows
    #output_flow_list = get_output_flows(consumer_list, producer_list)
    output_flow_list = []
    # Filter input flows
    #input_flow_list = get_input_flows(consumer_list, producer_list)
    input_flow_list = []
    # Filter consumers and producers list in order to create data flow
    data_flow_list = get_exchanged_flows(consumer_list, producer_list,
                                         {}, 1)
    # Write functional element decompo recursively and add allocated functions
    plantuml_text = recursive_decomposition(main_fun_elem, allocated_function_list,
                                            input_flow_list, output_flow_list)
    plantuml_text += util.MakePlantUml.close_component()
    # Write external(consumer or producer) functions and highest level functional
    # element allocated to it
    for function in external_function_list:
        check, fun_elem_txt = check_write_fun_elem(function, fun_elem_list)
        plantuml_text += fun_elem_txt
        plantuml_text += write_function_object(function, input_flow_list, output_flow_list,
                                               check)

    # Write data flows
    #plantuml_text += util.MakePlantUml.create_input_flow(input_flow_list)
    #plantuml_text += util.MakePlantUml.create_output_flow(output_flow_list)
    plantuml_text += util.MakePlantUml.create_data_flow(data_flow_list)
    #print(plantuml_text)
    diagram_url = util.MakePlantUml.get_url_from_local(plantuml_text)
    return diagram_url


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
    if fun_elem_list:
        for fun_elem in fun_elem_list:
            if function.id in fun_elem.allocated_function_list:
                if fun_elem.parent is None:
                    check = True
                    plantuml_text += util.MakePlantUml.create_component(fun_elem)
    return check, plantuml_text


def get_url_from_string(diagram_str):
    """
    Return diagram url from its string.
        Parameters:
            diagram_str (string) : Plantuml diagram string
        Returns:
            diagram_url (string) : Url can be local(big diagram) or hosted by plantuml server
    """
    diagram_url = util.MakePlantUml.get_url_from_local(diagram_str)
    return diagram_url


def get_sequence_diagram(function_list, consumer_function_list, producer_function_list,
                         parent_child_dict, data_list):
    # Allow plantuml option to put duration between 2 messages
    sequence_text = "!pragma teoz true\n"

    message_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                       parent_child_dict, 0)
    ordered_function_list, ordered_message_list = order_list(message_list, data_list)

    if ordered_function_list:
        for fun_name in ordered_function_list:
            for f in function_list:
                if fun_name == f.name.lower():
                    sequence_text += util.MakePlantUml.create_participant(f)
    else:
        for f in function_list:
            sequence_text += util.MakePlantUml.create_participant(f)

    sequence_text += util.MakePlantUml.create_sequence_message(ordered_message_list)
    diagram_url = util.MakePlantUml.get_url_from_local(sequence_text)

    return sequence_text, diagram_url


def get_predecessor_list(data):
    predecessor_list = set()
    if data.predecessor_list:
        for predecessor in data.predecessor_list:
            predecessor_list.add(predecessor)

    return predecessor_list


def check_sequence(predecessor_list, sequence):
    count = len(predecessor_list)
    check = False
    if not predecessor_list:
        return check
    for pred in predecessor_list:
        for elem in sequence:
            if pred in elem:
                count -= 1
    if count == 0:
        check = True
    return check


def clean_predecessor_list(message_object_list):

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


def get_sequence_list(message_object_list):
    sequence_list = get_sequences(message_object_list)

    sequence_list = sorted(sequence_list, key=lambda x: len(x), reverse=True)

    for (index, i) in enumerate(sequence_list):
        main_list = sequence_list[0]
        if index > 0:
            start = 0
            for j in i.copy():
                if not j[2].predecessor_list:
                    i.remove(j)
                    main_list.insert(start, j)
                    start += 1
                else:
                    for (idx, elem) in enumerate(main_list.copy()):
                        pred = get_predecessor_list(j[2])
                        next_pred = get_predecessor_list(main_list[idx][2])
                        next_check = check_sequence(next_pred, main_list[:idx-1])
                        if check_sequence(pred, main_list[:idx-1]) is True and j not in main_list and next_check is True:
                            i.remove(j)
                            main_list.insert(idx, j)
                            idx += 1

    sequence_list = [item for sub in sequence_list for item in sub]

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
                        concatenate_boolean):
    output_list = []
    for producer_flow, producer_function in producer_function_list:
        if len(producer_function.child_list) == 0:
            for cons_flow, consumer_function in consumer_function_list:
                if cons_flow == producer_flow:
                    if consumer_function.id in parent_child_dict.keys():
                        if len(consumer_function.child_list) == 0:
                            output_list.append(
                                [producer_function.name.lower(), consumer_function.name.lower(),
                                 producer_flow])
                    elif len(consumer_function.child_list) == 0:
                        output_list.append(
                            [producer_function.name.lower(), consumer_function.name.lower(),
                             producer_flow])

    if concatenate_boolean == 1:
        output_list = concatenate_flows(output_list)

    return output_list


def get_output_flows(consumer_function_list, producer_function_list):
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

    output_list = concatenate_flows(output_list)
    return output_list


def get_input_flows(consumer_function_list, producer_function_list):
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
                            state_machine_text += util.MakePlantUml.create_state(fun_elem, True)

            state_machine_text += write_composed_state(state, already_added_state_id_list,
                                                       objects_conditions_list)
            if check:
                state_machine_text += util.MakePlantUml.close_component()

    for s in xml_state_list:
        if s.id not in already_added_state_id_list:
            check = False
            if fun_elem_list:
                for fun_elem in fun_elem_list:
                    if s.id in fun_elem.allocated_state_list:
                        if fun_elem.parent is None:
                            check = True
                            state_machine_text += util.MakePlantUml.create_state(fun_elem, True)
            state_machine_text += write_state(s, already_added_state_id_list,
                                              objects_conditions_list)
            if check:
                state_machine_text += util.MakePlantUml.close_component()

    for p in objects_conditions_list:
        if (p[0].id and not p[1].id) or (not p[0].id and p[1].id):
            state_machine_text += util.MakePlantUml.create_transition([p])
            objects_conditions_list.remove(p)

    diagram_url = util.MakePlantUml.get_url_from_local(state_machine_text)

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
        output_str += util.MakePlantUml.create_state(state)
        new.append(state.id)

    for j in objects_conditions_list:
        if all(x in new for x in [j[0].id, j[1].id]):
            output_str += util.MakePlantUml.create_transition([j])
            objects_conditions_list.remove(j)

    return output_str


def write_composed_state(state, new, objects_conditions_list, output_str='', count=0):
    output_str += util.MakePlantUml.create_state(state, parent=True)
    new.insert(count, state.id)
    count += 1
    for i in state.child_list:
        if not i.child_list:
            output_str += util.MakePlantUml.create_state(i)
            new.insert(count+1, i.id)
        else:
            return write_composed_state(i, new, objects_conditions_list, output_str, count)

    for j in objects_conditions_list:
        if all(x in new for x in [j[0].id, j[1].id]):
            output_str += util.MakePlantUml.create_transition([j])
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
