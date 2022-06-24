#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module with methods relative to Functional section"""
# Libraries
import re
import uuid
# Modules
import datamodel
from . import shared_orchestrator
from .question_answer import get_objects_names, get_children, check_get_object, check_parentality


def create_function_obj(function_str, specific_obj_type, **kwargs):
    """
    Check if string function_str is not already corresponding to an actual object's name/alias,
    create new Function() object, instantiate it, add it to xml_function_list.

        Parameters:
            function_str (str) : Lists of string from jarvis cell
            specific_obj_type ([Function]) : specific type or None
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update (0/function) : function if update, else 0
    """
    if any(n == function_str for n in get_objects_names(kwargs['xml_function_list'])):
        return 0
    if not specific_obj_type:
        # Instantiate Function class and function
        function = datamodel.Function(p_name=function_str)
    else:
        # Instantiate Function
        function = datamodel.Function(p_name=function_str, p_type=specific_obj_type.name)

    alias_str = re.search(r"(.*)\s[-]\s", function_str, re.MULTILINE)
    if alias_str:
        function.set_alias(alias_str.group(1))
    function.set_id(shared_orchestrator.get_unique_id())
    # Add function to a set()
    kwargs['xml_function_list'].add(function)
    print(f"{function.name} is a {function.type}")
    if function:
        return function
    return 0


def create_data_obj(data_str, specific_obj_type, **kwargs):
    """
    Check if string data_str is not already corresponding to an actual object's name/alias,
    create new Data() object, instantiate it, add it to xml_data_list.

        Parameters:
            data_str (str) : Lists of string from jarvis cell
            specific_obj_type ([Function]) : specific type or None
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update (0/data) : data if update, else 0
    """
    if any(n == data_str for n in get_objects_names(kwargs['xml_data_list'])):
        return 0
    if not specific_obj_type:
        data = datamodel.Data(p_name=data_str)
    else:
        data = datamodel.Data(p_name=data_str, p_type=specific_obj_type.name)

    data.set_id(shared_orchestrator.get_unique_id())
    kwargs['xml_data_list'].add(data)
    print(f"{data.name} is a {data.type}")
    if data:
        return data
    return 0


