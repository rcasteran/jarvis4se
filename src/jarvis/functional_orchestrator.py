#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import re
import os
import sys
import uuid

# Modules
from .viewpoint_orchestrator import check_add_allocated_item
from .question_answer import get_object_type, get_object_name, get_allocation_object, \
    get_children, check_get_object, check_parentality

sys.path.append("../plantuml_adapter")
import plantuml_adapter # noqa
if not os.path.exists("../datamodel"):
    sys.path.append("../datamodel")
import datamodel # noqa


def add_function_by_name(function_name_str_list, xml_function_list, output_xml):
    """
    Check if each string in function_name_str_list is not already corresponding to an actual
    object's name/alias, create new Function() object, instantiate it, write it within XML and
    then returns update_list.

        Parameters:
            function_name_str_list ([str]) : Lists of string from jarvis cell
            xml_function_list ([Function]) : function list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    function_list = set()
    # Create a list with all function names/aliases already in the xml
    xml_function_name_list = get_object_name(xml_function_list)
    # Loop on the list and create set for functions
    for function_name in function_name_str_list:
        if function_name not in xml_function_name_list:
            # Instantiate Function class and function
            function = datamodel.Function()
            # Set function's name
            function.set_name(str(function_name))
            alias_str = re.search(r"(.*)\s[-]\s", function_name, re.MULTILINE)
            if alias_str:
                function.set_alias(alias_str.group(1))
            # Set function's type
            function.set_type(datamodel.FunctionType.UNKNOWN)
            function.set_operand()
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            function.set_id(str(identifier.int)[:10])
            # Add function to a set()
            xml_function_list.add(function)
            function_list.add(function)

    if not function_list:
        update_list.append(0)
    else:
        output_xml.write_function(function_list)
        for fun in function_list:
            print(fun.name + " is a function")
        update_list.append(1)

    return update_list


def cut_string_list(string_tuple_list):
    """From set of input command strings e.g for composition with input list as
    {(Function_name, Function_name_A), (Function_name, [Function_name_B, Function_name_C])} : this
    methods returns {(Function_name, Function_name_A), (Function_name, Function_name_B),
    (Function_name, Function_name_C)}

        Parameters:
            string_tuple_list ({(str, str), ...}) : Lists of string tuple from jarvis cell
        Returns:
            output_list ([0/1]) : output list
    """

    output_list = set()
    for parent, child in string_tuple_list:
        if "," in child:
            child_str = child.replace(" ", "")
            child_list_str = re.split(r',(?![^[]*\])', child_str)
            for elem in child_list_str:
                output_list.add((parent, elem))
        else:
            output_list.add((parent, child))

    return output_list


def check_add_child(parent_child_name_str_list, xml_function_list, xml_state_list,
                    xml_fun_elem_list, output_xml):
    """
    Check if each string in parent_child_name_str_list are corresponding to an actual object,
    create new [parent, child] objects lists for object's type : State/Function/FunctionalElement.
    Send lists to add_child() to write them within xml and then returns update_list from it.

        Parameters:
            parent_child_name_str_list ([str]) : Lists of string from jarvis cell
            xml_function_list ([Function]) : function list from xml parsing
            xml_state_list ([State]) : state list from xml parsing
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            fun elem's dict
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    # Instanciate new lists
    parent_child_function_list = []
    parent_child_state_list = []
    parent_child_fun_elem_list = []
    # Create the xml [function_name/function_alias] list
    xml_function_name_list = get_object_name(xml_function_list)
    # Create the xml [state_name/state_alias] list
    xml_state_name_list = get_object_name(xml_state_list)
    # Create the xml [fun_elem_name/fun_elem_alias] list
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)

    concatenated_lists = [*xml_function_name_list, *xml_state_name_list, *xml_fun_elem_name_list]

    cleaned_parent_child_list_str = cut_string_list(parent_child_name_str_list)

    for elem in cleaned_parent_child_list_str:
        is_elem_found = True
        if not any(elem[0] in j for j in concatenated_lists) or \
                not any(elem[1] in j for j in concatenated_lists):
            is_elem_found = False
            if any(elem[0] in j for j in concatenated_lists) and \
                    not any(elem[1] in j for j in concatenated_lists):
                print(f"{elem[1]} does not exist")
            elif any(elem[1] in j for j in concatenated_lists) and \
                    not any(elem[0] in j for j in concatenated_lists):
                print(f"{elem[0]} does not exist")
            else:
                print(f"{elem[0]} and {elem[1]} do not exist")
        if is_elem_found:
            result_function = all(t in xml_function_name_list for t in elem)
            result_state = all(t in xml_state_name_list for t in elem)
            result_fun_elem = all(t in xml_fun_elem_name_list for t in elem)
            if result_function:
                for function in xml_function_list:
                    if elem[0] == function.name or elem[0] == function.alias:
                        for fu in xml_function_list:
                            if elem[1] == fu.name or elem[1] == fu.alias:
                                if fu.parent is None:
                                    fu.set_parent(function)
                                    function.add_child(fu)
                                    parent_child_function_list.append([function, fu])

            elif result_state:
                for state in xml_state_list:
                    if elem[0] == state.name or elem[0] == state.alias:
                        for sta in xml_state_list:
                            if elem[1] == sta.name or elem[1] == sta.alias:
                                if sta.parent is None:
                                    sta.set_parent(state)
                                    state.add_child(sta)
                                    parent_child_state_list.append([state, sta])

            elif result_fun_elem:
                for fun_elem in xml_fun_elem_list:
                    if elem[0] == fun_elem.name or elem[0] == fun_elem.alias:
                        for fe in xml_fun_elem_list:
                            if elem[1] == fe.name or elem[1] == fe.alias:
                                if fe.parent is None:
                                    fe.set_parent(fun_elem)
                                    fun_elem.add_child(fe)
                                    parent_child_fun_elem_list.append([fun_elem, fe])

            else:
                if any(elem[0] in j for j in xml_function_name_list) and not any(
                        elem[1] in j for j in xml_function_name_list):
                    print(f"{elem[1]} is not a function object")
                elif any(elem[0] in j for j in xml_state_name_list) and not any(
                        elem[1] in j for j in xml_state_name_list):
                    print(f"{elem[1]} is not a state object")
                elif any(elem[0] in j for j in xml_fun_elem_name_list) and not any(
                        elem[1] in j for j in xml_fun_elem_name_list):
                    print(f"{elem[1]} is not a functional element object")

    all_lists = [parent_child_function_list, parent_child_state_list, parent_child_fun_elem_list]
    update_list = add_child(all_lists, xml_fun_elem_list, output_xml)

    return update_list


