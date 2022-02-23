#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import copy
import re
import os
import sys
import uuid

# Modules
from . import question_answer
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
            print(fun.name + " is a function (added)")
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


def check_add_child(parent_child_name_str_list, xml_function_list, xml_parent_function_dict,
                    xml_state_list, xml_parent_state_dict, xml_fun_elem_list,
                    xml_parent_fun_elem_dict, output_xml):
    """
    Check if each string in parent_child_name_str_list are corresponding to an actual object,
    create new [parent, child] objects lists for object's type : State/Function/FunctionalElement.
    Send lists to add_child() to write them within xml and then returns update_list from it.

        Parameters:
            parent_child_name_str_list ([str]) : Lists of string from jarvis cell
            xml_function_list ([Function]) : function list from xml parsing
            xml_parent_function_dict ({child_function_id: parent_function_id}) : parent and child
            function's dict
            xml_state_list ([State]) : state list from xml parsing
            xml_parent_state_dict ({child_state_id: parent_state_id}) : parent and child state's
                                                                        dictionnary
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            xml_parent_fun_elem_dict ({child_fun_elem_id: parent_fun_elem_id}) : parent and child
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
                        parent_id = function.id
                        for fu in xml_function_list:
                            if elem[1] == fu.name or elem[1] == fu.alias:
                                child_parent_tuple = (fu.id, parent_id)
                                if child_parent_tuple not in xml_parent_function_dict.items():
                                    fu.set_parent(function)
                                    parent_child_function_list.append([function, fu])

            elif result_state:
                for state in xml_state_list:
                    if elem[0] == state.name or elem[0] == state.alias:
                        parent_id = state.id
                        for sta in xml_state_list:
                            if elem[1] == sta.name or elem[1] == sta.alias:
                                child_parent_tuple = (sta.id, parent_id)
                                if child_parent_tuple not in xml_parent_state_dict.items():
                                    sta.set_parent(state)
                                    parent_child_state_list.append([state, sta])

            elif result_fun_elem:
                for fun_elem in xml_fun_elem_list:
                    if elem[0] == fun_elem.name or elem[0] == fun_elem.alias:
                        parent_id = fun_elem.id
                        for fe in xml_fun_elem_list:
                            if elem[1] == fe.name or elem[1] == fe.alias:
                                child_parent_tuple = (fe.id, parent_id)
                                if child_parent_tuple not in xml_parent_fun_elem_dict.items():
                                    fe.set_parent(fun_elem)
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
                print(f"{i[0].name} is composed of {i[1].name} (added)")
                for fun_elem in xml_fun_elem_list:
                    if i[0].id in fun_elem.allocated_function_list:
                        recursive_allocation([fun_elem, i[1]], output_xml)

        if parent_child_state_list:
            output_xml.write_state_child(parent_child_state_list)
            # Warn the user once added within xml
            for i in parent_child_state_list:
                print(f"{i[0].name} is composed of {i[1].name} (added)")
                for fun_elem in xml_fun_elem_list:
                    if i[0].id in fun_elem.allocated_state_list:
                        recursive_allocation([fun_elem, i[1]], output_xml)

        if paren_child_fun_elem_list:
            output_xml.write_functional_element_child(paren_child_fun_elem_list)
            # Warn the user once added within xml
            for i in paren_child_fun_elem_list:
                print(f"{i[0].name} is composed of {i[1].name} (added)")

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
            print(data.name + " is a data" + " (added)")
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
        bad_list = []
        if elem[0] not in xml_data_name_list:
            is_elem_found = False
            for i in elem[1]:
                if i not in xml_data_name_list:
                    bad_list.append(i)
            if not bad_list:
                print(f"{elem[0]} does not exist")
            if bad_list:
                print(f"{elem[0]} and {bad_list} do not exist")
        if elem[0] in xml_data_name_list:
            for i in elem[1]:
                if i not in xml_data_name_list:
                    bad_list.append(i)
                    is_elem_found = False
            if bad_list:
                print(f"{bad_list} do(es) not exist")

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
            for future_predecessor in p:
                for da in xml_data_list:
                    if future_predecessor == da.name and da.id not in existing_predecessor_id_list:
                        predecessor = da
                if predecessor is not None and selected_data is not None:
                    data_predecessor_list.append([selected_data, predecessor])
            allocation_chain_1 = check_add_allocated_item(d, xml_data_list, xml_chain_list)
            if allocation_chain_1:
                allocated_item_list.append(allocation_chain_1)
            for elem in p:
                allocation_chain_2 = check_add_allocated_item(elem, xml_data_list, xml_chain_list)
                if allocation_chain_2:
                    allocated_item_list.append(allocation_chain_2)

    update_list = add_predecessor(data_predecessor_list, xml_data_list, output_xml)
    add_allocation([0, 0, 0, allocated_item_list], output_xml)

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
                          f"{data_predecessor[0].name} (added)")
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
        if elem[1] not in xml_function_name_list and elem[0] not in xml_data_name_list:
            is_elem_found = False
            print(f"{elem[1]} and {elem[0]} do not exist")
        elif elem[1] not in xml_function_name_list or elem[0] not in xml_data_name_list:
            is_elem_found = False
            if any(elem[1] in j for j in xml_function_name_list) and not any(
                        elem[0] in j for j in xml_data_name_list):
                print(f"{elem[0]} does not exist")
            elif any(elem[0] in j for j in xml_data_name_list) and not any(
                    elem[1] in j for j in xml_function_name_list):
                print(f"{elem[1]} does not exist")

        if is_elem_found:
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if elem[1] == function.name or elem[1] == function.alias:
                    if [elem[0], function] not in xml_consumer_function_list:
                        if [elem[0], function] not in xml_producer_function_list:
                            add_parent_for_data(elem[0], function,
                                                xml_consumer_function_list,
                                                new_consumer_list)
                        elif [elem[0], function] in xml_producer_function_list:
                            # TODO: Delete producer function, check if the flow isn't already
                            #  produces by another function and add consumer function if not
                            out = input(
                                f"Do you want to replace '{function.name} produces {elem[0]}' "
                                f"by '{function.name} consumes {elem[0]}' ? (Y/N) ")
                            if out == 'Y':
                                # output_xml.delete_single_consumer_producer(elem[0], function,
                                # relationship_type)
                                print('Not implemented yet')
                                # print(f"{function.name} consumes {elem[0]} (not added)")
                            elif out == 'N':
                                # print(f"{function.name} consumes {elem[0]} (not added)")
                                None
                            else:
                                print(f"'{out}' is not a valid command")

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
            print(f"{consumer[1].name} consumer for {consumer[0]} (added)")
        update_list.append(1)

    return update_list


def add_parent_for_data(flow, function, current_list, new_list):
    """
    Add direct parent's function of consumer/producer and delete internal flow if the case

        Parameters:
            flow (Data_name_str) : Data's name
            function (Function) : Current function
            current_list ([Data_name_str, function_name_str]) : 'Current' list
            new_list ([Data_name_str, Function]) : Data's name and consumer/producer's function list

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    new_list.append([flow, function])
    if function.parent is not None:
        elem = [flow, function.parent]
        if elem not in current_list and elem not in new_list:
            new_list.append(elem)


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
        if elem[1] not in xml_function_name_list and elem[0] not in xml_data_name_list:
            is_elem_found = False
            print(f"{elem[1]} and {elem[0]} do not exist")
        elif elem[1] not in xml_function_name_list or elem[0] not in xml_data_name_list:
            is_elem_found = False
            if any(elem[1] in j for j in xml_function_name_list) and not any(
                    elem[0] in j for j in xml_data_name_list):
                print(f"{elem[0]} does not exist")
            elif any(elem[0] in j for j in xml_data_name_list) and not any(
                    elem[1] in j for j in xml_function_name_list):
                print(f"{elem[1]} does not exist")

        if is_elem_found:
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if elem[1] == function.name or elem[1] == function.alias:
                    if [elem[0], function] not in xml_producer_function_list:
                        if [elem[0], function] not in xml_consumer_function_list:
                            add_parent_for_data(elem[0], function,
                                                xml_producer_function_list,
                                                new_producer_list)
                        elif [elem[0], function] in xml_consumer_function_list:
                            # TODO: Delete consumer function, check if the flow isn't already
                            #  produces by another function and add producer function if not
                            out = input(
                                f"Do you want to replace '{function.name} consumes {elem[0]}' "
                                f"by '{function.name} produces {elem[0]}' ? (Y/N) ")
                            if out == 'Y':
                                # output_xml.delete_single_consumer_producer(elem[0], function,
                                # relationship_type)
                                print('Not implemented yet')
                                # print(f"{function.name} produces {elem[0]} (not added)")
                            elif out == 'N':
                                # print(f"{function.name} produces {elem[0]} (not added)")
                                None
                            else:
                                print(f"'{out}' is not a valid command")
                    else:
                        # print(f"{function.name} already produces {elem[0]} (not added)")
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
            print(f"{producer[1].name} producer for {producer[0]} (added)")
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
        if not any(elem in s for s in concatenated_lists):
            print(f"{elem} does not exist")
        elif any(elem in flow_consumer for flow_consumer in xml_consumer_function_name_list):
            print(f"{elem} in [flow, consumer] list (not deleted)")
        elif any(elem in flow_producer for flow_producer in xml_producer_function_name_list):
            print(f"{elem} in [flow, producer] list (not deleted)")
        else:
            result_function = any(elem in s for s in xml_function_name_list)
            resul_state = any(elem in s for s in xml_state_name_list)
            result_data = any(elem in s for s in xml_data_name_list)
            result_fun_elem = any(elem in s for s in xml_fun_elem_name_list)
            result_transition = any(elem in s for s in xml_transition_name_list)
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


