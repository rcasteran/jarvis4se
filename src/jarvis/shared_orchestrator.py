#!/usr/bin/env python
import re

import datamodel
from .question_answer import get_object_name, get_object_type, check_get_object, \
    get_allocation_object, check_parentality


def cut_string_list(string_tuple_list):
    """From set of input command strings e.g for composition with input list as
    {(Function_name, Function_name_A), (Function_name, [Function_name_B, Function_name_C])} : this
    methods returns {(Function_name, Function_name_A), (Function_name, Function_name_B),
    (Function_name, Function_name_C)}

        Parameters:
            string_tuple_list ([(str, str), ...]) : Lists of string tuple from jarvis cell
        Returns:
            output_list ([0/1]) : output list
    """

    output_list = []
    for parent, child in string_tuple_list:
        if "," in child:
            child_str = child.replace(" ", "")
            child_list_str = re.split(r',(?![^[]*\])', child_str)
            for elem in child_list_str:
                output_list.append((parent, elem))
        else:
            output_list.append((parent, child))

    return output_list


def check_add_child(parent_child_name_str_list, **kwargs):
    """
    Check if each string in parent_child_name_str_list are corresponding to an actual object,
    create new [parent, child] objects lists for object's type : State/Function/FunctionalElement.
    Send lists to add_child() to write them within xml and then returns update_list from it.

        Parameters:
            parent_child_name_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : 4 xml lists( see matched_composition() within command_parser.py
            + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    parent_child_lists = [[] for _ in range(4)]
    available_objects = (datamodel.Function, datamodel.State,
                         datamodel.FunctionalElement,  datamodel.PhysicalElement)

    cleaned_parent_child_list_str = cut_string_list(parent_child_name_str_list)
    # print(parent_child_name_str_list, cleaned_parent_child_list_str)
    for elem in cleaned_parent_child_list_str:
        parent_object = check_get_object(elem[0], **kwargs)
        child_object = check_get_object(elem[1], **kwargs)
        if parent_object is None:
            if child_object is None:
                print(f"{elem[0]} and {elem[1]} are not Function/State/FunctionalElement"
                      f"/PhysicalElement or the object does not exist")
                continue
            else:
                print(f"{elem[0]} is not Function/State/FunctionalElement"
                      f"/PhysicalElement or the object does not exist")
                continue
        elif child_object is None:
            print(f"{elem[1]} is not Function/State/FunctionalElement"
                  f"/PhysicalElement or the object does not exist")
            continue
        check_pair = None
        for idx, obj_type in enumerate(available_objects):
            if isinstance(parent_object, obj_type) and isinstance(child_object, obj_type):
                check_pair = idx
                break
            else:
                check_pair = None
        if isinstance(check_pair, int):
            if child_object.parent is None:
                parent_object.add_child(child_object)
                child_object.set_parent(parent_object)
                parent_child_lists[check_pair].append([parent_object, child_object])
        else:
            print(f"Please choose a valid pair of element(Function/State/FunctionalElement"
                  f"/PhysicalElement) for {parent_object.name} and {child_object.name}")

    update = add_child(parent_child_lists, kwargs['xml_fun_elem_list'], kwargs['output_xml'])

    return update


def add_child(parent_child_lists, xml_fun_elem_list, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            parent_child_lists ([Parent, Child]) : [[Function],[State],[FunctionalElement],
            [PhysicalElement]]
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if any(parent_child_lists):
        for i in range(4):
            if parent_child_lists[i]:
                output_xml.write_object_child(parent_child_lists[i])
                for k in parent_child_lists[i]:
                    print(f"{k[0].name} is composed of {k[1].name}")
                    if i in (0, 1):
                        for fun_elem in xml_fun_elem_list:
                            if k[0].id in fun_elem.allocated_function_list:
                                recursive_allocation([fun_elem, k[1]], output_xml)
        return 1
    else:
        return 0


def check_add_allocated_item(item, xml_item_list, xml_chain_list):
    """
    Checks if a chain is already activated, if yes check if item isn't already
    allocated and returns corresponding [Chain, Object].
    Args:
        item (string): Object's name/alias from user's input
        xml_item_list ([Object]): List of xml's item (same type as item)
        xml_chain_list ([Chain]) : Chain list from xml parsing

    Returns:
        [Chain, Object]
    """
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
                # To avoid errors for i.alias when i is Data (no such attriute)
                try:
                    if item == i.alias:
                        if i.id not in activated_chain.allocated_item_list:
                            activated_chain.add_allocated_item(i.id)
                            return [activated_chain, i]
                except AttributeError:
                    pass


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


def check_set_object_type(type_str_list, **kwargs):
    """
    Check if each string in type_str_list are corresponding to an actual object's name/alias, create
    [objects] ordered lists for:
    [[Function],[Data],[State],[Transition],[FunctionalElement],[Attribute],
    [FuncitonalInterface],[PhysicalElement],[PhysicalInterface],[Chain]]
    Send lists to set_object_type() to write them within xml and then returns update from it.

        Parameters:
            type_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    object_type_lists = [[] for _ in range(10)]
    # Check if the wanted object exists and the type can be set
    for object_str, type_name in type_str_list:
        object_to_set = check_get_object(object_str, **kwargs)
        if object_to_set is None:
            print(f"{object_str} does not exist")
            continue

        check, list_idx = check_new_type(object_to_set, type_name)
        if check:
            object_type_lists[list_idx].append(object_to_set)

    update = set_object_type(object_type_lists, kwargs['output_xml'])

    return update