def check_add_predecessor(data_predecessor_str_set, xml_data_list, xml_view_list, output_xml):
    """
    Check if each string in data_predecessor_str_set is corresponding to an actual Data object,
    create new [Data, predecessor] objects lists for object's type : Data.
    Send lists to add_predecessor() to write them within xml and then returns update_list from it.

        Parameters:
            data_predecessor_str_set ([str]) : Lists of string from jarvis cell
            xml_data_list ([Data]) : Data list from xml parsing
            xml_view_list ([View]) : View list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    data_predecessor_list = []

    allocated_item_list = []
    # Filter input string
    data_predecessor_str_list = shared_orchestrator.cut_string_list(data_predecessor_str_set)

    # Create data names list already in xml
    xml_data_name_list = get_objects_names(xml_data_list)

    for elem in data_predecessor_str_list:
        is_elem_found = True
        if elem[0] not in xml_data_name_list:
            is_elem_found = False
            if elem[1] not in xml_data_name_list:
                print(f"{elem[0]} and {elem[1]} do not exist")
            else:
                print(f"{elem[0]} does not exist")
        if elem[0] in xml_data_name_list:
            if elem[1] not in xml_data_name_list:
                is_elem_found = False
                print(f"{elem[1]} does not exist")

        if is_elem_found:
            predecessor = None
            selected_data = None
            existing_predecessor_id_list = []
            for data in xml_data_list:
                if elem[0] == data.name:
                    selected_data = data
                    for existing_predecessor in data.predecessor_list:
                        existing_predecessor_id_list.append(existing_predecessor.id)
            for da in xml_data_list:
                if elem[1] == da.name and da.id not in existing_predecessor_id_list:
                    predecessor = da
            if predecessor is not None and selected_data is not None:
                data_predecessor_list.append([selected_data, predecessor])
            allocation_chain_1 = shared_orchestrator.check_add_allocated_item(elem[0],
                                                                              xml_data_list,
                                                                              xml_view_list)
            if allocation_chain_1:
                allocated_item_list.append(allocation_chain_1)
            allocation_chain_2 = shared_orchestrator.check_add_allocated_item(elem[1],
                                                                              xml_data_list,
                                                                              xml_view_list)
            if allocation_chain_2:
                allocated_item_list.append(allocation_chain_2)

    update = add_predecessor(data_predecessor_list, xml_data_list, output_xml)
    shared_orchestrator.add_allocation({5: allocated_item_list}, output_xml)

    return update


def add_predecessor(predecessor_list, xml_data_list, output_xml):
    """
    Check if input lists is not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            predecessor_list ([Data, Data(predecessor)]) : Data object to set new predessor and
            predecessor Data
            xml_data_list ([Data]) : Data list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """

    if not predecessor_list:
        return 0

    output_xml.write_predecessor(predecessor_list)
    # Warn the user once added within xml
    for data_predecessor in predecessor_list:
        for d in xml_data_list:
            if data_predecessor[0].id == d.id:
                d.add_predecessor(data_predecessor[1])
                print(f"{data_predecessor[1].name} predecessor for "
                      f"{data_predecessor[0].name}")
    return 1


def check_add_consumer_function(consumer_str_list, xml_consumer_function_list,
                                xml_producer_function_list, xml_function_list, xml_data_list,
                                output_xml):
    """
    Check if each string in consumer_str_list are corresponding to an actual object, create new
    [data, consumer] objects list for object's type : Function.
    Send lists to add_consumer_function() to write them within xml and then returns update_list
    from it.

        Parameters:
            consumer_str_list ([str]) : Lists of string from jarvis cell
            xml_consumer_function_list ([Data_name_str, Function]) : Data's name and consumer's
            function list from xml
            xml_producer_function_list ([Data_name_str, Function]) : Data's name and producer's
            function list from xml
            xml_function_list ([Function]) : Function list from xml parsing
            xml_data_list ([Data]) : Data list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    new_consumer_list = []
    # Create object names/aliases list and data's name
    xml_function_name_list = get_objects_names(xml_function_list)
    xml_data_name_list = get_objects_names(xml_data_list)
    # Loop to filter consumer and create a new list
    for elem in consumer_str_list:
        is_elem_found = True
        if not any(item == elem[1] for item in xml_function_name_list) and \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            print(f"{elem[1]} and {elem[0]} do not exist")
        elif not any(item == elem[1] for item in xml_function_name_list) or \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            if any(item == elem[1] for item in xml_function_name_list) and \
                    not any(item == elem[0] for item in xml_data_name_list):
                print(f"{elem[0]} does not exist")
            elif any(item == elem[0] for item in xml_data_name_list) and \
                    not any(item == elem[1] for item in xml_function_name_list):
                print(f"{elem[1]} does not exist")

        if is_elem_found:
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if elem[1] == function.name or elem[1] == function.alias:
                    if [elem[0], function] not in xml_consumer_function_list:
                        if [elem[0], function] not in xml_producer_function_list:
                            new_consumer_list.append([elem[0], function])
                            parent = add_parent_recursively(elem[0], function,
                                                            xml_consumer_function_list,
                                                            xml_producer_function_list,
                                                            new_consumer_list,
                                                            output_xml, "consumer")

                            if parent is not None:
                                for par in parent:
                                    if par:
                                        new_consumer_list.append(par)
                        elif [elem[0], function] in xml_producer_function_list:
                            pass

    update = add_consumer_function(new_consumer_list, xml_consumer_function_list, output_xml)

    return update


def add_consumer_function(new_consumer_list, xml_consumer_function_list, output_xml):
    """
    Check if input list is not empty, write in xml for each element and return update list if some
    updates has been made

        Parameters:
            new_consumer_list ([Data_name_str, Function]) : Data's name and consumer's function list
            xml_consumer_function_list ([Data_name_str, Function]) : Data's name and consumer's
            function list from xml
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """

    if not new_consumer_list:
        return 0

    output_xml.write_consumer(new_consumer_list)
    # Warn the user once added within xml
    for consumer in new_consumer_list:
        xml_consumer_function_list.append(consumer)
        print(f"{consumer[1].name} consumes {consumer[0]}")

    return 1