def check_set_object_type(type_str_list, xml_function_list, xml_data_list, xml_state_list,
                          xml_transition_list, xml_fun_elem_list, output_xml):
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
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    object_in_xml_function_list = []
    object_in_xml_data_list = []
    object_in_xml_state_list = []
    object_in_xml_transition_list = []
    object_in_xml_fun_elem_list = []
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
                          *xml_trnansition_name_list, *xml_fun_elem_name_list]
    concatenated_type_lists = [*function_type_list, *data_type_list, *state_type_list,
                               *transition_type_list, *fun_elem_type_list]

    # Check if the wanted to object exists and the type can be set
    for object_to_set_type, type_name in type_str_list:
        is_elem_found = True
        if not any(object_to_set_type in s for s in concatenated_lists):
            is_elem_found = False
            print(f"The object {object_to_set_type} does not exist")
            # Else do nothing
        elif not any(type_name.upper() in s for s in concatenated_type_lists):
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
            if type_name.upper() in function_type_list:
                for fun in xml_function_list:
                    if object_to_set_type == fun.name or object_to_set_type == fun.alias:
                        if type_name.capitalize() != str(fun.type):
                            object_in_xml_function_list.append([fun, type_name.capitalize()])
                        # Else do nothing
            elif type_name.upper() in data_type_list:
                for d in xml_data_list:
                    if object_to_set_type == d.name:
                        if type_name.capitalize() != str(d.type):
                            object_in_xml_data_list.append([d, type_name.capitalize()])

            elif type_name.upper() in state_type_list:
                for sta in xml_state_list:
                    if object_to_set_type == sta.name or object_to_set_type == sta.alias:
                        if type_name.capitalize() != str(sta.type):
                            object_in_xml_state_list.append([sta, type_name.capitalize()])

            elif type_name.upper() in transition_type_list:
                for transition in xml_transition_list:
                    if object_to_set_type == transition.name or object_to_set_type == transition.alias:
                        if type_name.capitalize() != str(transition.type):
                            object_in_xml_transition_list.append([transition, type_name.capitalize()])

            elif type_name.upper() in fun_elem_type_list:
                for fun_elem in xml_fun_elem_list:
                    if object_to_set_type == fun_elem.name or object_to_set_type == fun_elem.alias:
                        if type_name.capitalize() != str(fun_elem.type):
                            object_in_xml_fun_elem_list.append([fun_elem, type_name.capitalize()])

            else:
                print(f"{object_to_set_type} can not be of type: {type_name}")

    object_type_lists = [object_in_xml_function_list, object_in_xml_data_list, object_in_xml_state_list,
                         object_in_xml_transition_list, object_in_xml_fun_elem_list]
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
        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def check_set_object_alias(alias_str_list, xml_function_list, xml_state_list, xml_transition_list,
                           xml_fun_elem_list, output_xml):
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
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    object_in_xml_function_list = []
    object_in_xml_state_list = []
    object_in_xml_transition_list = []
    object_in_xml_fun_elem_list = []
    # Create object names/aliases lists
    xml_function_name_list = get_object_name(xml_function_list)
    xml_state_name_list = get_object_name(xml_state_list)
    xml_transition_name_list = get_object_name(xml_transition_list)
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)

    concatenated_lists = [*xml_function_name_list, *xml_state_name_list, *xml_transition_name_list,
                          *xml_fun_elem_name_list]

    # Check if the wanted to object exists and the type can be set
    for object_to_set_alias, alias_name in alias_str_list:
        if not any(object_to_set_alias in s for s in concatenated_lists):
            print(f"The object {object_to_set_alias} does not exist")
        else:
            if object_to_set_alias in xml_function_name_list:
                for fun in xml_function_list:
                    if object_to_set_alias == fun.name or object_to_set_alias == fun.alias:
                        if fun.alias != alias_name:
                            object_in_xml_function_list.append([fun, alias_name])
                        # Else do nothing
            elif object_to_set_alias in xml_state_name_list:
                for sta in xml_state_list:
                    if object_to_set_alias == sta.name or object_to_set_alias == sta.alias:
                        if sta.alias != alias_name:
                            object_in_xml_state_list.append([sta, alias_name])
                        # Else do nothing
            elif object_to_set_alias in xml_transition_name_list:
                for transition in xml_transition_list:
                    if object_to_set_alias == transition.name or object_to_set_alias == transition.alias:
                        if transition.alias != alias_name:
                            object_in_xml_transition_list.append([transition, alias_name])
                        # Else do nothing
            elif object_to_set_alias in xml_fun_elem_name_list:
                for fun_elem in xml_fun_elem_list:
                    if object_to_set_alias == fun_elem.name or object_to_set_alias == fun_elem.alias:
                        if fun_elem.alias != alias_name:
                            object_in_xml_fun_elem_list.append([fun_elem, alias_name])
                        # Else do nothing
    output_lists = [object_in_xml_function_list, object_in_xml_state_list,
                    object_in_xml_transition_list, object_in_xml_fun_elem_list]
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
        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def case_function_diagram(**kwargs):
    # Create object names/aliases list
    xml_fun_elem_name_list = get_object_name(kwargs['xml_fun_elem_list'])
    if kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        filename = show_fun_elem_function(kwargs['diagram_object_str'],
                                          kwargs['xml_fun_elem_list'],
                                          kwargs['xml_function_list'],
                                          kwargs['xml_consumer_function_list'],
                                          kwargs['xml_producer_function_list'])
        return filename
    else:
        print(f"Jarvis does not know the functional Element {kwargs['diagram_object_str']}")
        return