def add_child(parent_child_lists, xml_fun_elem_list, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            parent_child_lists ([Parent State/Function/fun elem, Child State/Function/fun elem]) :
            parent object
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    if any(parent_child_lists):
        parent_child_function_list = parent_child_lists[0]
        parent_child_state_list = parent_child_lists[1]
        paren_child_fun_elem_list = parent_child_lists[2]
        if parent_child_function_list:
            output_xml.write_function_child(parent_child_function_list)
            # Warn the user once added within xml
            for i in parent_child_function_list:
                print(f"{i[0].name} is composed of {i[1].name}")
                for fun_elem in xml_fun_elem_list:
                    if i[0].id in fun_elem.allocated_function_list:
                        recursive_allocation([fun_elem, i[1]], output_xml)

        if parent_child_state_list:
            output_xml.write_state_child(parent_child_state_list)
            # Warn the user once added within xml
            for i in parent_child_state_list:
                print(f"{i[0].name} is composed of {i[1].name}")
                for fun_elem in xml_fun_elem_list:
                    if i[0].id in fun_elem.allocated_state_list:
                        recursive_allocation([fun_elem, i[1]], output_xml)

        if paren_child_fun_elem_list:
            output_xml.write_functional_element_child(paren_child_fun_elem_list)
            # Warn the user once added within xml
            for i in paren_child_fun_elem_list:
                print(f"{i[0].name} is composed of {i[1].name}")

        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def get_allocated_child(i, xml_fun_elem_list):
    """
    Check if the parent state/function is already allocated to a fun elem and create list to add
    its child also (if not already allocated)

        Parameters:
            i ([State/Function]) : parent object, child object
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing

        Returns:
            output_list ([FunctionalElement, State/Function]) : Allocation Relationships that need
            to be added
    """
    output_list = []
    object_type = get_object_type(i[0])
    allocated_list = None
    for fun_elem in xml_fun_elem_list:
        if object_type == "state":
            allocated_list = fun_elem.allocated_state_list.copy()
        elif object_type == "function":
            allocated_list = fun_elem.allocated_function_list.copy()
        if allocated_list:
            for allocated_object in allocated_list:
                if allocated_object == i[0].id:
                    if i[1].id not in allocated_list:
                        if object_type == "state":
                            fun_elem.add_allocated_state(i[1].id)
                        elif object_type == "function":
                            fun_elem.add_allocated_function(i[1].id)
                        output_list.append([fun_elem, i[1]])

    return output_list


def add_data(data_str_list, xml_data_list, output_xml):
    """
    Check if each string in data_str_list is not already corresponding to an actual object's
    name/alias, create new Data() object, instantiate it, write it within XML and then returns
    update_list.

        Parameters:
            data_str_list ([str]) : Lists of string from jarvis cell
            xml_data_list ([Data]) : Data list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    new_data_list = set()
    # Create data names list already in xml
    xml_data_name_list = get_object_name(xml_data_list)
    # Filter data_list, keeping only the the ones not already in the xml
    for data_name in data_str_list:
        if data_name not in xml_data_name_list:
            new_data = datamodel.Data()
            new_data.set_name(str(data_name))
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            new_data.set_id(str(identifier.int)[:10])
            new_data.set_type(datamodel.DataType.UNKNOWN)

            new_data_list.add(new_data)

    if not new_data_list:
        update_list.append(0)
    else:
        output_xml.write_data(new_data_list)
        for data in new_data_list:
            xml_data_list.add(data)
            print(data.name + " is a data" + "")
        update_list.append(1)

    return update_list


def check_add_predecessor(data_predecessor_str_set, xml_data_list, xml_chain_list, output_xml):
    """
    Check if each string in data_predecessor_str_set is corresponding to an actual Data object,
    create new [Data, predecessor] objects lists for object's type : Data.
    Send lists to add_predecessor() to write them within xml and then returns update_list from it.

        Parameters:
            data_predecessor_str_set ([str]) : Lists of string from jarvis cell
            xml_data_list ([Data]) : Data list from xml parsing
            xml_chain_list ([Chain]) : Chain list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    data_predecessor_list = []

    allocated_item_list = []
    # Filter input string
    data_predecessor_str_list = cut_string_list(data_predecessor_str_set)

    # Create data names list already in xml
    xml_data_name_list = get_object_name(xml_data_list)

    is_elem_found = False
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
        for d, p in data_predecessor_str_list:
            predecessor = None
            selected_data = None
            existing_predecessor_id_list = []
            for data in xml_data_list:
                if d == data.name:
                    selected_data = data
                    for existing_predecessor in data.predecessor_list:
                        existing_predecessor_id_list.append(existing_predecessor.id)
            for da in xml_data_list:
                if p == da.name and da.id not in existing_predecessor_id_list:
                    predecessor = da
            if predecessor is not None and selected_data is not None:
                data_predecessor_list.append([selected_data, predecessor])
            allocation_chain_1 = check_add_allocated_item(d,
                                                          xml_data_list,
                                                          xml_chain_list)
            if allocation_chain_1:
                allocated_item_list.append(allocation_chain_1)
            allocation_chain_2 = check_add_allocated_item(p,
                                                          xml_data_list,
                                                          xml_chain_list)
            if allocation_chain_2:
                allocated_item_list.append(allocation_chain_2)

    update_list = add_predecessor(data_predecessor_list, xml_data_list, output_xml)
    add_allocation([0, 0, 0, allocated_item_list, 0], output_xml)

    return update_list


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
    update_list = []
    if not predecessor_list:
        update_list.append(0)
    else:
        output_xml.write_predecessor(predecessor_list)
        # Warn the user once added within xml
        for data_predecessor in predecessor_list:
            for d in xml_data_list:
                if data_predecessor[0].id == d.id:
                    d.add_predecessor(data_predecessor[1])
                    print(f"{data_predecessor[1].name} predecessor for "
                          f"{data_predecessor[0].name}")
        update_list.append(1)

    return update_list


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
    xml_function_name_list = get_object_name(xml_function_list)
    xml_data_name_list = get_object_name(xml_data_list)
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
                            None

    update_list = add_consumer_function(new_consumer_list, xml_consumer_function_list, output_xml)

    return update_list


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
    update_list = []
    if not new_consumer_list:
        update_list.append(0)
    else:
        output_xml.write_consumer(new_consumer_list)
        # Warn the user once added within xml
        for consumer in new_consumer_list:
            xml_consumer_function_list.append(consumer)
            print(f"{consumer[1].name} consumes {consumer[0]}")
        update_list.append(1)

    return update_list


def add_parent_recursively(flow, function, current_list, opposite_list, new_list, output_xml,
                           relationship_str, out=False):
    """
    Recursive method around add_parent_for_data().
        Parameters:
            flow (Data_name_str) : Data's name
            function (Function) : Current function's parent
            current_list ([Data_name_str, function_name_str]) : 'Current' list (producer or consumer)
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
            current_list ([Data_name_str, function_name_str]) : 'Current' list (producer or consumer)
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
    Send list to add_producer_function() to write them within xml and then returns update_list from it.

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
    xml_function_name_list = get_object_name(xml_function_list)
    xml_data_name_list = get_object_name(xml_data_list)
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
                            None

    update_list = add_producer_function(new_producer_list, xml_producer_function_list, output_xml)

    return update_list


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
    update_list = []
    if not new_producer_list:
        update_list.append(0)
    else:
        output_xml.write_producer(new_producer_list)
        # Warn the user once added within xml
        for producer in new_producer_list:
            xml_producer_function_list.append(producer)
            print(f"{producer[1].name} produces {producer[0]}")
        update_list.append(1)

    return update_list


def check_and_delete(delete_str_list, xml_function_list, xml_producer_function_list,
                     xml_consumer_function_list, xml_data_list, xml_state_list,
                     xml_transition_list, xml_fun_elem_list, output_xml):
    """
    Check if each string in consumer_str_list are corresponding to an actual object, create new
    objects list for objects to delete : Data/State/Function/FunctionalElement/transition.
    Send list to delete_objects() to delete them within xml and then returns update_list from it.

        Parameters:
            delete_str_list ([str]) : List of string from jarvis cell
            xml_function_list ([Function]) : Function list from xml parsing
            xml_producer_function_list ([Data_name_str, Function]) : Data's name and producer's
            function list from xml
            xml_consumer_function_list ([Data_name_str, Function]) : Data's name and consumer's
            function list from xml
            xml_data_list ([Data]) : Data list from xml parsing
            xml_state_list ([State]) : State list from xml parsing
            xml_transition_list ([Transition]) : Transition list from xml parsing
            xml_fun_elem_list ([FunctionalElement]) : FunctionalElement list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    to_be_deleted_function_list = []
    to_be_deleted_data_list = []
    to_be_deleted_state_list = []
    to_be_deleted_fun_elem_list = []
    to_be_deleted_transition_list = []
    xml_consumer_function_name_list = []
    xml_producer_function_name_list = []
    xml_src_dest_list = []
    xml_allocated_object_id_list = []
    # Create object names/aliases lists
    xml_function_name_list = get_object_name(xml_function_list)
    xml_data_name_list = get_object_name(xml_data_list)
    xml_state_name_list = get_object_name(xml_state_list)
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)
    xml_transition_name_list = get_object_name(xml_transition_list)
    # Create the xml [flow, consumer_name] list
    for xml_consumer in xml_consumer_function_list:
        xml_consumer_function_name_list.append([xml_consumer[0], xml_consumer[1].name])
    # Create the xml [flow, producer_name] list
    for xml_producer in xml_producer_function_list:
        xml_producer_function_name_list.append([xml_producer[0], xml_producer[1].name])
    # Create the list with all xml [source_id, destination_id] for transitions
    for transitions in xml_transition_list:
        xml_src_dest_list.append(transitions.source)
        xml_src_dest_list.append(transitions.destination)
    # Create the list with all xml [allocated_function, allocated_state] for transitions
    for fun_elem in xml_fun_elem_list:
        for i in fun_elem.allocated_state_list:
            xml_allocated_object_id_list.append(i)
        for j in fun_elem.allocated_function_list:
            xml_allocated_object_id_list.append(j)
    for state in xml_state_list:
        if state.allocated_function_list:
            for k in state.allocated_function_list:
                xml_allocated_object_id_list.append(k)

    concatenated_lists = [*xml_function_name_list, *xml_data_name_list, *xml_state_name_list,
                          *xml_fun_elem_name_list, *xml_transition_name_list]
    # Check if the wanted to delete object exists and can be deleted
    for elem in delete_str_list:
        if not any(s == elem for s in concatenated_lists):
            print(f"{elem} does not exist")
        elif any(elem in flow_consumer for flow_consumer in xml_consumer_function_name_list):
            print(f"{elem} in [flow, consumer] list (not deleted)")
        elif any(elem in flow_producer for flow_producer in xml_producer_function_name_list):
            print(f"{elem} in [flow, producer] list (not deleted)")
        else:
            result_function = any(s == elem for s in xml_function_name_list)
            resul_state = any(s == elem for s in xml_state_name_list)
            result_data = any(s == elem for s in xml_data_name_list)
            result_fun_elem = any(s == elem for s in xml_fun_elem_name_list)
            result_transition = any(s == elem for s in xml_transition_name_list)
            if result_function:
                for function in xml_function_list:
                    if elem == function.name or elem == function.alias:
                        if function.id in xml_allocated_object_id_list:
                            print(f"{elem} allocated to a functional element or state "
                                  f"(not deleted)")
                        else:
                            if function.parent is None and function.child_list == set():
                                to_be_deleted_function_list.append(function)
                            else:
                                print(f"{elem} is already composed or composes a function "
                                      f"(not deleted)")
            elif result_data:
                for xml_data in xml_data_list:
                    if elem == xml_data.name:
                        if xml_data.predecessor_list == set():
                            to_be_deleted_data_list.append(xml_data)
            elif resul_state:
                for state in xml_state_list:
                    if elem == state.name or elem == state.alias:
                        if state.id in xml_src_dest_list:
                            print(f"{elem} associated to transition (not deleted)")
                        elif state.id in xml_allocated_object_id_list:
                            print(f"{elem} allocated to a functional element (not deleted)")
                        else:
                            if state.parent is None and state.child_list == set():
                                to_be_deleted_state_list.append(state)
                            else:
                                print(f"{elem} is already composed of or composes a state "
                                      f"(not deleted)")
            elif result_fun_elem:
                for fun_elem in xml_fun_elem_list:
                    if elem == fun_elem.name or elem == fun_elem.alias:
                        if fun_elem.allocated_state_list != set():
                            print(f"{elem} has allocated state(s) (not deleted)")
                        elif fun_elem.allocated_function_list != set():
                            print(f"{elem} has allocated function(s) (not deleted)")
                        else:
                            if fun_elem.parent is None and fun_elem.child_list == set():
                                to_be_deleted_fun_elem_list.append(fun_elem)
                            else:
                                print(f"{elem} is already composed or composes a functional "
                                      f"element (not deleted)")
            elif result_transition:
                for transition in xml_transition_list:
                    if elem == transition.name or elem == transition.alias:
                        if transition.source != 'None':
                            print(f"{elem} attached to a source's state (not deleted)")
                        elif transition.destination != 'None':
                            print(f"{elem} attached to a destination's state (not deleted)")
                        elif transition.condition_list != set():
                            print(f"{elem} has conditions (not deleted)")
                        else:
                            to_be_deleted_transition_list.append(transition)

    to_be_deleted_lists = [to_be_deleted_function_list, to_be_deleted_data_list,
                           to_be_deleted_state_list, to_be_deleted_fun_elem_list,
                           to_be_deleted_transition_list]
    xml_lists = [xml_function_list, xml_data_list, xml_state_list, xml_fun_elem_list,
                 xml_transition_list]
    update_list = delete_objects(to_be_deleted_lists, xml_lists, output_xml)

    return update_list


