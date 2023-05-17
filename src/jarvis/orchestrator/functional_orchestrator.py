#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module with methods relative to Functional section"""
# Libraries

# Modules
import datamodel
from . import shared_orchestrator
from jarvis import question_answer
from jarvis import util
from tools import Logger


def check_add_predecessor(data_predecessor_str_set, xml_data_list, xml_view_list, output_xml):
    """
    Check if each string in data_predecessor_str_set is corresponding to an actual Data object,
    create new [Data, predecessor] objects lists for object's type : Data.
    Send lists to add_predecessor() to write them within xml and then returns update_list from it.

        Parameters:
            data_predecessor_str_set ([str]) : Lists of string from jarvis cell
            xml_data_list ([Data]) : Data list from xml parsing
            xml_view_list ([View]) : View list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    data_predecessor_list = []

    allocated_item_list = []
    # Filter input string
    data_predecessor_str_list = util.cut_tuple_list(data_predecessor_str_set)

    # Create data names list already in xml
    xml_data_name_list = question_answer.get_objects_names(xml_data_list)

    for elem in data_predecessor_str_list:
        is_elem_found = True
        if elem[0] not in xml_data_name_list:
            is_elem_found = False
            if elem[1] not in xml_data_name_list:
                Logger.set_error(__name__,
                                 f"{elem[0]} and {elem[1]} do not exist")
            else:
                Logger.set_error(__name__,
                                 f"{elem[0]} does not exist")

        if elem[0] in xml_data_name_list:
            if elem[1] not in xml_data_name_list:
                is_elem_found = False
                Logger.set_error(__name__,
                                 f"{elem[1]} does not exist")

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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """

    if not predecessor_list:
        return 0

    output_xml.write_data_predecessor(predecessor_list)

    for data_predecessor in predecessor_list:
        for d in xml_data_list:
            if data_predecessor[0].id == d.id:
                d.add_predecessor(data_predecessor[1])

        Logger.set_info(__name__,
                        f"{data_predecessor[1].name} predecessor for "
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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    new_consumer_list = []
    # Create object names/aliases list and data's name
    xml_function_name_list = question_answer.get_objects_names(xml_function_list)
    xml_data_name_list = question_answer.get_objects_names(xml_data_list)
    # Loop to filter consumer and create a new list
    for elem in consumer_str_list:
        is_elem_found = True
        if not any(item == elem[1] for item in xml_function_name_list) and \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            Logger.set_error(__name__,
                             f"{elem[1]} and {elem[0]} do not exist")
        elif not any(item == elem[1] for item in xml_function_name_list) or \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            if any(item == elem[1] for item in xml_function_name_list) and \
                    not any(item == elem[0] for item in xml_data_name_list):
                Logger.set_error(__name__,
                                 f"{elem[0]} does not exist")
            elif any(item == elem[0] for item in xml_data_name_list) and \
                    not any(item == elem[1] for item in xml_function_name_list):
                Logger.set_error(__name__,
                                 f"{elem[1]} does not exist")

        if is_elem_found:
            Logger.set_debug(__name__, f"[{elem[0]}, {elem[1]}] check")
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if elem[1] == function.name or elem[1] == function.alias:
                    if [elem[0], function] not in xml_consumer_function_list:
                        add_producer_consumer_flow_recursively(elem[0],
                                                               function,
                                                               xml_consumer_function_list,
                                                               xml_producer_function_list,
                                                               new_consumer_list,
                                                               output_xml,
                                                               "consumer")
                    break

    Logger.set_debug(__name__, f"{consumer_str_list}: {new_consumer_list}")
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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """

    if not new_consumer_list:
        return 0

    # TODO : new_producer_list to be [data, function] and not [data_name, function]
    output_xml.write_data_consumer(new_consumer_list)

    # Warn the user once added within xml
    for consumer in new_consumer_list:
        xml_consumer_function_list.append(consumer)
        Logger.set_info(__name__,
                        f"{consumer[1].name} consumes {consumer[0]}")

    return 1


def add_producer_consumer_flow_recursively(flow, function, current_list, opposite_list, new_list, output_xml,
                                           relationship_str):
    """
    Recursive method to add producer / consumer function for a flow.
        Parameters:
            flow (Data_name_str) : Data's name
            function (Function) : Current function's parent
            current_list ([Data_name_str, function_name_str]) : 'Current' list (producer/consumer)
            opposite_list ([Data_name_str, function_name_str]) : Opposite list from current
            new_list ([Data_name_str, Function]) : Data's name and consumer/producer's function list
            output_xml (XmlWriter3SE object) : XML's file object
            relationship_str (str) : "consumer" or "producer"
            out (bool) : List for recursivity
        Returns:
            elem ([data, Function]) : Return parent

    """
    # Prevent function.parent to be added twice
    if [flow, function] not in new_list and [flow, function] not in current_list:
        new_list.append([flow, function])
        Logger.set_debug(__name__, f"[{flow}, {function.name}] added")

        # Check that parent opposite flow is present (if any)
        is_opposite = False
        for [opposite_flow, opposite_function] in opposite_list:
            if opposite_flow == flow:
                is_opposite = True
                if opposite_function.parent is not None and opposite_function.parent != function and \
                        opposite_function.parent != function.parent:
                    if [opposite_flow, opposite_function.parent] not in opposite_list:
                        add_producer_consumer_opposite(flow, opposite_function.parent, opposite_list, output_xml,
                                                       relationship_str)

        if not is_opposite:
            if relationship_str == "consumer":
                Logger.set_warning(__name__, f"No producer found for {flow}")
            elif relationship_str == "producer":
                Logger.set_warning(__name__, f"No consumer found for {flow}")
            else:
                Logger.set_error(__name__, f"Unsupported data relationship type: {relationship_str}")

    if function.parent is not None:
        parent_child_list, parent_child_dict = question_answer.get_children(function.parent)

        if not any([flow, parent_child] in opposite_list for parent_child in parent_child_list):
            add_producer_consumer_flow_recursively(flow, function.parent, current_list, opposite_list, new_list,
                                                   output_xml,
                                                   relationship_str)
        elif [flow, function.parent] in opposite_list:
            # Check that no other function needs the flow before removing it
            ext_function_list = []
            for [current_flow, current_function] in current_list:
                if current_flow == flow:
                    Logger.set_debug(__name__, f"[{current_flow}, {current_function.name}] "
                                               f"added in external function list")
                    ext_function_list.append([current_flow, current_function])

            for parent_child in parent_child_list:
                if [flow, parent_child] in ext_function_list:
                    ext_function_list.remove([flow, parent_child])

            if len(ext_function_list) == 0:
                remove_producer_consumer_opposite(flow, function.parent, opposite_list, output_xml, relationship_str)
            else:
                Logger.set_debug(__name__, f"[{flow}, {function.parent.name}] still needed")


def add_producer_consumer_opposite(flow, function, flow_function_list, output_xml, relationship_type):
    """
    Add specific consumer/producer relationship within xml's file.

        Parameters:
            flow (Data_name_str) : Data's name
            function (Function) : Current Function object
            flow_function_list : list of [flow, function]
            output_xml (XmlWriter3SE object) : XML's file object
            relationship_type (str) : Type of relationship (i.e. consumer or producer)
        Returns:
            None
    """
    flow_function_list.append([flow, function])

    if relationship_type == "producer":
        output_xml.write_data_relationship([flow, function],
                                           "consumer")
        Logger.set_info(__name__,
                        f"{function.name} consumes {flow} due to one of its children")
    elif relationship_type == "consumer":

        output_xml.write_data_relationship([flow, function],
                                           "producer")
        Logger.set_info(__name__,
                        f"{function.name} produces {flow} due to one of its children")

    if function.parent:
        add_producer_consumer_opposite(flow, function.parent, flow_function_list, output_xml, relationship_type)


def remove_producer_consumer_opposite(flow, function, flow_function_list, output_xml, relationship_type):
    """
    Delete specific consumer/producer relationship within xml's file.

        Parameters:
            flow (Data_name_str) : Data's name
            function (Function) : Current Function object
            flow_function_list : list of [flow, function]
            output_xml (XmlWriter3SE object) : XML's file object
            relationship_type (str) : Type of relationship (i.e. consumer or producer)
        Returns:
            None
    """
    flow_function_list.remove([flow, function])

    if relationship_type == "producer":
        output_xml.delete_data_relationship([flow, function],
                                            "consumer")
        Logger.set_info(__name__,
                        f"{function.name} does not consume {flow} anymore")
    elif relationship_type == "consumer":

        output_xml.delete_data_relationship([flow, function],
                                            "producer")
        Logger.set_info(__name__,
                        f"{function.name} does not produce {flow} anymore")

    if function.parent and [flow, function.parent] in flow_function_list:
        remove_producer_consumer_opposite(flow, function.parent, flow_function_list, output_xml, relationship_type)


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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    new_producer_list = []
    # Create object names/aliases list
    xml_function_name_list = question_answer.get_objects_names(xml_function_list)
    xml_data_name_list = question_answer.get_objects_names(xml_data_list)
    # Loop to filter producer and create a new list
    for elem in producer_str_list:
        is_elem_found = True
        if not any(item == elem[1] for item in xml_function_name_list) and \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            Logger.set_error(__name__,
                             f"{elem[1]} and {elem[0]} do not exist")
        elif not any(item == elem[1] for item in xml_function_name_list) or \
                not any(item == elem[0] for item in xml_data_name_list):
            is_elem_found = False
            if any(item == elem[1] for item in xml_function_name_list) and \
                    not any(item == elem[0] for item in xml_data_name_list):
                Logger.set_error(__name__,
                                 f"{elem[0]} does not exist")
            elif any(item == elem[0] for item in xml_data_name_list) and \
                    not any(item == elem[1] for item in xml_function_name_list):
                Logger.set_error(__name__,
                                 f"{elem[1]} does not exist")

        if is_elem_found:
            Logger.set_debug(__name__, f"[{elem[0]}, {elem[1]}] check")
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if elem[1] == function.name or elem[1] == function.alias:
                    if [elem[0], function] not in xml_producer_function_list:
                        add_producer_consumer_flow_recursively(elem[0],
                                                               function,
                                                               xml_producer_function_list,
                                                               xml_consumer_function_list,
                                                               new_producer_list,
                                                               output_xml,
                                                               "producer")
                    break

    Logger.set_debug(__name__, f"{producer_str_list}: {new_producer_list}")
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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if not new_producer_list:
        return 0

    # TODO : new_producer_list to be [data, function] and not [data_name, function]
    output_xml.write_data_producer(new_producer_list)
    # Warn the user once added within xml
    for producer in new_producer_list:
        xml_producer_function_list.append(producer)
        Logger.set_info(__name__,
                        f"{producer[1].name} produces {producer[0]}")
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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    condition_list = []
    # Create a list with all transition names/aliases already in the xml
    xml_transition_name_list = question_answer.get_objects_names(xml_transition_list)
    for transition_str, condition_str in trans_condition_str_list:
        is_elem_found = True
        if not any(transition_str in s for s in xml_transition_name_list):
            is_elem_found = False
            Logger.set_error(__name__,
                             f"The transition {transition_str} does not exist")

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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if not condition_list:
        return 0

    output_xml.write_transition_condition(condition_list)
    for elem in condition_list:
        elem[0].add_condition(elem[1])
        Logger.set_info(__name__,
                        f"Condition for {elem[0].name} : {elem[1]}")
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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    new_src_list = []
    new_dest_list = []
    # Create lists with all object names/aliases already in the xml
    xml_transition_name_list = question_answer.get_objects_names(xml_transition_list)
    xml_state_name_list = question_answer.get_objects_names(xml_state_list)

    concatenated_lists = [*xml_transition_name_list, *xml_state_name_list]

    # elem = [source/destination, transition_name, state_name]
    for elem in src_dest_str:
        is_elem_found = True
        if not all(t in concatenated_lists for t in [elem[1], elem[2]]):
            is_elem_found = False
            if any(elem[1] in s for s in xml_transition_name_list) and not any(
                    elem[2] in j for j in xml_state_name_list):
                Logger.set_error(__name__,
                                 f"{elem[2]} state does not exist")
            elif any(elem[2] in s for s in xml_state_name_list) and not any(
                    elem[1] in j for j in xml_transition_name_list):
                Logger.set_error(__name__,
                                 f"{elem[1]} transition does not exist")
            else:
                Logger.set_error(__name__,
                                 f"{elem[1]} transition and {elem[2]} state do not exist")

        if is_elem_found:
            if elem[0] == "source":
                for transition in xml_transition_list:
                    if elem[1] == transition.name or elem[1] == transition.alias:
                        for state in xml_state_list:
                            if elem[2] == state.name or elem[2] == state.alias:
                                if not isinstance(state.type, datamodel.BaseType):
                                    if 'EXIT' in state.type.name:
                                        Logger.set_error(__name__,
                                                         f"{elem[2]} is typed as EXIT state, "
                                                         f"it cannot be put as source's transition (not added)")
                                else:
                                    if transition.source != state.id:
                                        new_src_list.append([transition, state])

            elif elem[0] == "destination":
                for transition in xml_transition_list:
                    if elem[1] == transition.name or elem[1] == transition.alias:
                        for state in xml_state_list:
                            if elem[2] == state.name or elem[2] == state.alias:
                                if not isinstance(state.type, datamodel.BaseType):
                                    if 'ENTRY' in state.type.name:
                                        Logger.set_error(__name__,
                                                         f"{elem[2]} is typed as ENTRY state, it cannot be "
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
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if any(src_dest_lists):
        new_src_list = src_dest_lists[0]
        new_dest_list = src_dest_lists[1]
        if new_src_list:
            output_xml.write_transition_source(new_src_list)
            # Warn the user once writtent and added within xml
            for source in new_src_list:
                source[0].set_source(source[1].id)
                Logger.set_info(__name__,
                                f"{source[1].name} source for {source[0].name}")

        if new_dest_list:
            output_xml.write_transition_destination(new_dest_list)
            # Warn the user once writtent and added within xml
            for destination in new_dest_list:
                destination[0].set_destination(destination[1].id)
                Logger.set_info(__name__,
                                f"{destination[1].name} destination for {destination[0].name}")
        return 1

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
        output_xml (XmlWriter3SE object) : XML's file object

    Returns:
        [0/1] : if update has been made
    """
    # TODO : add physical interface support (see write_element_exposed_interface())
    output = False
    cleaned_exposes_str_list = util.cut_tuple_list(exposes_str_list)
    for exposes_str in cleaned_exposes_str_list:
        fun_elem = question_answer.check_get_object(exposes_str[0], **{'xml_fun_elem_list': xml_fun_elem_list})
        fun_inter = question_answer.check_get_object(exposes_str[1], **{'xml_fun_inter_list': xml_fun_inter_list})

        check_print_wrong_pair_object((exposes_str[0], fun_elem, 'Functional Element'),
                                      (exposes_str[1], fun_inter, 'Functional Interface'),
                                      'exposes')
        if fun_elem and fun_inter:
            check_rule = check_fun_elem_inter_families(fun_elem, fun_inter, xml_fun_elem_list)
            if fun_inter.id not in fun_elem.exposed_interface_list and check_rule:
                output = True
                fun_elem.add_exposed_interface(fun_inter.id)
                output_xml.write_element_exposed_interface([[fun_elem, fun_inter]])
                Logger.set_info(__name__,
                                f"{fun_elem.name} exposes {fun_inter.name}")

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
        if question_answer.check_parentality(elem, fun_elem) or \
                question_answer.check_parentality(fun_elem, elem):
            return check
        else:
            opposite_fun_elem_list.append(elem)

    for idx in range(0, len(opposite_fun_elem_list) - 1):
        if not question_answer.check_parentality(
                opposite_fun_elem_list[idx], opposite_fun_elem_list[idx + 1]) and \
                not question_answer.check_parentality(opposite_fun_elem_list[idx + 1], opposite_fun_elem_list[idx]):
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
        Logger.set_error(__name__,
                         f"{object_a[0]} and {object_b[0]} do not exist, choose valid names/aliases for: "
                         f"'{object_a[2]}' {relationship_type} "
                         f"'{object_b[2]}'")
    elif object_a[1] is None or object_b[1] is None:
        if object_a[1] is None and object_b[1]:
            Logger.set_error(__name__,
                             f"{object_a[0]} does not exist, choose a valid name/alias for: "
                             f"'{object_a[2]}' {relationship_type} "
                             f"{object_b[1].name}")
        elif object_b[1] is None and object_a[1]:
            Logger.set_error(__name__,
                             f"{object_b[0]} does not exist, choose a valid name/alias for: "
                             f"{object_a[1].name} {relationship_type} "
                             f"'{object_b[2]}'")