def check_new_type(object_to_set, type_name):
    """Check if type in specity object's type list and if changed"""
    check = False
    specific_obj_type_list, list_idx = get_specific_obj_type(object_to_set)
    if list_idx in (0, 1, 2, 3, 4, 5):
        if type_name.upper() in specific_obj_type_list:
            if type_name.capitalize() != str(object_to_set.type):
                check = True
                object_to_set.set_type(type_name.capitalize())
        else:
            print(
                f"The type {type_name} does not exist, available types are "
                f": {', '.join(specific_obj_type_list)}.")

    elif list_idx in (6, 7, 8, 9):
        if type_name != str(object_to_set.type):
            check = True
            object_to_set.set_type(type_name)

    return check, list_idx


def get_specific_obj_type(object_to_set):
    """Get __str__ list from FunctionType, DataType, StateType, TransitionType,
    FunctionalElementType, ChainType and index for output_list (depends on the type)"""
    specific_obj_type_list = []
    list_idx = None
    if isinstance(object_to_set, datamodel.Function):
        specific_obj_type_list = [str(i).upper() for i in datamodel.FunctionType]
        list_idx = 0
    elif isinstance(object_to_set, datamodel.Data):
        specific_obj_type_list = [str(i).upper() for i in datamodel.DataType]
        list_idx = 1
    elif isinstance(object_to_set, datamodel.State):
        specific_obj_type_list = [str(i).upper() for i in datamodel.StateType]
        list_idx = 2
    elif isinstance(object_to_set, datamodel.Transition):  # TBC
        specific_obj_type_list = [str(i).upper() for i in datamodel.TransitionType]
        list_idx = 3
    elif isinstance(object_to_set, datamodel.FunctionalElement):
        specific_obj_type_list = [str(i).upper() for i in datamodel.FunctionalElementType]
        list_idx = 4
    elif isinstance(object_to_set, datamodel.Chain):
        specific_obj_type_list = [str(i).upper() for i in datamodel.ChainType]
        list_idx = 5
    elif isinstance(object_to_set, datamodel.Attribute):
        list_idx = 6
    elif isinstance(object_to_set, datamodel.FunctionalInterface):
        list_idx = 7
    elif isinstance(object_to_set, datamodel.PhysicalElement):
        list_idx = 8
    elif isinstance(object_to_set, datamodel.PhysicalInterface):
        list_idx = 9

    return specific_obj_type_list, list_idx


def set_object_type(object_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            object_lists : see order in comments below
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_lists):
        for i in range(10):
            if object_lists[i]:
                output_xml.write_object_type(object_lists[i])
                for object_type in object_lists[i]:
                    print(f"The type of {object_type.name} is {object_type.type}")
        return 1
    else:
        return 0


def check_set_object_alias(alias_str_list, **kwargs):
    """
    Check if each string in alias_str_list are corresponding to an actual object's name/alias,
    create [objects] ordered lists for:
    [[Function],[State],[Transition],[FunctionalElement],[Attribute],
    [FuncitonalInterface],[PhysicalElement],[PhysicalInterface]]
    Send lists to set_object_type() to write them within xml and then returns update from it.

        Parameters:
            alias_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    object_lists = [[] for _ in range(8)]
    # Check if the wanted to object exists and the type can be set
    for object_to_set_alias, alias_str in alias_str_list:
        object_to_set = check_get_object(object_to_set_alias, **kwargs)
        if object_to_set is None:
            print(f"{object_to_set_alias} does not exist")
            continue

        idx = check_new_alias(object_to_set, alias_str)
        if isinstance(idx, int):
            object_lists[idx].append(object_to_set)

    update_list = set_object_alias(object_lists, kwargs['output_xml'])

    return update_list


def check_new_alias(object_to_set, alias_str):
    """Check that alias is new and object has en alias attribute, then returns corresponding
    object's type index"""
    list_idx = None
    if object_to_set.alias != alias_str:
        object_to_set.set_alias(alias_str)
        if isinstance(object_to_set, datamodel.Function):
            list_idx = 0
        elif isinstance(object_to_set, datamodel.State):
            list_idx = 1
        elif isinstance(object_to_set, datamodel.Transition):
            list_idx = 2
        elif isinstance(object_to_set, datamodel.FunctionalElement):
            list_idx = 3
        elif isinstance(object_to_set, datamodel.Attribute):
            list_idx = 4
        elif isinstance(object_to_set, datamodel.FunctionalInterface):
            list_idx = 5
        elif isinstance(object_to_set, datamodel.PhysicalElement):
            list_idx = 6
        elif isinstance(object_to_set, datamodel.PhysicalInterface):
            list_idx = 7
        else:
            print(f"{object_to_set.name} does not have alias attribute")

    return list_idx


def set_object_alias(object_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update if some
    updates has been made.
        Parameters:
            object_lists ([Object]) : object with new alias
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_lists):
        for i in range(8):
            if object_lists[i]:
                output_xml.write_object_alias(object_lists[i])
                for object_alias in object_lists[i]:
                    print(f"The alias for {object_alias.name} is {object_alias.alias}")

        return 1
    else:
        return 0


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