def delete_objects(to_be_deleted_lists, xml_lists, output_xml):
    """
    Check if input lists are not empty, delete each element and return update list if some updates
    has been made

        Parameters:
            to_be_deleted_lists ([[Function], [Data], [State], ...]) : Objects to delete
            xml_lists ([Data_name_str, Function]) : Current xml objects to remove object from it
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    if any(to_be_deleted_lists):
        to_be_deleted_function_list = to_be_deleted_lists[0]
        to_be_deleted_data_list = to_be_deleted_lists[1]
        to_be_deleted_state_list = to_be_deleted_lists[2]
        to_be_deleted_fun_elem_list = to_be_deleted_lists[3]
        to_be_deleted_transition_list = to_be_deleted_lists[4]
        if to_be_deleted_function_list:
            output_xml.delete_function(to_be_deleted_function_list)
            for deleted_function in to_be_deleted_function_list:
                xml_lists[0].remove(deleted_function)
                print(f"{deleted_function.name} deleted")

        if to_be_deleted_data_list:
            output_xml.delete_data(to_be_deleted_data_list)
            for deleted_data in to_be_deleted_data_list:
                xml_lists[1].remove(deleted_data)
                print(f"{deleted_data.name} deleted")

        if to_be_deleted_state_list:
            output_xml.delete_state(to_be_deleted_state_list)
            for deleted_state in to_be_deleted_state_list:
                xml_lists[2].remove(deleted_state)
                print(f"{deleted_state.name} deleted")

        if to_be_deleted_fun_elem_list:
            output_xml.delete_functional_element(to_be_deleted_fun_elem_list)
            for deleted_fun_elem in to_be_deleted_fun_elem_list:
                xml_lists[3].remove(deleted_fun_elem)
                print(f"{deleted_fun_elem.name} deleted")

        if to_be_deleted_transition_list:
            output_xml.delete_transition(to_be_deleted_transition_list)
            for deleted_transition in to_be_deleted_transition_list:
                xml_lists[4].remove(deleted_transition)
                print(f"{deleted_transition.name} deleted")
        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


# TODO: Clean this method
def check_set_object_type(type_str_list, xml_function_list, xml_data_list, xml_state_list,
                          xml_transition_list, xml_fun_elem_list, xml_attribute_list,
                          xml_fun_inter_list, output_xml):
    """
    Check if each string in type_str_list are corresponding to an actual object's name/alias, create
    [object, type] lists for objects : Data/State/Function/Transition/FunctionalElement.
    Send lists to set_object_type() to write them within xml and then returns update_list from it.

        Parameters:
            type_str_list ([str]) : Lists of string from jarvis cell
            xml_function_list ([Function]) : function list from xml parsing
            xml_data_list ([Data]) : Data list from xml parsing
            xml_state_list ([State]) : State list from xml parsing
            xml_transition_list ([Transition]) : Transition list from xml parsing
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            xml_attribute_list ([Attribute]) : Attribute list from xml parsing
            xml_fun_inter_list ([FunctionalInterface]) : FunctionalInterface list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    object_from_xml_function_list = []
    object_from_xml_data_list = []
    object_from_xml_state_list = []
    object_from_xml_transition_list = []
    object_from_xml_fun_elem_list = []
    object_from_xml_attribute_list = []
    object_from_xml_fun_inter_list = []
    function_type_list = []
    state_type_list = []
    data_type_list = []
    transition_type_list = []
    fun_elem_type_list = []
    # Create object names/aliases lists
    xml_function_name_list = get_object_name(xml_function_list)
    xml_data_name_list = get_object_name(xml_data_list)
    xml_state_name_list = get_object_name(xml_state_list)
    xml_trnansition_name_list = get_object_name(xml_transition_list)
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)
    xml_attribute_name_list = get_object_name(xml_attribute_list)
    xml_fun_inter_name_list = get_object_name(xml_fun_inter_list)
    # Get __str__ list from FUNCTION_TYPE, DataType, StateType
    for i in datamodel.FunctionType:
        function_type_list.append(str(i).upper())
    for j in datamodel.DataType:
        data_type_list.append(str(j).upper())
    for k in datamodel.StateType:
        state_type_list.append(str(k).upper())
    for m in datamodel.TransitionType:
        transition_type_list.append(str(m).upper())
    for n in datamodel.FunctionalElementType:
        fun_elem_type_list.append(str(n).upper())

    concatenated_lists = [*xml_function_name_list, *xml_data_name_list, *xml_state_name_list,
                          *xml_trnansition_name_list, *xml_fun_elem_name_list,
                          *xml_attribute_name_list, *xml_fun_inter_name_list]
    concatenated_type_lists = [*function_type_list, *data_type_list, *state_type_list,
                               *transition_type_list, *fun_elem_type_list]
    no_specific_type_lists = [*xml_attribute_name_list, *xml_fun_inter_name_list]

    # Check if the wanted to object exists and the type can be set
    for object_to_set_type, type_name in type_str_list:
        is_elem_found = True
        if not any(s == object_to_set_type for s in concatenated_lists):
            is_elem_found = False
            print(f"The object {object_to_set_type} does not exist")
            # Else do nothing
        elif not any(s == type_name.upper() for s in concatenated_type_lists) and \
                not any(s == object_to_set_type for s in no_specific_type_lists):
            is_elem_found = False
            if object_to_set_type in xml_function_name_list:
                print(
                    f"The type {type_name} does not exist, available types are "
                    f": {', '.join(function_type_list)}.")
            elif object_to_set_type in xml_data_name_list:
                print(
                    f"The type {type_name} does not exist, available types are "
                    f": {', '.join(data_type_list)}.")
            elif object_to_set_type in xml_state_name_list:
                print(
                    f"The type {type_name} does not exist, available types are "
                    f": {', '.join(state_type_list)}.")
            elif object_to_set_type in xml_trnansition_name_list:
                print(
                    f"The type {type_name} does not exist, available types are "
                    f": {', '.join(transition_type_list)}.")
            elif object_to_set_type in xml_fun_elem_name_list:
                print(
                    f"The type {type_name} does not exist, available types are "
                    f": {', '.join(fun_elem_type_list)}.")
        if is_elem_found:
            if any(s == object_to_set_type for s in xml_attribute_name_list):
                for attribute in xml_attribute_list:
                    if object_to_set_type == attribute.name or \
                            object_to_set_type == attribute.alias:
                        if type_name != str(attribute.type):
                            object_from_xml_attribute_list.append([attribute, type_name])

            elif any(s == object_to_set_type for s in xml_fun_inter_name_list):
                for fun_inter in xml_fun_inter_list:
                    if object_to_set_type == fun_inter.name or \
                            object_to_set_type == fun_inter.alias:
                        if type_name != str(fun_inter.type):
                            object_from_xml_fun_inter_list.append([fun_inter, type_name])

            elif type_name.upper() in function_type_list:
                for fun in xml_function_list:
                    if object_to_set_type == fun.name or object_to_set_type == fun.alias:
                        if type_name.capitalize() != str(fun.type):
                            object_from_xml_function_list.append([fun, type_name.capitalize()])

            elif type_name.upper() in data_type_list:
                for d in xml_data_list:
                    if object_to_set_type == d.name:
                        if type_name.capitalize() != str(d.type):
                            object_from_xml_data_list.append([d, type_name.capitalize()])

            elif type_name.upper() in state_type_list:
                for sta in xml_state_list:
                    if object_to_set_type == sta.name or object_to_set_type == sta.alias:
                        if type_name.capitalize() != str(sta.type):
                            object_from_xml_state_list.append([sta, type_name.capitalize()])

            elif type_name.upper() in transition_type_list:
                for transition in xml_transition_list:
                    if object_to_set_type == transition.name or \
                            object_to_set_type == transition.alias:
                        if type_name.capitalize() != str(transition.type):
                            object_from_xml_transition_list.append([transition,
                                                                    type_name.capitalize()])

            elif type_name.upper() in fun_elem_type_list:
                for fun_elem in xml_fun_elem_list:
                    if object_to_set_type == fun_elem.name or object_to_set_type == fun_elem.alias:
                        if type_name.capitalize() != str(fun_elem.type):
                            object_from_xml_fun_elem_list.append([fun_elem, type_name.capitalize()])

            else:
                print(f"{object_to_set_type} can not be of type: {type_name}")

    object_type_lists = [object_from_xml_function_list, object_from_xml_data_list,
                         object_from_xml_state_list, object_from_xml_transition_list,
                         object_from_xml_fun_elem_list, object_from_xml_attribute_list,
                         object_from_xml_fun_inter_list]
    update_list = set_object_type(object_type_lists, output_xml)

    return update_list