def case_context_diagram(**kwargs):
    # Create object names/aliases lists
    xml_function_name_list = get_object_name(kwargs['xml_function_list'])
    xml_state_name_list = get_object_name(kwargs['xml_state_list'])
    xml_fun_elem_name_list = get_object_name(kwargs['xml_fun_elem_list'])
    if kwargs['diagram_object_str'] in xml_function_name_list:
        filename = show_function_context(kwargs['diagram_object_str'], kwargs['xml_function_list'],
                                         kwargs['xml_consumer_function_list'],
                                         kwargs['xml_producer_function_list'],
                                         kwargs['xml_data_list'])
        return filename
    elif kwargs['diagram_object_str'] in xml_state_name_list:
        filename = show_states_chain([kwargs['diagram_object_str']], kwargs['xml_state_list'],
                                     kwargs['xml_transition_list'])
        return filename
    elif kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        filename = show_fun_elem_context(kwargs['diagram_object_str'], kwargs['xml_fun_elem_list'],
                                         kwargs['xml_function_list'],
                                         kwargs['xml_consumer_function_list'],
                                         kwargs['xml_producer_function_list'])
        return filename
    else:
        print(f"Jarvis does not know the function {kwargs['diagram_object_str']}")
        return


def case_decomposition_diagram(**kwargs):
    # Create object names/aliases lists
    xml_function_name_list = get_object_name(kwargs['xml_function_list'])
    xml_fun_elem_name_list = get_object_name(kwargs['xml_fun_elem_list'])
    if kwargs['diagram_object_str'] in xml_function_name_list:
        filename = show_function_decomposition(kwargs['diagram_object_str'],
                                               kwargs['xml_function_list'],
                                               kwargs['xml_consumer_function_list'],
                                               kwargs['xml_producer_function_list'])
        return filename
    elif kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        filename = show_fun_elem_decomposition(kwargs['diagram_object_str'],
                                               kwargs['xml_function_list'],
                                               kwargs['xml_consumer_function_list'],
                                               kwargs['xml_producer_function_list'],
                                               kwargs['xml_fun_elem_list'])
        return filename
    else:
        print(f"Jarvis does not know the object {kwargs['diagram_object_str']}"
              f"(i.e. it is not a function, nor a functional element)")
        return


def case_chain_diagram(**kwargs):
    # Create object names/aliases lists
    xml_function_name_list = get_object_name(kwargs['xml_function_list'])
    xml_state_name_list = get_object_name(kwargs['xml_state_list'])
    clean_diagram_object_str = kwargs['diagram_object_str'].replace(" ", "")
    object_list_str = re.split(r',(?![^[]*\])', clean_diagram_object_str)
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
                filename = show_functions_chain(object_list_str,
                                                kwargs['xml_function_list'],
                                                kwargs['xml_consumer_function_list'],
                                                kwargs['xml_producer_function_list'])
                return filename
            elif result_state:
                filename = show_states_chain(object_list_str, kwargs['xml_state_list'],
                                             kwargs['xml_transition_list'])
                return filename
        else:
            print(f"{kwargs['diagram_object_str']} is not a valid chain")
            return


def case_sequence_diagram(**kwargs):
    # Create object names/aliases list
    xml_function_name_list = get_object_name(kwargs['xml_function_list'])
    clean_diagram_object_str = kwargs['diagram_object_str'].replace(" ", "")
    function_list_str = re.split(r',(?![^[]*\])', clean_diagram_object_str)
    if len(function_list_str) > 0:
        bad_list = []
        for i in function_list_str:
            if len(i) > 0:
                if i not in xml_function_name_list:
                    print(f"{i} is not a function's name nor an alias")
                    bad_list.append(i)
            else:
                print(f"{kwargs['diagram_object_str']} is not a valid sequence")
        if not bad_list:
            xml_data_list = filter_allocated_item_from_chain(kwargs['xml_data_list'],
                                                             kwargs['xml_chain_list'])
            filename = show_functions_sequence(function_list_str,
                                               kwargs['xml_function_list'],
                                               kwargs['xml_consumer_function_list'],
                                               kwargs['xml_producer_function_list'],
                                               xml_data_list)
            return filename
        else:
            return