def add_parent_recursively(flow, function, current_list, opposite_list, new_list, output_xml,
                           relationship_str, out=False):
    """
    Recursive method around add_parent_for_data().
        Parameters:
            flow (Data_name_str) : Data's name
            function (Function) : Current function's parent
            current_list ([Data_name_str, function_name_str]) : 'Current' list (producer/consumer)
            opposite_list ([Data_name_str, function_name_str]) : Opposite list from current
            new_list ([Data_name_str, Function]) : Data's name and consumer/producer's function list
            output_xml (GenerateXML object) : XML's file object
            relationship_str (str) : "consumer" or "producer"
            out (bool) : List for recursivity
        Returns:
            elem ([data, Function]) : Return parent

    """
    if not out:
        out = []
    parent = add_parent_for_data(flow, function,
                                 current_list,
                                 opposite_list,
                                 new_list,
                                 output_xml, relationship_str)

    if parent is not None:
        out.append(parent)
        return add_parent_recursively(flow, function.parent, current_list, opposite_list, new_list,
                                      output_xml,
                                      relationship_str, out)

    return out


def add_parent_for_data(flow, function, current_list, opposite_list, new_list, output_xml,
                        relationship_str):
    """
    Adds direct parent's function of consumer/producer and delete internal flow if the case

        Parameters:
            flow (Data_name_str) : Data's name
            function (Function) : Current function's parent
            current_list ([Data_name_str, function_name_str]) : 'Current' list (producer/consumer)
            opposite_list ([Data_name_str, function_name_str]) : Opposite list from current
            new_list ([Data_name_str, Function]) : Data's name and consumer/producer's function list
            output_xml (GenerateXML object) : XML's file object
            relationship_str (str) : "consumer" or "producer"
        Returns:
            elem ([data, Function]) : Return parent
    """
    elem = [flow, function.parent]
    temp_set = set()
    check = False

    if function.parent is not None and elem not in [*current_list, *new_list]:
        parent_child_list, parent_child_dict = get_children(function.parent)

        current_loop_check = False
        for current_loop_data in [*current_list, *new_list]:
            if current_loop_data[0] == flow and current_loop_data[1] not in parent_child_list:
                current_loop_check = True
        for data_function in opposite_list:
            if data_function[0] == flow:
                temp_set.add(data_function[1])
        length = len(temp_set)
        if temp_set == set():
            check = True
        else:
            for fun in temp_set:
                if fun not in parent_child_list:
                    check = True
                    if any(s == [flow, function.parent] for s in opposite_list):
                        delete_opposite(flow, function.parent, output_xml, relationship_str)
                if fun in parent_child_list:
                    length -= 1
        if length == 0 and not current_loop_check and temp_set != set():
            delete_opposite(flow, function.parent, output_xml, relationship_str)
    if check:
        return elem


def delete_opposite(data, function, output_xml, relationship_type):
    """
    Delete specific consumer/producer relationship within xml's file.

        Parameters:
            data (Data_name_str) : Data's name
            function (Function) : Current Function object
            output_xml (GenerateXML object) : XML's file object
            relationship_type (str) : Type of relationship (i.e. consumer or producer)
        Returns:
            None
    """

    if relationship_type == "producer":
        output_xml.delete_single_consumer_producer(data,
                                                   function,
                                                   "consumer")
        print(f"{function.name} does not consume {data} anymore")
    elif relationship_type == "consumer":

        output_xml.delete_single_consumer_producer(data,
                                                   function,
                                                   "producer")
        print(f"{function.name} does not produce {data} anymore")