def set_object_type(object_type_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            object_type_lists ([Object Data/State/Function/Transition/FunctionalElement, type]) :
            object with new type
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    if any(object_type_lists):
        new_type_in_xml_function_list = object_type_lists[0]
        new_type_in_xml_data_list = object_type_lists[1]
        new_type_in_xml_state_list = object_type_lists[2]
        new_type_in_xml_transition_list = object_type_lists[3]
        new_type_in_xml_fun_elem_list = object_type_lists[4]
        new_type_in_xml_attribute_list = object_type_lists[5]
        new_type_in_xml_fun_inter_list = object_type_lists[6]
        if new_type_in_xml_function_list:
            output_xml.write_function_type(new_type_in_xml_function_list)
            for elem in new_type_in_xml_function_list:
                elem[0].set_type(elem[1])
                elem[0].set_operand()
                print(f"The type of {elem[0].name} is {elem[0].type}")

        if new_type_in_xml_data_list:
            output_xml.write_data_type(new_type_in_xml_data_list)
            for data_type in new_type_in_xml_data_list:
                data_type[0].set_type(data_type[1])
                print(f"The type of {data_type[0].name} is {data_type[0].type}")

        if new_type_in_xml_state_list:
            output_xml.write_state_type(new_type_in_xml_state_list)
            for state_type in new_type_in_xml_state_list:
                state_type[0].set_type(state_type[1])
                print(f"The type of {state_type[0].name} is {state_type[0].type}")

        if new_type_in_xml_transition_list:
            output_xml.write_transition_type(new_type_in_xml_transition_list)
            for transition_type in new_type_in_xml_transition_list:
                transition_type[0].set_type(transition_type[1])
                print(f"The type of {transition_type[0].name} is {transition_type[0].type}")

        if new_type_in_xml_fun_elem_list:
            output_xml.write_fun_elem_type(new_type_in_xml_fun_elem_list)
            for fun_elem_type in new_type_in_xml_fun_elem_list:
                fun_elem_type[0].set_type(fun_elem_type[1])
                print(f"The type of {fun_elem_type[0].name} is {fun_elem_type[0].type}")

        if new_type_in_xml_attribute_list:
            output_xml.write_attribute_type(new_type_in_xml_attribute_list)
            for attribute_type in new_type_in_xml_attribute_list:
                attribute_type[0].set_type(attribute_type[1])
                print(f"The type of {attribute_type[0].name} is {attribute_type[0].type}")

        if new_type_in_xml_fun_inter_list:
            output_xml.write_fun_interface_type(new_type_in_xml_fun_inter_list)
            for fun_inter_type in new_type_in_xml_fun_inter_list:
                fun_inter_type[0].set_type(fun_inter_type[1])
                print(f"The type of {fun_inter_type[0].name} is {fun_inter_type[0].type}")

        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def check_set_object_alias(alias_str_list, xml_function_list, xml_state_list, xml_transition_list,
                           xml_fun_elem_list, xml_fun_inter_list, output_xml):
    """
    Check if each string in alias_str_list are corresponding to an actual object's name/alias,
    create [object, alias] lists for objects : State/Function/Transition/FunctionalElement.
    Send lists to set_object_alias() to write them within xml and then returns update_list from it.

        Parameters:
            alias_str_list ([str]) : Lists of string from jarvis cell
            xml_function_list ([Function]) : function list from xml parsing
            xml_state_list ([State]) : state list from xml parsing
            xml_transition_list ([Transition]) : Transition list from xml parsing
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            xml_fun_inter_list ([FunctionalINterface]) : functional interface list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    object_from_xml_function_list = []
    object_from_xml_state_list = []
    object_from_xml_transition_list = []
    object_from_xml_fun_elem_list = []
    object_from_xml_fun_inter_list = []
    # Create object names/aliases lists
    xml_function_name_list = get_object_name(xml_function_list)
    xml_state_name_list = get_object_name(xml_state_list)
    xml_transition_name_list = get_object_name(xml_transition_list)
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)
    xml_fun_inter_name_list = get_object_name(xml_fun_inter_list)

    concatenated_lists = [*xml_function_name_list, *xml_state_name_list, *xml_transition_name_list,
                          *xml_fun_elem_name_list, *xml_fun_inter_name_list]

    # Check if the wanted to object exists and the type can be set
    for object_to_set_alias, alias_name in alias_str_list:
        if not any(object_to_set_alias in s for s in concatenated_lists):
            print(f"The object {object_to_set_alias} does not exist")
        else:
            if object_to_set_alias in xml_function_name_list:
                for fun in xml_function_list:
                    if object_to_set_alias == fun.name or object_to_set_alias == fun.alias:
                        if fun.alias != alias_name:
                            object_from_xml_function_list.append([fun, alias_name])
                        # Else do nothing
            elif object_to_set_alias in xml_state_name_list:
                for sta in xml_state_list:
                    if object_to_set_alias == sta.name or object_to_set_alias == sta.alias:
                        if sta.alias != alias_name:
                            object_from_xml_state_list.append([sta, alias_name])
                        # Else do nothing
            elif object_to_set_alias in xml_transition_name_list:
                for transition in xml_transition_list:
                    if object_to_set_alias == transition.name or \
                            object_to_set_alias == transition.alias:
                        if transition.alias != alias_name:
                            object_from_xml_transition_list.append([transition, alias_name])
                        # Else do nothing
            elif object_to_set_alias in xml_fun_elem_name_list:
                for fun_elem in xml_fun_elem_list:
                    if object_to_set_alias == fun_elem.name or \
                            object_to_set_alias == fun_elem.alias:
                        if fun_elem.alias != alias_name:
                            object_from_xml_fun_elem_list.append([fun_elem, alias_name])

            elif object_to_set_alias in xml_fun_inter_name_list:
                for fun_inter in xml_fun_inter_list:
                    if object_to_set_alias == fun_inter.name or \
                            object_to_set_alias == fun_inter.alias:
                        if fun_inter.alias != alias_name:
                            object_from_xml_fun_inter_list.append([fun_inter, alias_name])

    output_lists = [object_from_xml_function_list, object_from_xml_state_list,
                    object_from_xml_transition_list, object_from_xml_fun_elem_list,
                    object_from_xml_fun_inter_list]
    update_list = set_object_alias(output_lists, output_xml)

    return update_list


def set_object_alias(object_alias_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            object_alias_lists ([Object State/Function/Transition/FunctionalElement, alias]) :
            object with new alias
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    if any(object_alias_lists):
        new_alias_in_xml_function_list = object_alias_lists[0]
        new_alias_in_xml_state_list = object_alias_lists[1]
        new_alias_in_xml_transition_list = object_alias_lists[2]
        new_alias_in_xml_fun_elem_list = object_alias_lists[3]
        new_alias_in_xml_fun_inter_list = object_alias_lists[4]
        if new_alias_in_xml_function_list:
            output_xml.write_function_alias(new_alias_in_xml_function_list)
            for elem in new_alias_in_xml_function_list:
                elem[0].set_alias(elem[1])
                print(f"The alias for {elem[0].name} is {elem[1]}")

        if new_alias_in_xml_state_list:
            output_xml.write_state_alias(new_alias_in_xml_state_list)
            for elem in new_alias_in_xml_state_list:
                elem[0].set_alias(elem[1])
                print(f"The alias for {elem[0].name} is {elem[1]}")

        if new_alias_in_xml_transition_list:
            output_xml.write_transition_alias(new_alias_in_xml_transition_list)
            for transition_alias in new_alias_in_xml_transition_list:
                transition_alias[0].set_alias(transition_alias[1])
                print(f"The alias for {transition_alias[0].name} is {transition_alias[1]}")

        if new_alias_in_xml_fun_elem_list:
            output_xml.write_fun_elem_alias(new_alias_in_xml_fun_elem_list)
            for fun_elem_alias in new_alias_in_xml_fun_elem_list:
                fun_elem_alias[0].set_alias(fun_elem_alias[1])
                print(f"The alias for {fun_elem_alias[0].name} is {fun_elem_alias[1]}")

        if new_alias_in_xml_fun_inter_list:
            output_xml.write_fun_interface_alias(new_alias_in_xml_fun_inter_list)
            for fun_inter_alias in new_alias_in_xml_fun_inter_list:
                fun_inter_alias[0].set_alias(fun_inter_alias[1])
                print(f"The alias for {fun_inter_alias[0].name} is {fun_inter_alias[1]}")

        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


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
    update_list = []
    state_list = set()
    # Create a list with all state names/aliases already in the xml
    xml_state_name = get_object_name(xml_state_list)
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
            state.set_type(datamodel.StateType.UNKNOWN)
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            state.set_id(str(identifier.int)[:10])
            # Add state to a set()
            xml_state_list.add(state)
            state_list.add(state)
        else:
            # print(state_name + " already exists (not added)")
            None
    if not state_list:
        update_list.append(0)
    else:
        output_xml.write_state(state_list)
        for state in state_list:
            print(state.name + " is a state")
        update_list.append(1)
    return update_list


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
    update_list = []
    transition_list = set()
    # Create a list with all transition's name already in the xml
    xml_transition_name_list = get_object_name(xml_transition_list)
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
            transition.set_type(datamodel.StateType.UNKNOWN)
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            transition.set_id(str(identifier.int)[:10])
            # Add state to a set()
            xml_transition_list.add(transition)
            transition_list.add(transition)
        else:
            # print(state_name + " already exists (not added)")
            None
    if not transition_list:
        update_list.append(0)
    else:
        output_xml.write_transition(transition_list)
        for transition in transition_list:
            print(transition.name + " is a transition")
        update_list.append(1)

    return update_list


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
    xml_transition_name_list = get_object_name(xml_transition_list)
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

    update_list = add_transition_condition(condition_list, output_xml)

    return update_list


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
    update_list = []
    if not condition_list:
        update_list.append(0)
    else:
        output_xml.write_transition_condition(condition_list)
        for elem in condition_list:
            elem[0].add_condition(elem[1])
            print(f"Condition for {elem[0].name} : {elem[1]}")
        update_list.append(1)

    return update_list


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
    xml_transition_name_list = get_object_name(xml_transition_list)
    xml_state_name_list = get_object_name(xml_state_list)

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
    update_list = add_src_dest(src_dest_lists, output_xml)

    return update_list


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
    update_list = []
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
        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def add_fun_elem_by_name(functional_elem_name_str_list, xml_fun_elem_list, output_xml):
    """
    Check if each string in functional_elem_name_str_list is not already corresponding to an actual
    object's name/alias, create new FunctionalElement() object, instantiate it, write it within
    XML and then returns update_list.

        Parameters:
            functional_elem_name_str_list ([str]) : Lists of string from jarvis cell
            xml_fun_elem_list ([FunctionalElement]) : FunctionalElement list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    functional_element_list = set()
    # Create a list with all functional element names/aliases already in the xml
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)
    # Loop on the list and create set for fun elem
    for fun_elem_name in functional_elem_name_str_list:
        if fun_elem_name not in xml_fun_elem_name_list:
            # Instantiate FunctionalElement
            fun_elem = datamodel.FunctionalElement()
            # Set FunctionalElement's name
            fun_elem.set_name(str(fun_elem_name))
            alias_str = re.search(r"(.*)\s[-]\s", fun_elem_name, re.MULTILINE)
            if alias_str:
                fun_elem.set_alias(alias_str.group(1))
            # Set FunctionalElement's type
            fun_elem.set_type(datamodel.StateType.UNKNOWN)
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            fun_elem.set_id(str(identifier.int)[:10])
            # Add FunctionalElement to a set()
            xml_fun_elem_list.add(fun_elem)
            functional_element_list.add(fun_elem)
        else:
            # print(fun_elem_name + " already exists (not added)")
            None

    if not functional_element_list:
        update_list.append(0)
    else:
        output_xml.write_functional_element(functional_element_list)
        for func_elem in functional_element_list:
            print(func_elem.name + " is a functional element")
        update_list.append(1)

    return update_list