def case_state_diagram(**kwargs):
    # Create object names/aliases list
    xml_fun_elem_name_list = get_object_name(kwargs['xml_fun_elem_list'])
    if kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        filename = show_fun_elem_state_machine(kwargs['diagram_object_str'],
                                               kwargs['xml_state_list'],
                                               kwargs['xml_transition_list'],
                                               kwargs['xml_fun_elem_list'])
        return filename
    else:
        print(f"Jarvis does not know the functional Element {kwargs['diagram_object_str']}")
        return


def case_state_sequence_diagram(**kwargs):
    # Create object names/aliases list
    xml_state_name_list = get_object_name(kwargs['xml_state_list'])
    if kwargs['diagram_object_str'] in xml_state_name_list:
        filename = show_state_allocated_function(kwargs['diagram_object_str'],
                                                 kwargs['xml_state_list'],
                                                 kwargs['xml_function_list'],
                                                 kwargs['xml_consumer_function_list'],
                                                 kwargs['xml_producer_function_list'],
                                                 kwargs['xml_data_list'])
        return filename
    else:
        print(f"Jarvis does not know the State {kwargs['diagram_object_str']}")
        return None


def case_no_diagram(**kwargs):

    print(f"Jarvis does not understand the command {kwargs['diagram_type_str']}")


def switch_show_filter(**kwargs):
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


def filter_show_command(diagram_name_str, **kwargs):
    wanted_diagram_str = diagram_name_str.group(1)

    # TODO: Add to regex that it can also take the case (decomposition|context|chain)''
    #  in order to send specific user message for empty compo|context|chain
    regex = r"(decomposition|context|chain|sequence|state|function|state sequence)\s(.*)"
    specific_diagram_str = re.search(regex, wanted_diagram_str, re.MULTILINE)
    if specific_diagram_str:
        if 'sequence' not in specific_diagram_str.group(2):
            diagram_type_str = specific_diagram_str.group(1)
            diagram_object_str = specific_diagram_str.group(2)
        else:
            diagram_type_str = specific_diagram_str.group(1) + ' sequence'
            diagram_object_str = specific_diagram_str.group(2).replace("sequence ", "")

        filename = switch_show_filter(diagram_type_str=diagram_type_str,
                                      diagram_object_str=diagram_object_str,
                                      **kwargs)
        if filename:
            return filename

    else:
        print(f"Jarvis does not understand the command {wanted_diagram_str}")
        return


def check_level_0_allocated_child(fun_elem, function):
    if fun_elem.child_list == set():
        return True
    else:
        for fun_elem_child in fun_elem.child_list:
            if function.child_list != set():
                for function_child in function.child_list:
                    if function_child.id in fun_elem_child.allocated_function_list:
                        return False
                    elif function.id in fun_elem.allocated_function_list:
                        return False
                    else:
                        check_level_0_allocated_child(fun_elem_child, function_child)

            else:
                return True


def get_level_0_function(fun_elem, function_list, allocated_function_list=None):
    if allocated_function_list is None:
        allocated_function_list = set()
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
                                xml_producer_function_list, xml_fun_elem_list):
    main_fun_elem = None
    # main_fun_elem_list = set()
    external_function_list = set()
    new_producer_list = []
    new_consumer_list = []
    for fun_elem in xml_fun_elem_list:
        if fun_elem_str in (fun_elem.name, fun_elem.alias):
            fun_elem.parent = None
            main_fun_elem = fun_elem
            # main_fun_elem_list, main_parent_dict = get_children(fun_elem)

    allocated_function_list = get_level_0_function(main_fun_elem, xml_function_list)

    for allocated_function in allocated_function_list:
        for elem in xml_producer_function_list:
            if allocated_function in elem:
                new_producer_list.append(elem)
        for elem in xml_consumer_function_list:
            if allocated_function in elem:
                new_consumer_list.append(elem)

    for elem in new_consumer_list:
        if not any(elem[0] in s for s in new_producer_list):
            for t in xml_producer_function_list:
                if t[0] == elem[0] and t[1].parent is None:
                    external_function_list.add(t[1])
                    if t not in new_producer_list:
                        new_producer_list.append(t)

    for elem in new_producer_list:
        if not any(elem[0] in s for s in new_consumer_list):
            for t in xml_consumer_function_list:
                if t[0] == elem[0] and t[1].parent is None:
                    external_function_list.add(t[1])
                    if t not in new_consumer_list:
                        new_consumer_list.append(t)

    url_diagram = plantuml_adapter.get_fun_elem_decomposition(main_fun_elem, xml_fun_elem_list,
                                                              allocated_function_list,
                                                              new_consumer_list,
                                                              new_producer_list,
                                                              external_function_list)
    print("Decomposition Diagram for " + fun_elem_str + " generated")
    return url_diagram


def show_state_allocated_function(state_str, state_list, function_list, xml_consumer_function_list,
                                  xml_producer_function_list, xml_data_list):
    allocated_function_id_list = set()
    for state in state_list:
        if state_str in (state.name, state.alias):
            if not state.allocated_function_list:
                print(f"No function allocated to {state.name} (no display)")
                return
            else:
                state_name = state.name
                for s in state.allocated_function_list:
                    allocated_function_id_list.add(s)
    for function in function_list:
        if function.id in allocated_function_id_list.copy():
            allocated_function_id_list.remove(function.id)
            allocated_function_id_list.add(function.name)

    diagram_str = show_functions_sequence(allocated_function_id_list, function_list,
                                          xml_consumer_function_list, xml_producer_function_list,
                                          xml_data_list, True)

    diagram_str = f'box "{state_name}"\n' + diagram_str + "end box\n"
    url_diagram = plantuml_adapter.get_url_from_string(diagram_str)
    print("Function Sequence Diagram for " + state_str + " generated")
    return url_diagram