def check_add_producer_function(producer_str_list, xml_consumer_function_list,
                                xml_producer_function_list, xml_function_list, xml_data_list,
                                output_xml):
    """
    Check if each string in consumer_str_list are corresponding to an actual object, create new
    [data, producer] objects list for object's type : Function.
    Send list to add_producer_function() to write them within xml and then returns update.

        Parameters:
            producer_str_list ([str]) : List of string from jarvis cell
            xml_consumer_function_list ([Data_name_str, Function]) : Data's name and consumer's
            function list from xml
            xml_producer_function_list ([Data_name_str, Function]) : Data's name and producer's
            function list from xml
            xml_function_list ([Function]) : Function list from xml parsing
            xml_data_list ([Data]) : Data list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    new_producer_list = []
    # Create object names/aliases list
    xml_function_name_list = get_objects_names(xml_function_list)
    xml_data_name_list = get_objects_names(xml_data_list)
    # Loop to filter producer and create a new list
    for elem in producer_str_list:
        is_elem_found = True
        if not any(item == elem[1] for item in xml_function_name_list) and \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            print(f"{elem[1]} and {elem[0]} do not exist")
        elif not any(item == elem[1] for item in xml_function_name_list) or \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            if any(item == elem[1] for item in xml_function_name_list) and \
                    not any(item == elem[0] for item in xml_data_name_list):
                print(f"{elem[0]} does not exist")
            elif any(item == elem[0] for item in xml_data_name_list) and \
                    not any(item == elem[1] for item in xml_function_name_list):
                print(f"{elem[1]} does not exist")

        if is_elem_found:
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if elem[1] == function.name or elem[1] == function.alias:
                    if [elem[0], function] not in xml_producer_function_list:
                        if [elem[0], function] not in xml_consumer_function_list:
                            new_producer_list.append([elem[0], function])
                            parent = add_parent_recursively(elem[0], function,
                                                            xml_producer_function_list,
                                                            xml_consumer_function_list,
                                                            new_producer_list, output_xml,
                                                            "producer")
                            if parent is not None:
                                for par in parent:
                                    if par:
                                        new_producer_list.append(par)

                        elif [elem[0], function] in xml_consumer_function_list:
                            pass

    update = add_producer_function(new_producer_list, xml_producer_function_list, output_xml)

    return update


def add_producer_function(new_producer_list, xml_producer_function_list, output_xml):
    """
    Check if input list is not empty, write in xml for each element and return update list if some
    updates has been made

        Parameters:
            new_producer_list ([Data_name_str, Function]) : Data's name and producer's function list
            xml_producer_function_list ([Data_name_str, Function]) : Data's name and producer's
            function list from xml
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if not new_producer_list:
        return 0

    output_xml.write_producer(new_producer_list)
    # Warn the user once added within xml
    for producer in new_producer_list:
        xml_producer_function_list.append(producer)
        print(f"{producer[1].name} produces {producer[0]}")
    return 1


def add_state_by_name(state_name_str_list, xml_state_list, output_xml):
    """
    Check if each string in state_name_str_list is not already corresponding to an actual object's
    name/alias, create new State() object, instantiate it, write it within XML and then returns
    update_list.

        Parameters:
            state_name_str_list ([str]) : Lists of string from jarvis cell
            xml_state_list ([State]) : State list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    state_list = []
    # Create a list with all state names/aliases already in the xml
    xml_state_name = get_objects_names(xml_state_list)
    # Loop on the list and create set for states
    for state_name in state_name_str_list:
        if state_name not in xml_state_name:
            # Instantiate State class and state
            state = datamodel.State()
            # Set state's name
            state.set_name(str(state_name))
            alias_str = re.search(r"(.*)\s[-]\s", state_name, re.MULTILINE)
            if alias_str:
                state.set_alias(alias_str.group(1))
            # Set state's type
            state.set_type(str(datamodel.StateType.UNKNOWN))
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            state.set_id(str(identifier.int)[:10])
            # Add state to a set()
            xml_state_list.add(state)
            state_list.append(state)
        else:
            # print(state_name + " already exists (not added)")
            pass
    if not state_list:
        return 0

    output_xml.write_state(state_list)
    for state in state_list:
        print(state.name + " is a state")
    return 1


def add_transition_by_name(transition_name_str_list, xml_transition_list, output_xml):
    """
    Check if each string in transition_name_str_list is not already corresponding to an actual
    object's name/alias, create new Transition() object, instantiate it, write it within XML and
    then returns update_list.

        Parameters:
            transition_name_str_list ([str]) : Lists of string from jarvis cell
            xml_transition_list ([State]) : Transition list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    transition_list = []
    # Create a list with all transition's name already in the xml
    xml_transition_name_list = get_objects_names(xml_transition_list)
    # Loop on the list and create set for transitions
    for transition_name in transition_name_str_list:
        if transition_name not in xml_transition_name_list:
            # Instantiate Transition
            transition = datamodel.Transition()
            # Set state's name
            transition.set_name(str(transition_name))
            alias_str = re.search(r"(.*)\s[-]\s", transition_name, re.MULTILINE)
            if alias_str:
                transition.set_alias(alias_str.group(1))
            # Set state's type
            transition.set_type(str(datamodel.StateType.UNKNOWN))
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            transition.set_id(str(identifier.int)[:10])
            # Add state to a set()
            xml_transition_list.add(transition)
            transition_list.append(transition)

    if not transition_list:
        return 0

    output_xml.write_transition(transition_list)
    for transition in transition_list:
        print(transition.name + " is a transition")
    return 1