def check_add_allocation(allocation_str_list, xml_fun_elem_list, xml_state_list, xml_function_list,
                         xml_fun_inter_list, xml_data_list,
                         xml_consumer_function_list, xml_producer_function_list, output_xml):
    """
    Check if each string in allocation_str_list are corresponding to an actual object, create new
    [FunctionalElement, allocated State/Function] lists.
    Send lists to add_allocation() to write them within xml and then returns update_list from it.

        Parameters:
            allocation_str_list ([str]) : Lists of string from jarvis cell
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            xml_state_list ([State]) : state list from xml parsing
            xml_function_list ([Function]) : function list from xml parsing
            xml_fun_inter_list ([FunctionalInterface]) : FunctionalInterface list from xml parsing
            xml_data_list ([Data]) : Data list from xml parsing
            xml_consumer_function_list ([flow_name, Function]): consumer's list
            xml_producer_function_list ([flow_name, Function]): producer's list
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    fun_elem_allocated_function_list = []
    fun_elem_allocated_state_list = []
    state_allocated_function_list = []
    fun_inter_allocated_data_list = []
    # Create lists with all object names/aliases already in the xml
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)
    xml_state_name_list = get_object_name(xml_state_list)
    xml_function_name_list = get_object_name(xml_function_list)
    xml_data_name_list = get_object_name(xml_data_list)
    xml_fun_inter_name_list = get_object_name(xml_fun_inter_list)

    concatenated_lists = [*xml_fun_elem_name_list, *xml_state_name_list, *xml_function_name_list,
                          *xml_data_name_list, *xml_fun_inter_name_list]
    available_objects_list = [*xml_state_name_list, *xml_function_name_list]

    # elem = [state/functional_element_name/alias, state/function_name/alias]
    for elem in allocation_str_list:
        is_elem_found = True
        if not all(t in concatenated_lists for t in elem):
            is_elem_found = False
            if any(s == elem[0] for s in xml_fun_elem_name_list) and not any(
                    j == elem[1] for j in available_objects_list):
                print(f"Object {elem[1]} does not exist")
            elif any(s == elem[1] for s in available_objects_list) and not any(
                    j == elem[0] for j in xml_fun_elem_name_list):
                print(f"Functional Element {elem[0]} does not exist")
            elif any(s == elem[1] for s in xml_data_name_list) and not any(
                    j == elem[0] for j in xml_fun_inter_name_list):
                print(f"Functional Interface {elem[0]} does not exist")
            elif any(s == elem[0] for s in xml_fun_inter_name_list) and not any(
                    j == elem[1] for j in xml_data_name_list):
                print(f"Data {elem[0]} does not exist")
            else:
                print(f"{elem[0]} and {elem[1]} do not exist")

        if is_elem_found:
            result_fun_elem_function = (elem[0] in xml_fun_elem_name_list) and (
                        elem[1] in xml_function_name_list)
            result_fun_elem_state = (elem[0] in xml_fun_elem_name_list) and (
                        elem[1] in xml_state_name_list)
            result_state_function = (elem[0] in xml_state_name_list) and (
                    elem[1] in xml_function_name_list)
            result_fun_inter_data = any(s == elem[0] for s in xml_fun_inter_name_list) and any(
                    s == elem[1] for s in xml_data_name_list)

            if result_fun_elem_function:
                for fun_elem in xml_fun_elem_list:
                    if elem[0] == fun_elem.name or elem[0] == fun_elem.alias:
                        for fun in xml_function_list:
                            if elem[1] == fun.name or elem[1] == fun.alias:
                                check_allocation = \
                                    get_allocation_object(fun, xml_fun_elem_list)
                                count = None
                                if check_allocation is not None:
                                    count = len(check_allocation)
                                    for item in check_allocation:
                                        if check_parentality(item, fun_elem):
                                            count -= 1
                                if count in (None, 0):
                                    fun_elem.add_allocated_function(fun.id)
                                    fun_elem_allocated_function_list.append([fun_elem, fun])

            elif result_fun_elem_state:
                for fun_elem in xml_fun_elem_list:
                    if elem[0] == fun_elem.name or elem[0] == fun_elem.alias:
                        for state in xml_state_list:
                            if elem[1] == state.name or elem[1] == state.alias:
                                check_allocation = \
                                    get_allocation_object(state, xml_fun_elem_list)
                                count = None
                                if check_allocation is not None:
                                    count = len(check_allocation)
                                    for item in check_allocation:
                                        if check_parentality(item, fun_elem):
                                            count -= 1
                                if count in (None, 0):
                                    fun_elem.add_allocated_state(state.id)
                                    fun_elem_allocated_state_list.append([fun_elem, state])

            elif result_state_function:
                for state in xml_state_list:
                    if elem[0] == state.name or elem[0] == state.alias:
                        for fun in xml_function_list:
                            if elem[1] == fun.name or elem[1] == fun.alias:
                                check_allocation = \
                                    get_allocation_object(fun, xml_state_list)
                                if check_allocation is None:
                                    state.add_allocated_function(fun.id)
                                    state_allocated_function_list.append([state, fun])
                                else:
                                    if state not in check_allocation:
                                        state.add_allocated_function(fun.id)
                                        state_allocated_function_list.append([state, fun])

            elif result_fun_inter_data:
                for fun_inter in xml_fun_inter_list:
                    if elem[0] == fun_inter.name or elem[0] == fun_inter.alias:
                        for data in xml_data_list:
                            if elem[1] == data.name:
                                check_allocation_fun_inter = \
                                    get_allocation_object(data, xml_fun_inter_list)
                                if check_allocation_fun_inter is None:
                                    check_fe = check_fun_elem_data_consumption(
                                        data, fun_inter,
                                        xml_fun_elem_list,
                                        xml_function_list,
                                        xml_consumer_function_list,
                                        xml_producer_function_list)
                                    if all(i for i in check_fe):
                                        fun_inter_allocated_data_list.append([fun_inter, data])
                                        fun_inter.add_allocated_data(data.id)
                                    elif True in check_fe:
                                        if check_fe[0] is True:
                                            print(f"Data {data.name} has only consumer(s) "
                                                  f"allocated to a functional element exposing "
                                                  f"{fun_inter.name}, {data.name} not "
                                                  f"allocated to {fun_inter.name}")
                                        elif check_fe[1] is True:
                                            print(f"Data {data.name} has only producer(s) "
                                                  f"allocated to a functional element exposing "
                                                  f"{fun_inter.name}, {data.name} not "
                                                  f"allocated to {fun_inter.name}")
                                    else:
                                        print(f"Data {data.name} has no producer(s) nor "
                                              f"consumer(s) allocated to functional elements "
                                              f"exposing {fun_inter.name}, {data.name} not "
                                              f"allocated to {fun_inter.name}")
            else:
                print(f"Available allocation types are: (State/Function with Functional Element) OR"
                      f" (State with Function) OR (Data with Functional Interface)")

    allocation_lists = [fun_elem_allocated_function_list, fun_elem_allocated_state_list,
                        state_allocated_function_list, [], fun_inter_allocated_data_list]
    update_list = add_allocation(allocation_lists, output_xml)

    return update_list


def check_fun_elem_data_consumption(data, fun_inter, fun_elem_list, function_list,
                                    xml_consumer_function_list, xml_producer_function_list,):
    fun_elem_exposes = set()
    for fun_elem in fun_elem_list:
        if any(a == fun_inter.id for a in fun_elem.exposed_interface_list):
            fun_elem_exposes.add(fun_elem)

    cons_list = False
    prod_list = False
    for function in function_list:
        for fun_elem in fun_elem_exposes:
            if any(a == function.id for a in fun_elem.allocated_function_list):
                fun_data = [data.name, function]
                if any(a == fun_data for a in xml_consumer_function_list):
                    cons_list = True
                if any(a == fun_data for a in xml_producer_function_list):
                    prod_list = True

    return [cons_list, prod_list]


def add_allocation(allocation_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made.

        Parameters:
            allocation_lists ([FunctionalElement, allocated State/Function]) : FunctionalElement
            with object to allocate
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    if any(allocation_lists):
        fun_elem_allocated_function_list = allocation_lists[0]
        fun_elem_allocated_state_list = allocation_lists[1]
        state_allocated_function_list = allocation_lists[2]
        chain_allocated_item_list = allocation_lists[3]
        fun_inter_allocated_data_list = allocation_lists[4]
        if fun_elem_allocated_function_list:
            output_xml.write_allocated_function(fun_elem_allocated_function_list)
            # Warn the user once added within xml
            for elem in fun_elem_allocated_function_list:
                print(f"{elem[1].__class__.__name__} {elem[1].name} is allocated to functional "
                      f"element {elem[0].name}")
                recursive_allocation(elem, output_xml)
        if fun_elem_allocated_state_list:
            output_xml.write_allocated_state(fun_elem_allocated_state_list)
            # Warn the user once added within xml
            for elem in fun_elem_allocated_state_list:
                print(f"{elem[1].__class__.__name__} {elem[1].name} is allocated to functional "
                      f"element {elem[0].name}")
                recursive_allocation(elem, output_xml)
        if state_allocated_function_list:
            output_xml.write_allocated_function_to_state(state_allocated_function_list)
            # Warn the user once added within xml
            for elem in state_allocated_function_list:
                print(f"{elem[1].__class__.__name__} {elem[1].name} is allocated to state "
                      f"{elem[0].name}")
                recursive_allocation(elem, output_xml)
        if chain_allocated_item_list:
            output_xml.write_allocated_chain_item(chain_allocated_item_list)
            # Warn the user once added within xml
            for elem in chain_allocated_item_list:
                print(f"{elem[1].__class__.__name__} {elem[1].name} is allocated to "
                      f"chain {elem[0].name}")
        if fun_inter_allocated_data_list:
            output_xml.write_fun_interface_allocated_data(fun_inter_allocated_data_list)
            # Warn the user once added within xml
            for elem in fun_inter_allocated_data_list:
                print(f"{elem[1].__class__.__name__} {elem[1].name} is allocated to "
                      f"functional interface {elem[0].name}")
        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def check_parent_allocation(elem, output_xml):
    if elem[0].parent is not None and elem[1].parent is not None:
        fun_elem_parent = elem[0].parent
        object_parent = elem[1].parent
        object_type = get_object_type(elem[1])
        check = False
        if object_type == "state":
            if object_parent.id in fun_elem_parent.allocated_state_list:
                check = True
        elif object_type == "function":
            if object_parent.id in fun_elem_parent.allocated_function_list:
                check = True
        if not check:
            answer = input(f"Do you also want to allocate parents(i.e. {object_parent.name} "
                           f"to {fun_elem_parent.name}) ?(Y/N)")
            if answer.lower() == "y":
                if object_type == "state":
                    output_xml.write_allocated_state([[fun_elem_parent, object_parent]])
                    fun_elem_parent.add_allocated_state(object_parent.id)
                    print(f"State {object_parent.name} is allocated to functional "
                          f"element {fun_elem_parent.name}")
                    check_parent_allocation([fun_elem_parent, object_parent], output_xml)
                elif object_type == "function":
                    output_xml.write_allocated_function([[fun_elem_parent, object_parent]])
                    fun_elem_parent.add_allocated_function(object_parent.id)
                    print(f"Function {object_parent.name} is allocated to functional "
                          f"element {fun_elem_parent.name}")
                    check_parent_allocation([fun_elem_parent, object_parent], output_xml)
            else:
                print(f"Error: {object_parent.name} is not allocated despite at least one "
                      f"of its child is")
                return
    else:
        return


def recursive_allocation(elem, output_xml):
    check_parent_allocation(elem, output_xml)
    object_type = get_object_type(elem[1])
    if elem[1].child_list:
        for i in elem[1].child_list:
            parent_child = [elem[1], i]
            allocated_child_list = get_allocated_child(parent_child, [elem[0]])
            if allocated_child_list:
                if object_type == "state":
                    output_xml.write_allocated_state(allocated_child_list)
                elif object_type == "function":
                    output_xml.write_allocated_function(allocated_child_list)
                for e in allocated_child_list:
                    if object_type == "state":
                        e[0].add_allocated_state(e[1].id)
                        print(f"State {e[1].name} is allocated to functional "
                              f"element {e[0].name}")
                    elif object_type == "function":
                        e[0].add_allocated_function(e[1].id)
                        print(f"Function {e[1].name} is allocated to functional "
                              f"element {e[0].name}")
                    if e[1].child_list:
                        recursive_allocation(e, output_xml)

    else:
        if object_type == "state" and elem[1].id not in elem[0].allocated_state_list:
            elem[0].add_allocated_state(elem[1].id)
            print(f"State {elem[1].name} is allocated to functional "
                  f"element {elem[0].name}")
        elif object_type == "function" and elem[1].id not in elem[0].allocated_function_list:
            elem[0].add_allocated_function(elem[1].id)
            print(f"Function {elem[1].name} is allocated to functional "
                  f"element {elem[0].name}")

    return None


def add_fun_inter_by_name(functional_inter_name_str_list, xml_fun_inter_list, output_xml):
    """
    Check if each string in functional_inter_name_str_list is not already corresponding to an actual
    object's name/alias, create new FunctionalInterface() object, instantiate it, write it
    within XML and then returns update_list.

        Parameters:
            functional_inter_name_str_list ([str]) : Lists of string from jarvis cell
            xml_fun_inter_list ([FunctionalInterface]) : FunctionalInterface list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update_list = []
    functional_interface_list = set()
    # Create a list with all functional interface names/aliases already in the xml
    xml_fun_inter_name_list = get_object_name(xml_fun_inter_list)
    # Loop on the list and create set for fun inter
    for fun_inter_name in functional_inter_name_str_list:
        if fun_inter_name not in xml_fun_inter_name_list:
            # Instantiate FunctionalInterface
            fun_inter = datamodel.FunctionalInterface()
            # Set FunctionalInterface's name
            fun_inter.set_name(str(fun_inter_name))
            alias_str = re.search(r"(.*)\s[-]\s", fun_inter_name, re.MULTILINE)
            if alias_str:
                fun_inter.set_alias(alias_str.group(1))
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            fun_inter.set_id(str(identifier.int)[:10])
            # Add FunctionalInterface to a set()
            xml_fun_inter_list.add(fun_inter)
            functional_interface_list.add(fun_inter)
        else:
            # print(fun_elem_name + " already exists (not added)")
            None

    if not functional_interface_list:
        update_list.append(0)
    else:
        output_xml.write_functional_interface(functional_interface_list)
        for func_inter in functional_interface_list:
            print(func_inter.name + " is a functional interface")
        update_list.append(1)

    return update_list


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
        fun_elem = check_get_object(exposes_str[0],
                                                    **{'xml_fun_elem_list': xml_fun_elem_list})
        fun_inter = check_get_object(exposes_str[1],
                                                     **{'xml_fun_inter_list': xml_fun_inter_list})

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
        return [1]
    else:
        return [0]


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
        if not check_parentality(opposite_fun_elem_list[idx],
                                                 opposite_fun_elem_list[idx+1]) and \
                not check_parentality(opposite_fun_elem_list[idx+1],
                                                      opposite_fun_elem_list[idx]):
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