def show_fun_elem_function(fun_elem_str, xml_fun_elem_list, xml_function_list,
                           xml_consumer_function_list, xml_producer_function_list):

    allocated_function_id_list = set()
    new_function_list = set()
    new_fun_elem_list = set()
    new_consumer_list = []
    new_producer_list = []
    for fun_elem in xml_fun_elem_list:
        if fun_elem_str in (fun_elem.name, fun_elem.alias):
            if not fun_elem.allocated_function_list:
                print(f"No function allocated to {fun_elem.name} (no display)")
                return
            else:
                fun_elem.parent = None
                fun_elem.child_list.clear()
                new_fun_elem_list.add(fun_elem)
                for s in fun_elem.allocated_function_list:
                    allocated_function_id_list.add(s)

    for function_id in allocated_function_id_list:
        for fun in xml_function_list:
            if function_id == fun.id and fun.parent is None:
                new_function_list.add(fun)

    for f in new_function_list:
        for cons in xml_consumer_function_list:
            if f in cons and cons not in new_consumer_list:
                for prod in xml_producer_function_list:
                    if prod[0] == cons[0] and prod[1] in new_function_list:
                        new_consumer_list.append(cons)

    for f in new_function_list:
        for prod in xml_producer_function_list:
            if f in prod and prod not in new_producer_list:
                for cons in xml_consumer_function_list:
                    if cons[0] == prod[0] and cons[1] in new_function_list:
                        new_producer_list.append(prod)

    diagram_str, url_diagram = plantuml_adapter.plantuml_binder(new_function_list,
                                                                new_consumer_list,
                                                                new_producer_list,
                                                                {}, None)

    print("Function Diagram for " + fun_elem_str + " generated")
    return url_diagram


def show_fun_elem_context(fun_elem_str, xml_fun_elem_list, xml_function_list,
                          xml_consumer_function_list, xml_producer_function_list):
    allocated_function_id_list = set()
    allocated_function_list = set()
    new_function_list = set()
    cons = []
    prod = []
    for fun_elem in xml_fun_elem_list:
        if fun_elem_str in (fun_elem.name, fun_elem.alias):
            if not fun_elem.allocated_function_list:
                print(f"No function allocated to {fun_elem.name} (no display)")
                return
            else:
                for s in fun_elem.allocated_function_list:
                    allocated_function_id_list.add(s)

    for function_id in allocated_function_id_list:
        for fun in xml_function_list:
            if function_id == fun.id:
                allocated_function_list.add(fun)

    for i in allocated_function_list.copy():
        if i.parent is None:
            returned_list = show_function_context(i.name, allocated_function_list,
                                                  xml_consumer_function_list,
                                                  xml_producer_function_list, set(), list_out=True)
            for k in returned_list[0]:
                new_function_list.add(k)
            for c in returned_list[1]:
                if c not in cons:
                    cons.append(c)
            for p in returned_list[2]:
                if p not in prod:
                    prod.append(p)

    plant_uml_text, url_diagram = plantuml_adapter.plantuml_binder(new_function_list,
                                                                   cons,
                                                                   prod,
                                                                   {},
                                                                   set(),
                                                                   xml_fun_elem_list)
    print("Context Diagram for " + fun_elem_str + " generated")
    return url_diagram


def show_fun_elem_state_machine(fun_elem_str, xml_state_list, xml_transition_list,
                                xml_fun_elem_list):
    new_state_list = set()
    new_fun_elem_list = set()
    allocated_state_id_list = set()
    for fun_elem in xml_fun_elem_list:
        if fun_elem_str in (fun_elem.name, fun_elem.alias):
            if not fun_elem.allocated_state_list:
                print(f"No state allocated to {fun_elem.name} (no display)")
                return
            else:
                new_fun_elem_list.add(fun_elem)
                for s in fun_elem.allocated_state_list:
                    allocated_state_id_list.add(s)

    for state_id in allocated_state_id_list:
        for state in xml_state_list:
            if state_id == state.id:
                new_state_list.add(state)

    new_transition_list = get_transitions(new_state_list, xml_transition_list)

    plant_uml_text, url_diagram = plantuml_adapter.get_state_machine_diagram(new_state_list,
                                                                             new_transition_list,
                                                                             xml_fun_elem_list)
    print("State Machine Diagram for " + fun_elem_str + " generated")
    return url_diagram


def get_transitions(state_list, xml_transition_list):
    new_transition_list = set()
    for new_state in state_list:
        for transition in xml_transition_list:
            if new_state.id == transition.source:
                new_transition_list.add(transition)
            if new_state.id == transition.destination:
                new_transition_list.add(transition)

    return new_transition_list


def show_states_chain(state_list_str, xml_state_list, xml_transition_list):
    new_state_list = set()
    # To avoid alterate original objects => TBC if useful or not
    copied_xml_state_list = copy.deepcopy(xml_state_list)
    for state_str in state_list_str:
        for state in copied_xml_state_list:
            if state_str == state.name or state_str == state.alias:
                state.child_list.clear()
                state.set_parent(None)
                new_state_list.add(state)

    new_transition_list = get_transitions(new_state_list, xml_transition_list)

    plant_uml_text, url_diagram = plantuml_adapter.get_state_machine_diagram(new_state_list,
                                                                             new_transition_list)
    spaced_state_list = ", ".join(state_list_str)
    if len(state_list_str) == 1:
        print("Context Diagram " + str(spaced_state_list) + " generated")
    else:
        print("Chain Diagram " + str(spaced_state_list) + " generated")
    return url_diagram