# TODO: Check condition_str on data and (add LogicalType, ArithmeticType in datamodel.py)
def check_add_transition_condition(trans_condition_str_list, xml_transition_list, output_xml):
    """
    Check if each string in trans_condition_str_list is corresponding to an actual Transition
    object, create new [Transition, condition_str] objects lists for object's type : Transition.
    Send lists to add_transition_condition() to write them within xml and then returns update_list
    from it.

        Parameters:
            trans_condition_str_list ([str]) : Lists of string from jarvis cell
            xml_transition_list ([Transition]) : Transition list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    condition_list = []
    # Create a list with all transition names/aliases already in the xml
    xml_transition_name_list = get_objects_names(xml_transition_list)
    for transition_str, condition_str in trans_condition_str_list:
        is_elem_found = True
        if not any(transition_str in s for s in xml_transition_name_list):
            is_elem_found = False
            print(f"The transition {transition_str} does not exist")

        if is_elem_found:
            for transition in xml_transition_list:
                if transition_str == transition.name or transition_str == transition.alias:
                    if not condition_str.lstrip(' ') in transition.condition_list:
                        condition_list.append([transition, condition_str.lstrip(' ')])

    update = add_transition_condition(condition_list, output_xml)

    return update


def add_transition_condition(condition_list, output_xml):
    """
    Check if input list is not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            condition_list ([Transition, condition_str]) : Transition object and conditions as str
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if not condition_list:
        return 0

    output_xml.write_transition_condition(condition_list)
    for elem in condition_list:
        elem[0].add_condition(elem[1])
        print(f"Condition for {elem[0].name} : {elem[1]}")
    return 1