def show_functions_sequence(function_list_str, xml_function_list, xml_consumer_function_list,
                            xml_producer_function_list, xml_data_list, str_out=False):
    new_function_list = set()
    new_parent_dict = {}
    new_producer_list = []
    new_consumer_list = []
    new_data_list = set()
    new_function_id_list = []
    for i in function_list_str:
        for fun in xml_function_list:
            if i == fun.name or i == fun.alias:
                fun.child_list.clear()
                new_function_list.add(fun)
                new_function_id_list.append(fun.id)

    for function in new_function_list:
        for xml_consumer_flow, xml_consumer in xml_consumer_function_list:
            if function == xml_consumer:
                for prod_flow, prod in xml_producer_function_list:
                    if prod_flow == xml_consumer_flow and prod in new_function_list and \
                            prod != function:
                        if [xml_consumer_flow, function] not in new_consumer_list:
                            new_consumer_list.append([xml_consumer_flow, function])

        for xml_producer_flow, xml_producer in xml_producer_function_list:
            if function == xml_producer:
                for cons_flow, cons in xml_consumer_function_list:
                    if cons_flow == xml_producer_flow and cons in new_function_list and \
                            cons != function:
                        if [xml_producer_flow, function] not in new_producer_list:
                            new_producer_list.append([xml_producer_flow, function])

    # TODO: Check if still usefull TBC/TBT
    for prod_elem in new_producer_list.copy():
        for cons_elem in new_consumer_list.copy():
            if cons_elem == prod_elem:
                new_producer_list.remove(prod_elem)
                new_consumer_list.remove(cons_elem)

    for prod_elem in new_producer_list:
        for data in xml_data_list:
            if data.name == prod_elem[0]:
                new_data_list.add(data)

    for cons_elem in new_consumer_list:
        for data in xml_data_list:
            if data.name == cons_elem[0]:
                new_data_list.add(data)

    for new_data in new_data_list:
        for pred in new_data.predecessor_list.copy():
            if pred not in new_data_list:
                new_data.predecessor_list.remove(pred)

    plant_uml_text, url_diagram = plantuml_adapter.get_sequence_diagram(new_function_list,
                                                                        new_consumer_list,
                                                                        new_producer_list,
                                                                        new_parent_dict,
                                                                        new_data_list)
    if str_out:
        out = plant_uml_text
    else:
        out = url_diagram
        spaced_function_list = ", ".join(function_list_str)
        print("Sequence Diagram " + str(spaced_function_list) + " generated")
    return out


def show_functions_chain(function_list_str, xml_function_list, xml_consumer_function_list,
                         xml_producer_function_list):
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
    plant_uml_text, url_diagram = plantuml_adapter.plantuml_binder(new_function_list,
                                                                   new_consumer_list,
                                                                   new_producer_list,
                                                                   new_parent_dict, None)
    spaced_function_list = ", ".join(function_list_str)
    print("Chain Diagram " + str(spaced_function_list) + " generated")
    return url_diagram


# TODO: Clean/organize this method by creating sub
def show_function_decomposition(diagram_function_str, xml_function_list, xml_consumer_function_list,
                                xml_producer_function_list, str_out=False, xml_fun_elem_list=None):
    main_function_list = set()
    ext_prod_fun_list = set()
    ext_cons_fun_list = set()
    ext_producer_list = []
    ext_consumer_list = []
    main_parent_dict = {}
    ext_prod_parent_dict = {}
    ext_cons_parent_dict = {}
    main_parent = None
    main_fun = None
    for fun in xml_function_list:
        if diagram_function_str == fun.name or diagram_function_str == fun.alias:
            main_parent = fun.parent
            main_fun = fun
            main_function_list, main_parent_dict = get_children(fun)

    main_consumer_list = check_get_child_flows(main_function_list, xml_consumer_function_list)
    main_producer_list = check_get_child_flows(main_function_list, xml_producer_function_list)

    for p, m in main_consumer_list:
        for xml_prod_flow, xml_prod in xml_producer_function_list:
            if p == xml_prod_flow and xml_prod not in main_function_list \
                    and xml_prod != main_parent and check_parentality(xml_prod, main_fun) is False:
                ext_prod_fun_list.add(xml_prod)
                if not xml_prod.child_list:
                    if [xml_prod_flow, xml_prod] not in ext_producer_list:
                        ext_producer_list.append([xml_prod_flow, xml_prod])
                else:
                    temp = []
                    for k in xml_prod.child_list:
                        temp.append([xml_prod_flow, k])
                    if not any(t in temp for t in xml_producer_function_list):
                        if [xml_prod_flow, xml_prod] not in ext_producer_list:
                            ext_producer_list.append([xml_prod_flow, xml_prod])

    for k in ext_prod_fun_list:
        if k.parent in ext_prod_fun_list:
            ext_prod_parent_dict[k.id] = k.parent.id

    for a, z in main_producer_list:
        for xml_cons_flow, xml_cons in xml_consumer_function_list:
            if a == xml_cons_flow and xml_cons not in main_function_list \
                    and xml_cons != main_parent and check_parentality(xml_cons, main_fun) is False:
                ext_cons_fun_list.add(xml_cons)
                if not xml_cons.child_list:
                    if [xml_cons_flow, xml_cons] not in ext_consumer_list:
                        ext_consumer_list.append([xml_cons_flow, xml_cons])
                else:
                    temp = []
                    for k in xml_cons.child_list:
                        temp.append([xml_cons_flow, k])
                    if not any(t in temp for t in xml_consumer_function_list):
                        if [xml_cons_flow, xml_cons] not in ext_consumer_list:
                            ext_consumer_list.append([xml_cons_flow, xml_cons])

    for e in ext_cons_fun_list:
        if e.parent in ext_cons_fun_list:
            ext_cons_parent_dict[e.id] = e.parent.id

    new_function_list = main_function_list.union(ext_prod_fun_list).union(ext_cons_fun_list)
    new_consumer_list = main_consumer_list + ext_consumer_list
    new_producer_list = main_producer_list + ext_producer_list
    new_parent_dict = {**main_parent_dict, **ext_cons_parent_dict, **ext_prod_parent_dict}

    for a in new_function_list:
        if main_parent and a.parent is main_parent:
            a.parent = None
        if a.child_list:
            for j in a.child_list.copy():
                if j not in new_function_list:
                    a.child_list.remove(j)

    plant_uml_text, url_diagram = plantuml_adapter.plantuml_binder(new_function_list,
                                                                   new_consumer_list,
                                                                   new_producer_list,
                                                                   new_parent_dict,
                                                                   None,
                                                                   xml_fun_elem_list)
    if str_out:
        out = plant_uml_text
    else:
        out = url_diagram
        print("Decomposition Diagram " + diagram_function_str + " generated")
    return out


def get_children(element, function_list=None, parent_dict=None):
    if function_list is None:
        function_list = set()
    if parent_dict is None:
        parent_dict = {}

    function_list.add(element)
    if element.child_list:
        for child in element.child_list:
            parent_dict[child.id] = element.id
            get_children(child, function_list, parent_dict)
    return function_list, parent_dict


def check_get_child_flows(function_list, xml_flow_list, new_flow_list=None):
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
                          xml_producer_function_list, xml_data_list, list_out=False):
    new_function_list = set()
    new_parent_dict = {}
    new_producer_list = []
    new_consumer_list = []
    main = None
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
                    if [xml_consumer_flow, xml_consumer] not in new_producer_list:
                        new_producer_list.append([xml_consumer_flow, xml_consumer])

    for f in new_function_list:
        f.child_list.clear()

    if list_out:
        out = new_function_list, new_consumer_list, new_producer_list
    else:
        plant_uml_text, url_diagram = plantuml_adapter.plantuml_binder(new_function_list,
                                                                       new_consumer_list,
                                                                       new_producer_list,
                                                                       new_parent_dict,
                                                                       xml_data_list)

        out = url_diagram
        print("Context Diagram " + diagram_function_str + " generated")
    return out


def check_parentality(a, b):
    """Check recursively if object 'a' is not parent of object 'b'"""
    if b.parent:
        if a == b.parent:
            return True
        else:
            return check_parentality(a, b.parent)
    else:
        return False


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
            print(state.name + " is a state (added)")
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
            print(transition.name + " is a transition (added)")
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
            print(f"Condition for {elem[0].name} : {elem[1]} (added)")
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
                print(f"{source[1].name} source for {source[0].name} (added)")

        if new_dest_list:
            output_xml.write_destination(new_dest_list)
            # Warn the user once writtent and added within xml
            for destination in new_dest_list:
                destination[0].set_destination(destination[1].id)
                print(f"{destination[1].name} destination for {destination[0].name} (added)")
        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def add_fun_elem_by_name(functional_elem_name_str_list, xml_fun_elem_list, output_xml):
    """
    Check if each string in functional_elem_name_str_list is not already corresponding to an actual
    object's name/alias, create new Transition() object, instantiate it, write it within XML and
    then returns update_list.

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
            print(func_elem.name + " is a functional element (added)")
        update_list.append(1)

    return update_list


def check_add_allocation(allocation_str_list, xml_fun_elem_list, xml_state_list, xml_function_list,
                         output_xml):
    """
    Check if each string in allocation_str_list are corresponding to an actual object, create new
    [FunctionalElement, allocated State/Function] lists.
    Send lists to add_allocation() to write them within xml and then returns update_list from it.

        Parameters:
            allocation_str_list ([str]) : Lists of string from jarvis cell
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            xml_state_list ([State]) : state list from xml parsing
            xml_function_list ([Function]) : function list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    fun_elem_allocated_function_list = []
    fun_elem_allocated_state_list = []
    state_allocated_function_list = []
    # Create lists with all object names/aliases already in the xml
    xml_fun_elem_name_list = get_object_name(xml_fun_elem_list)
    xml_state_name_list = get_object_name(xml_state_list)
    xml_function_name_list = get_object_name(xml_function_list)

    concatenated_lists = [*xml_fun_elem_name_list, *xml_state_name_list, *xml_function_name_list]
    available_objects_list = [*xml_state_name_list, *xml_function_name_list]

    # elem = [state/functional_element_name/alias, state/function_name/alias]
    for elem in allocation_str_list:
        is_elem_found = True
        if not all(t in concatenated_lists for t in elem):
            is_elem_found = False
            if any(elem[0] in s for s in xml_fun_elem_name_list) and not any(
                    elem[1] in j for j in available_objects_list):
                print(f"Object {elem[1]} does not exist")
            elif any(elem[1] in s for s in available_objects_list) and not any(
                    elem[0] in j for j in xml_fun_elem_name_list):
                print(f"Functional Element {elem[0]} does not exist")
            else:
                print(f"Functional element {elem[0]} and object {elem[1]} do not exist")

        if is_elem_found:
            result_fun_elem_function = (elem[0] in xml_fun_elem_name_list) and (
                        elem[1] in xml_function_name_list)
            result_fun_elem_state = (elem[0] in xml_fun_elem_name_list) and (
                        elem[1] in xml_state_name_list)
            result_state_function = (elem[0] in xml_state_name_list) and (
                    elem[1] in xml_function_name_list)
            if result_fun_elem_function:
                for fun_elem in xml_fun_elem_list:
                    if elem[0] == fun_elem.name or elem[0] == fun_elem.alias:
                        for fun in xml_function_list:
                            if elem[1] == fun.name or elem[1] == fun.alias:
                                check_allocation = \
                                    question_answer.get_allocation_object(fun, xml_fun_elem_list)
                                if check_allocation is None:
                                    fun_elem.add_allocated_function(fun.id)
                                    fun_elem_allocated_function_list.append([fun_elem, fun])

            elif result_fun_elem_state:
                for fun_elem in xml_fun_elem_list:
                    if elem[0] == fun_elem.name or elem[0] == fun_elem.alias:
                        for state in xml_state_list:
                            if elem[1] == state.name or elem[1] == state.alias:
                                check_allocation = \
                                    question_answer.get_allocation_object(state, xml_fun_elem_list)
                                if check_allocation is None:
                                    fun_elem.add_allocated_state(state.id)
                                    fun_elem_allocated_state_list.append([fun_elem, state])

            elif result_state_function:
                for state in xml_state_list:
                    if elem[0] == state.name or elem[0] == state.alias:
                        for fun in xml_function_list:
                            if elem[1] == fun.name or elem[1] == fun.alias:
                                check_allocation = \
                                    question_answer.get_allocation_object(fun, xml_state_list)
                                if not check_allocation:
                                    state.add_allocated_function(fun.id)
                                    state_allocated_function_list.append([state, fun])
                                elif check_allocation:
                                    if not any(state.name in s for s in check_allocation):
                                        state.add_allocated_function(fun.id)
                                        state_allocated_function_list.append([state, fun])
            else:
                print(f"Available allocation types are: (State/Function with Functional Element) OR"
                      f" (State with Function)")
    allocation_lists = [fun_elem_allocated_function_list, fun_elem_allocated_state_list,
                        state_allocated_function_list, []]
    update_list = add_allocation(allocation_lists, output_xml)

    return update_list


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
        if fun_elem_allocated_function_list:
            output_xml.write_allocated_function(fun_elem_allocated_function_list)
            # Warn the user once added within xml
            for elem in fun_elem_allocated_function_list:
                print(f"Function {elem[1].name} allocated to functional "
                      f"element {elem[0].name} (added)")
                recursive_allocation(elem, output_xml)
        if fun_elem_allocated_state_list:
            output_xml.write_allocated_state(fun_elem_allocated_state_list)
            # Warn the user once added within xml
            for elem in fun_elem_allocated_state_list:
                print(f"State {elem[1].name} allocated to functional "
                      f"element {elem[0].name} (added)")
                recursive_allocation(elem, output_xml)
        if state_allocated_function_list:
            output_xml.write_allocated_function_to_state(state_allocated_function_list)
            # Warn the user once added within xml
            for elem in state_allocated_function_list:
                print(f"Function {elem[1].name} allocated to state {elem[0].name} (added)")
                recursive_allocation(elem, output_xml)
        if chain_allocated_item_list:
            output_xml.write_allocated_chain_item(chain_allocated_item_list)
            # Warn the user once added within xml
            for elem in chain_allocated_item_list:
                print(f"{elem[1].__class__.__name__} {elem[1].name} allocated to "
                      f"chain {elem[0].name} (added)")
        update_list.append(1)
    else:
        update_list.append(0)

    return update_list