def check_add_src_dest(src_dest_str, xml_transition_list, xml_state_list, output_xml):
    """
    Check if each string in src_dest_str is corresponding to an actual Transition and State object,
    create new [Transition, State] objects lists.
    Send lists to add_src_dest() to write them within xml and then returns update_list from it.

        Parameters:
            src_dest_str ([str]) : Lists of string from jarvis cell
            xml_transition_list ([Transition]) : Transition list from xml parsing
            xml_state_list ([State]) : State list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    new_src_list = []
    new_dest_list = []
    # Create lists with all object names/aliases already in the xml
    xml_transition_name_list = get_objects_names(xml_transition_list)
    xml_state_name_list = get_objects_names(xml_state_list)

    concatenated_lists = [*xml_transition_name_list, *xml_state_name_list]

    # elem = [source/destination, transition_name, state_name]
    for elem in src_dest_str:
        is_elem_found = True
        if not all(t in concatenated_lists for t in [elem[1], elem[2]]):
            is_elem_found = False
            if any(elem[1] in s for s in xml_transition_name_list) and not any(
                    elem[2] in j for j in xml_state_name_list):
                print(f"{elem[2]} state does not exist")
            elif any(elem[2] in s for s in xml_state_name_list) and not any(
                    elem[1] in j for j in xml_transition_name_list):
                print(f"{elem[1]} transition does not exist")
            else:
                print(f"{elem[1]} transition and {elem[2]} state do not exist")

        if is_elem_found:
            if elem[0] == "source":
                for transition in xml_transition_list:
                    if elem[1] == transition.name or elem[1] == transition.alias:
                        for state in xml_state_list:
                            if elem[2] == state.name or elem[2] == state.alias:
                                if state.type == datamodel.StateType.EXIT:
                                    print(f"{elem[2]} is typed as EXIT state, "
                                          f"it cannot be put as source's transition (not added)")
                                else:
                                    if transition.source != state.id:
                                        new_src_list.append([transition, state])

            elif elem[0] == "destination":
                for transition in xml_transition_list:
                    if elem[1] == transition.name or elem[1] == transition.alias:
                        for state in xml_state_list:
                            if elem[2] == state.name or elem[2] == state.alias:
                                if state.type == datamodel.StateType.ENTRY:
                                    print(f"{elem[2]} is typed as ENTRY state, it cannot be "
                                          f"put as destination's transition (not added)")
                                else:
                                    if transition.destination != state.id:
                                        new_dest_list.append([transition, state])

    src_dest_lists = [new_src_list, new_dest_list]
    update = add_src_dest(src_dest_lists, output_xml)

    return update


def add_src_dest(src_dest_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            src_dest_lists ([Transition, State(Source)],[Transition, State(Destination)]) :
            Transition object and Source/Destination
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if any(src_dest_lists):
        new_src_list = src_dest_lists[0]
        new_dest_list = src_dest_lists[1]
        if new_src_list:
            output_xml.write_source(new_src_list)
            # Warn the user once writtent and added within xml
            for source in new_src_list:
                source[0].set_source(source[1].id)
                print(f"{source[1].name} source for {source[0].name}")

        if new_dest_list:
            output_xml.write_destination(new_dest_list)
            # Warn the user once writtent and added within xml
            for destination in new_dest_list:
                destination[0].set_destination(destination[1].id)
                print(f"{destination[1].name} destination for {destination[0].name}")
        return 1

    return 0


def create_fun_elem_obj(fun_elem_str, specific_obj_type, **kwargs):
    """
    Check if string fun_elem_str is not already corresponding to an actual object's name/alias,
    create new FunctionalElement() object, instantiate it, add it to xml_fun_elem_list.

        Parameters:
            fun_elem_str (str) : Lists of string from jarvis cell
            specific_obj_type ([Function]) : specific type or None
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update (0/fun_elem) : fun_elem if update, else 0
    """
    if any(n == fun_elem_str for n in get_objects_names(kwargs['xml_fun_elem_list'])):
        return 0
    if not specific_obj_type:
        fun_elem = datamodel.FunctionalElement(p_name=fun_elem_str)
    else:
        fun_elem = datamodel.FunctionalElement(p_name=fun_elem_str, p_type=specific_obj_type.name)

    alias_str = re.search(r"(.*)\s[-]\s", fun_elem_str, re.MULTILINE)
    if alias_str:
        fun_elem.set_alias(alias_str.group(1))
    fun_elem.set_id(shared_orchestrator.get_unique_id())
    # Add function to a set()
    kwargs['xml_fun_elem_list'].add(fun_elem)
    print(f"{fun_elem.name} is a {fun_elem.type}")
    if fun_elem:
        return fun_elem
    return 0


def create_fun_inter_obj(fun_inter_str, specific_obj_type, **kwargs):
    """
    Check if string fun_inter_str is not already corresponding to an actual object's name/alias,
    create new FunctionalInterface() object, instantiate it, add it to xml_fun_inter_list.

        Parameters:
            fun_inter_str (str) : Lists of string from jarvis cell
            specific_obj_type ([Function]) : specific type or None
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update (0/fun_elem) : fun_elem if update, else 0
    """
    if any(n == fun_inter_str for n in get_objects_names(kwargs['xml_fun_inter_list'])):
        return 0
    if not specific_obj_type:
        fun_inter = datamodel.FunctionalInterface(p_name=fun_inter_str)
    else:
        fun_inter = datamodel.FunctionalInterface(p_name=fun_inter_str,
                                                  p_type=specific_obj_type.name)

    alias_str = re.search(r"(.*)\s[-]\s", fun_inter_str, re.MULTILINE)
    if alias_str:
        fun_inter.set_alias(alias_str.group(1))
    fun_inter.set_id(shared_orchestrator.get_unique_id())
    # Add function to a set()
    kwargs['xml_fun_inter_list'].add(fun_inter)
    print(f"{fun_inter.name} is a {fun_inter.type}")
    if fun_inter:
        return fun_inter
    return 0


def check_add_exposes(exposes_str_list, xml_fun_elem_list, xml_fun_inter_list, xml_data_list,
                      output_xml):
    """
    Check and get all "Fun_elem exposes Fun_inter" strings, if Fun_inter is not exposed yet
    (or parentality relationship) => add it to Fun_elem object and as exposedInterface within xml.
    Args:
        exposes_str_list ([strings]): list of strings
        xml_fun_elem_list ([Fun Elem]) : Functional Element list from xml parsing
        xml_fun_inter_list ([FunctionalInterface]) : FunctionalInterface list from xml parsing
        xml_data_list ([Data]) : Data list from xml parsing
        output_xml (GenerateXML object) : XML's file object

    Returns:
        [0/1] : if update has been made
    """
    output = False
    for exposes_str in exposes_str_list:
        fun_elem = check_get_object(exposes_str[0], **{'xml_fun_elem_list': xml_fun_elem_list})
        fun_inter = check_get_object(exposes_str[1], **{'xml_fun_inter_list': xml_fun_inter_list})

        check_print_wrong_pair_object((exposes_str[0], fun_elem, 'Functional Element'),
                                      (exposes_str[1], fun_inter, 'Functional Interface'),
                                      'exposes')
        if fun_elem and fun_inter:
            check_rule = check_fun_elem_inter_families(fun_elem, fun_inter, xml_fun_elem_list)
            if fun_inter.id not in fun_elem.exposed_interface_list and check_rule:
                output = True
                fun_elem.add_exposed_interface(fun_inter.id)
                output_xml.write_exposed_interface([[fun_elem, fun_inter]])
                print(f"{fun_elem.name} exposes {fun_inter.name}")

    if output:
        return 1

    return 0


def check_fun_elem_inter_families(fun_elem, fun_inter, xml_fun_elem_list):
    """A fun elem can expose an interface if already allocated to a parent/child and
    an interface can only be exposed by 2 families of fun_elem"""
    check = True
    exposed_fun_elem_list = set()
    for xml_fun_elem in xml_fun_elem_list:
        if any(s == fun_inter.id for s in xml_fun_elem.exposed_interface_list) and \
                xml_fun_elem != fun_elem:
            exposed_fun_elem_list.add(xml_fun_elem)

    if not exposed_fun_elem_list:
        return check

    opposite_fun_elem_list = []
    for elem in exposed_fun_elem_list:
        if check_parentality(elem, fun_elem) or \
                check_parentality(fun_elem, elem):
            return check
        else:
            opposite_fun_elem_list.append(elem)

    for idx in range(0, len(opposite_fun_elem_list)-1):
        if not check_parentality(
                opposite_fun_elem_list[idx], opposite_fun_elem_list[idx+1]) and \
                not check_parentality(opposite_fun_elem_list[idx+1], opposite_fun_elem_list[idx]):
            check = False
            return check

    return check


def check_print_wrong_pair_object(object_a, object_b, relationship_type):
    """
    Prints specific user messages for wrong object(s) pair (Object_a, Object_b) relationship

    Args:
        object_a: (input_string, object_or_none, object_type_string)
        e.g. (exposes_str[0], fun_elem, 'Functional Element')
        object_b: (exposes_str[1], fun_inter, 'Functional Interface')
        relationship_type: e.g. 'exposes'

    """
    if object_a[1] == object_b[1] is None:
        print(f"{object_a[0]} and {object_b[0]} do not exist, choose valid names/aliases for: "
              f"'{object_a[2]}' {relationship_type} "
              f"'{object_b[2]}'")
    elif object_a[1] is None or object_b[1] is None:
        if object_a[1] is None and object_b[1]:
            print(f"{object_a[0]} does not exist, choose a valid name/alias for: "
                  f"'{object_a[2]}' {relationship_type} "
                  f"{object_b[1].name}")
        elif object_b[1] is None and object_a[1]:
            print(f"{object_b[0]} does not exist, choose a valid name/alias for: "
                  f"{object_a[1].name} {relationship_type} "
                  f"'{object_b[2]}'")