def get_object_type(object_to_check):
    if isinstance(object_to_check, datamodel.State):
        object_type = "state"
    elif isinstance(object_to_check, datamodel.Function):
        object_type = "function"
    elif isinstance(object_to_check, datamodel.Data):
        object_type = "data"
    elif isinstance(object_to_check, datamodel.FunctionalElement):
        object_type = "Functional element"
    else:
        object_type = ''

    return object_type


def recursive_parent_allocation(elem, output_xml):
    if elem[0].parent is not None:
        object_type = get_object_type(elem[1])
        fun_elem_item = [elem[0].parent, elem[1]]
        if object_type == "state":
            if elem[1] not in elem[0].parent.allocated_state_list:
                output_xml.write_allocated_state([fun_elem_item])
                elem[0].parent.add_allocated_state(elem[1].id)
                print(f"State {elem[1].name} allocated to functional "
                      f"element {elem[0].parent.name} (added)")
                return recursive_parent_allocation([elem[0].parent, elem[1]], output_xml)
        elif object_type == "function":
            if elem[1] not in elem[0].parent.allocated_function_list:
                output_xml.write_allocated_function([fun_elem_item])
                elem[0].parent.add_allocated_function(elem[1].id)
                print(f"Function {elem[1].name} allocated to functional "
                      f"element {elem[0].parent.name} (added)")
                return recursive_parent_allocation([elem[0].parent, elem[1]], output_xml)
    else:
        return


def recursive_allocation(elem, output_xml):
    recursive_parent_allocation(elem, output_xml)
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
                        print(f"State {e[1].name} allocated to functional "
                              f"element {e[0].name} (added)")
                    elif object_type == "function":
                        e[0].add_allocated_function(e[1].id)
                        print(f"Function {e[1].name} allocated to functional "
                              f"element {e[0].name} (added)")
                    if e[1].child_list:
                        return recursive_allocation(e, output_xml)
    else:
        if object_type == "state" and elem[1].id not in elem[0].allocated_state_list:
            elem[0].add_allocated_state(elem[1].id)
            print(f"State {elem[1].name} allocated to functional "
                  f"element {elem[0].name} (added)")
        elif object_type == "function" and elem[1].id not in elem[0].allocated_function_list:
            elem[0].add_allocated_function(elem[1].id)
            print(f"Function {elem[1].name} allocated to functional "
                  f"element {elem[0].name} (added)")

    return None


# Method that returns a list with all object aliases/names
def get_object_name(xml_object_list):
    object_name_list = []
    # Create the xml [object_name (and object_alias)] list
    for xml_object in xml_object_list:
        object_name_list.append(xml_object.name)
        try:
            if len(xml_object.alias) > 0:
                object_name_list.append(xml_object.alias)
        except AttributeError:
            # To avoid error when there is no alias attribute for the object
            None

    return object_name_list


def add_chain(chain_name_str, xml_chain_list, output_xml):
    """
        Check if each string in chain_name_str is not already corresponding to an actual
        object's name, create new Chain() object, instantiate it, write it within XML and
        then returns update_list.

            Parameters:
                chain_name_str ([str]) : Lists of string from jarvis cell
                xml_chain_list ([Function]) : chain list from xml parsing
                output_xml (GenerateXML object) : XML's file object

            Returns:
                update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
        """
    update_list = []
    chain_list = set()
    # Create a list with all chain names already in the xml
    xml_chain_name_list = get_object_name(xml_chain_list)
    # Loop on the list and create set for functions
    if chain_name_str not in xml_chain_name_list:
        # Instantiate chain class and chain
        chain = datamodel.Chain()
        # Set chain's name
        chain.set_name(str(chain_name_str))
        # Set chain's type
        chain.set_type(datamodel.ChainType.UNKNOWN)
        # Generate and set unique identifier of length 10 integers
        identifier = uuid.uuid4()
        chain.set_id(str(identifier.int)[:10])
        # Add chain to new set() and existing et() from xml
        xml_chain_list.add(chain)
        chain_list.add(chain)
        activate_chain(chain.name, xml_chain_list)
    elif chain_name_str in xml_chain_name_list:
        # print(chain_name + " already exists (not added)")
        activate_chain(chain_name_str, xml_chain_list)

    if not chain_list:
        update_list.append(0)
    else:
        output_xml.write_chain(chain_list)
        for chain in chain_list:
            print(chain.name + " is a chain (added)")
        update_list.append(1)

    return update_list


def activate_chain(chain_name, xml_chain_list):
    for chain in xml_chain_list:
        if chain_name == chain.name:
            chain.set_activation(True)
        else:
            chain.set_activation(False)


def check_add_allocated_item(item, xml_item_list, xml_chain_list):
    if not any(s.activated for s in xml_chain_list):
        return
    else:
        activated_chain = None
        for chain in xml_chain_list:
            if chain.activated:
                activated_chain = chain
        if activated_chain:
            for i in xml_item_list:
                if item == i.name:
                    if i.id not in activated_chain.allocated_item_list:
                        activated_chain.add_allocated_item(i.id)
                        return [activated_chain, i]


def filter_allocated_item_from_chain(xml_item_list, xml_chain_list):
    if not any(j.activated for j in xml_chain_list):
        return xml_item_list
    else:
        filtered_items_list = []
        for j in xml_chain_list:
            if j.activated:
                for item in xml_item_list:
                    if item.id in j.allocated_item_list:
                        filtered_items_list.append(item)
        return filtered_items_list
