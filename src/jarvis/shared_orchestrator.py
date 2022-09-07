#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module containing methods shared between objects/orchestrator"""
import re
import uuid

import datamodel
from .question_answer import (get_object_type, check_get_object, get_allocation_object,
                              check_not_family, get_objects_names, get_children)
from .functional_orchestrator import (create_function_obj, create_data_obj, create_fun_elem_obj,
                                      create_fun_inter_obj)
from .physical_orchestrator import (create_phy_elem_obj, create_phy_inter_obj)


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
            kwargs (dict) : 4 xml lists(see matched_composition() within command_parser.py)
            + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """

    parent_child_lists = [[] for _ in range(4)]
    available_objects = (datamodel.Function, datamodel.State,
                         datamodel.FunctionalElement,  datamodel.PhysicalElement)

    cleaned_parent_child_list_str = cut_string_list(parent_child_name_str_list)
    for elem in cleaned_parent_child_list_str:
        parent_object = check_get_object(elem[0], **kwargs)
        child_object = check_get_object(elem[1], **kwargs)
        if parent_object is None:
            if child_object is None:
                print(f"{elem[0]} and {elem[1]} are not Function/State/FunctionalElement"
                      f"/PhysicalElement or the object does not exist")
                continue

            print(f"{elem[0]} is not Function/State/FunctionalElement"
                  f"/PhysicalElement or the object does not exist")
            continue
        if child_object is None:
            print(f"{elem[1]} is not Function/State/FunctionalElement"
                  f"/PhysicalElement or the object does not exist")
            continue
        check_pair = None
        for idx, obj_type in enumerate(available_objects):
            if isinstance(parent_object, obj_type) and isinstance(child_object, obj_type):
                check_pair = idx
                break
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

    return 0


def check_add_allocated_item(item, xml_item_list, xml_view_list):
    """
    Checks if a view is already activated, if yes check if item isn't already
    allocated and returns corresponding [View, Object].
    Args:
        item (string): Object's name/alias from user's input
        xml_item_list ([Object]): List of xml's item (same type as item)
        xml_view_list ([View]) : View list from xml parsing

    Returns:
        [View, Object]
    """
    if not any(s.activated for s in xml_view_list):
        return None

    activated_view = None
    for view in xml_view_list:
        if view.activated:
            activated_view = view
            break
    if activated_view:
        for i in xml_item_list:
            if item == i.name:
                if i.id not in activated_view.allocated_item_list:
                    activated_view.add_allocated_item(i.id)
                    return [activated_view, i]
            # To avoid errors for i.alias when i is Data (no such attriute)
            try:
                if item == i.alias:
                    if i.id not in activated_view.allocated_item_list:
                        activated_view.add_allocated_item(i.id)
                        return [activated_view, i]
            except AttributeError:
                pass


def check_and_delete_object(delete_str_list, **kwargs):
    """
    Check if each string in delete_str_list are corresponding to an actual object, create new
    objects list for objects to delete.
    Send lists to delete_objects() to delete them within xml and then returns update from it.

        Parameters:
            delete_str_list ([str]) : List of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    to_be_deleted_obj_lists = [[] for _ in range(10)]
    # Check if the wanted to delete object exists and can be deleted
    for obj_str in delete_str_list:
        object_to_del = check_get_object(obj_str, **kwargs)
        if object_to_del is None:
            print(f"{obj_str} does not exist")
            continue
        check, list_idx = check_relationship_before_delete(object_to_del, **kwargs)
        if check:
            to_be_deleted_obj_lists[list_idx].append(object_to_del)
        else:
            print(f"{object_to_del.name} can not be deleted")

    update = delete_objects(to_be_deleted_obj_lists, kwargs['output_xml'])

    return update


def check_relationship_before_delete(object_to_del, **kwargs):
    """Switch to trigger differents methods depend object's type"""
    _, idx = get_specific_obj_type_and_idx(object_to_del)
    switch_check = {
        0: check_function,
        1: check_data,
        2: check_state,
        3: check_transition,
        4: check_fun_elem,
        5: check_chain,
        6: check_attribute,
        7: check_fun_inter,
        8: check_phy_elem,
        9: check_phy_inter,
    }
    check_obj = switch_check.get(idx, "Object can not be deleted")
    check = check_obj(object_to_del, **kwargs)
    return check, idx


def check_object_not_in_prod_cons(object_to_check, consumer_list, producer_list):
    """Check if object/data_name not in producer or consumer lists"""
    check = False
    if not any(object_to_check in o for o in consumer_list + producer_list):
        check = True
    return check


def check_object_no_parent_and_child(object_to_check):
    """Check if an object has not parent and not child"""
    check = False
    if not object_to_check.child_list and object_to_check.parent is None:
        check = True

    return check


def check_object_not_allocated(object_to_check, allocated_to_object_list):
    """Check if object in allocated_list of allocated objects"""
    check = False
    if not allocated_to_object_list:
        check = True
        return check

    converted_list = list(allocated_to_object_list)
    if isinstance(object_to_check, datamodel.Function):
        if isinstance(converted_list[0], (datamodel.State, datamodel.FunctionalElement)):
            if not any(object_to_check.id in obj.allocated_function_list for obj
                       in converted_list):
                check = True
        if isinstance(converted_list[0], datamodel.View):
            if not any(object_to_check.id in obj.allocated_item_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.Data):
        if isinstance(converted_list[0], datamodel.View):
            if not any(object_to_check.id in obj.allocated_item_list for obj
                       in converted_list):
                check = True
        if isinstance(converted_list[0], datamodel.FunctionalInterface):
            if not any(object_to_check.id in obj.allocated_data_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.State):
        if isinstance(converted_list[0], datamodel.FunctionalElement):
            if not any(object_to_check.id in obj.allocated_state_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.FunctionalElement):
        if isinstance(converted_list[0], datamodel.PhysicalElement):
            if not any(object_to_check.id in obj.allocated_fun_elem_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.FunctionalInterface):
        if isinstance(converted_list[0], datamodel.FunctionalElement):
            if not any(object_to_check.id in obj.exposed_interface_list for obj
                       in converted_list):
                check = True
        if isinstance(converted_list[0], datamodel.PhysicalInterface):
            if not any(object_to_check.id in obj.allocated_fun_inter_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.PhysicalInterface):
        if isinstance(converted_list[0], datamodel.PhysicalElement):
            if not any(object_to_check.id in obj.exposed_interface_list for obj
                       in converted_list):
                check = True
    return check


def check_object_no_attribute(object_to_check, attribute_list):
    """Check that object has not attribute set"""
    check = False
    described_item_list = [obj.described_item_list for obj in attribute_list]
    if not any(object_to_check.id in obj for obj in described_item_list):
        check = True
    return check


def check_function(object_to_del, **kwargs):
    """Checks for Function's object"""
    check = False
    check_list = [False]*6
    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        print(f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = check_object_not_allocated(object_to_del, kwargs['xml_state_list'])
    check_list[2] = check_object_not_allocated(object_to_del, kwargs['xml_fun_elem_list'])
    if not check_list[1] or not check_list[2]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    check_list[3] = check_object_not_in_prod_cons(object_to_del,
                                                  kwargs['xml_consumer_function_list'],
                                                  kwargs['xml_producer_function_list'])
    if not check_list[3]:
        print(f"{object_to_del.name} has production/consumption relationship(s)")

    check_list[4] = check_object_no_attribute(object_to_del, kwargs['xml_attribute_list'])
    if not check_list[4]:
        print(f"{object_to_del.name} has attribute(s) set")

    check_list[5] = check_object_not_allocated(object_to_del, kwargs['xml_view_list'])
    if not check_list[5]:
        print(f"{object_to_del.name} has chain relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_function_list'].remove(object_to_del)
    return check


def check_data(object_to_del, **kwargs):
    """Checks for Data's object"""
    check = False
    check_list = [False]*3
    check_list[0] = check_object_not_in_prod_cons(object_to_del.name,
                                                  kwargs['xml_consumer_function_list'],
                                                  kwargs['xml_producer_function_list'])
    if not check_list[0]:
        print(f"{object_to_del.name} has production/consumption relationship(s)")

    check_list[1] = check_object_not_allocated(object_to_del, kwargs['xml_view_list'])
    if not check_list[1]:
        print(f"{object_to_del.name} has chain relationship(s)")

    check_list[2] = check_object_not_allocated(object_to_del, kwargs['xml_fun_inter_list'])
    if not check_list[2]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_data_list'].remove(object_to_del)
    return check


def check_state(object_to_del, **kwargs):
    """Checks for State's object"""
    check = False
    check_list = [False] * 4

    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        print(f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = not object_to_del.allocated_function_list
    check_list[2] = check_object_not_allocated(object_to_del, kwargs['xml_fun_elem_list'])
    if not check_list[1] or not check_list[2]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    check_list[3] = not any(object_to_del.id in (trans.source, trans.destination)
                            for trans in kwargs['xml_transition_list'])
    if not check_list[3]:
        print(f"{object_to_del.name} has transition relationship(s)")
    if all(check_list):
        check = True
        kwargs['xml_state_list'].remove(object_to_del)
    return check


def check_transition(object_to_del, **kwargs):
    """Checks for State's object"""
    check = False
    check_list = [False] * 1

    check_list[0] = object_to_del.source is None and object_to_del.destination is None
    if not check_list[0]:
        print(f"{object_to_del.name} has source/destination relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_transition_list'].remove(object_to_del)
    return check


def check_fun_elem(object_to_del, **kwargs):
    """Checks for Functional Element's object"""
    check = False
    check_list = [False] * 4

    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        print(f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = (not object_to_del.allocated_function_list and
                     not object_to_del.allocated_state_list)
    check_list[2] = check_object_not_allocated(object_to_del, kwargs['xml_phy_elem_list'])
    if not check_list[1] or not check_list[2]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    check_list[3] = not object_to_del.exposed_interface_list
    if not check_list[3]:
        print(f"{object_to_del.name} has interface relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_fun_elem_list'].remove(object_to_del)

    return check


def check_chain(object_to_del, **kwargs):
    """Checks for View's object"""
    check = False
    check_list = [False] * 1

    check_list[0] = not object_to_del.allocated_item_list
    if not check_list[0]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_view_list'].remove(object_to_del)

    return check


def check_attribute(object_to_del, **kwargs):
    """Checks for Attribute's object"""
    check = False
    check_list = [False] * 1

    check_list[0] = not object_to_del.described_item_list
    if not check_list[0]:
        print(f"{object_to_del.name} has attribute relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_attribute_list'].remove(object_to_del)

    return check


def check_fun_inter(object_to_del, **kwargs):
    """Checks for Functional Interface's object"""
    check = False
    check_list = [False] * 3

    check_list[0] = not object_to_del.allocated_data_list
    check_list[1] = check_object_not_allocated(object_to_del, kwargs['xml_fun_elem_list'])
    check_list[2] = check_object_not_allocated(object_to_del, kwargs['xml_phy_inter_list'])
    if not check_list[0] or not check_list[1] or not check_list[2]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_fun_inter_list'].remove(object_to_del)

    return check


def check_phy_elem(object_to_del, **kwargs):
    """Checks for Physical Element's object"""
    check = False
    check_list = [False] * 3

    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        print(f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = not object_to_del.allocated_fun_elem_list
    if not check_list[1]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    check_list[2] = not object_to_del.exposed_interface_list
    if not check_list[2]:
        print(f"{object_to_del.name} has interface relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_phy_elem_list'].remove(object_to_del)

    return check


def check_phy_inter(object_to_del, **kwargs):
    """Checks for Physical Interface's object"""
    check = False
    check_list = [False] * 2

    check_list[0] = not object_to_del.allocated_fun_inter_list
    if not check_list[0]:
        print(f"{object_to_del.name} has allocation relationship(s)")

    check_list[1] = check_object_not_allocated(object_to_del, kwargs['xml_phy_elem_list'])
    if not check_list[1]:
        print(f"{object_to_del.name} has interface relationship(s)")

    if all(check_list):
        check = True
        kwargs['xml_phy_inter_list'].remove(object_to_del)

    return check


def delete_objects(object_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            object_lists : see order in get_specific_obj_type_and_idx()
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_lists):
        for i in range(10):
            if object_lists[i]:
                output_xml.delete_object(object_lists[i])
                for object_type in object_lists[i]:
                    print(f"{object_type.name} deleted")
        return 1
    return 0


def check_set_object_type(type_str_list, **kwargs):
    """
    Check if each string in type_str_list are corresponding to an actual object's name/alias, create
    [objects] ordered lists for:
    [[Function],[Data],[State],[Transition],[FunctionalElement],[Attribute],
    [FuncitonalInterface],[PhysicalElement],[PhysicalInterface],[View]]
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
        if object_to_set.type == type_name:
            continue
        check, list_idx = check_new_type(object_to_set, type_name, kwargs['xml_type_list'])
        if check:
            object_type_lists[list_idx].append(object_to_set)

    update = set_object_type(object_type_lists, kwargs['output_xml'])

    return update


def check_new_type(object_to_set, type_name, xml_type_list):
    """Check if type in specity object's type list and if changed"""
    check = False
    specific_obj_type_list, list_idx = get_specific_obj_type_and_idx(object_to_set)
    if list_idx in (0, 1, 2, 3, 4, 5, 7, 8, 9):
        if any(t == type_name.upper() for t in specific_obj_type_list):
            if type_name.capitalize() != str(object_to_set.type):
                check = True
                object_to_set.set_type(type_name.capitalize())
        elif any(t == type_name for t in get_objects_names(xml_type_list)):
            obj_type = check_get_object(type_name, **{'xml_type_list': xml_type_list})
            check = check_type_recursively(obj_type, specific_obj_type_list)
            if not check:
                print(f"{obj_type.name} is not base type: "
                      f"{specific_obj_type_list[0].capitalize()}")
            else:
                object_to_set.set_type(obj_type.name)
        else:
            print(
                f"The type {type_name} does not exist, available types are "
                f": {', '.join(specific_obj_type_list)}.")

    elif list_idx == 6:
        check = True
        object_to_set.set_type(type_name)

    return check, list_idx


def check_type_recursively(obj_type, specific_obj_type_list):
    """Checks type.base recursively if it within specific_obj_type_list"""
    check = False
    if isinstance(obj_type.base, str) and obj_type.base.upper() in specific_obj_type_list:
        check = True
        return check
    elif isinstance(obj_type.base, datamodel.Type):
        return check_type_recursively(obj_type.base, specific_obj_type_list)
    return check


def get_specific_obj_type_and_idx(object_to_set):
    """Get __str__ list from FunctionType, DataType, StateType, TransitionType,
    FunctionalElementType, ViewType and index for output_list (depends on the type)"""
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
    elif isinstance(object_to_set, datamodel.View):
        specific_obj_type_list = [str(i).upper() for i in datamodel.ViewType]
        list_idx = 5
    elif isinstance(object_to_set, datamodel.Attribute):
        list_idx = 6
    elif isinstance(object_to_set, datamodel.FunctionalInterface):
        specific_obj_type_list = [str(datamodel.BaseType.FUNCTIONAL_INTERFACE).upper()]
        list_idx = 7
    elif isinstance(object_to_set, datamodel.PhysicalElement):
        specific_obj_type_list = [str(datamodel.BaseType.PHYSICAL_ELEMENT).upper()]
        list_idx = 8
    elif isinstance(object_to_set, datamodel.PhysicalInterface):
        specific_obj_type_list = [str(datamodel.BaseType.PHYSICAL_INTERFACE).upper()]
        list_idx = 9

    return specific_obj_type_list, list_idx


def set_object_type(object_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            object_lists : see order in get_specific_obj_type_and_idx()
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
    object_lists = [[] for _ in range(9)]
    # Check if the wanted to object exists and the type can be set
    for object_to_set_alias, alias_str in alias_str_list:
        object_to_set = check_get_object(object_to_set_alias, **kwargs)
        if object_to_set is None:
            print(f"{object_to_set_alias} does not exist")
            continue

        idx = check_new_alias(object_to_set, alias_str)
        if isinstance(idx, int):
            object_lists[idx].append(object_to_set)

    update = set_object_alias(object_lists, kwargs['output_xml'])

    return update


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
        elif isinstance(object_to_set, datamodel.Type):
            list_idx = 8
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
        for i in range(9):
            if object_lists[i]:
                output_xml.write_object_alias(object_lists[i])
                for object_alias in object_lists[i]:
                    print(f"The alias for {object_alias.name} is {object_alias.alias}")

        return 1

    return 0


def check_add_allocation(allocation_str_list, **kwargs):
    """
    Check if each string in allocation_str_list are corresponding to an actual object's name/alias,
    create lists for:
    [[FunctionalElement, Function/State], [FunctionalInterface, Data],[State, Function],
    [PhysicalElement, FunctionalElement], [PhysicalInterface, FunctionalInterface]]
    Send lists to add_allocation() to write them within xml and then returns update from it.

        Parameters:
            allocation_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    new_allocation = {
        0: [],  # [FunctionalElement, Function/State]
        1: [],  # [State, Function]
        2: [],  # [FunctionalInterface, Data]
        3: [],  # [PhysicalElement, FunctionalElement]
        4: [],  # [PhysicalInterface, FunctionalInterface]
        # 5: [],  [View, Object] in other modules or [Fun_elem_Parent, Function/State] in
        # check_parent_allocation() it's just a key with no recursivety
    }
    for elem in allocation_str_list:
        alloc_obj = check_get_object(elem[0],
                                     **{'xml_fun_elem_list': kwargs['xml_fun_elem_list'],
                                        'xml_state_list': kwargs['xml_state_list'],
                                        'xml_fun_inter_list': kwargs['xml_fun_inter_list'],
                                        'xml_phy_elem_list': kwargs['xml_phy_elem_list'],
                                        'xml_phy_inter_list': kwargs['xml_phy_inter_list'],
                                        })
        obj_to_alloc = check_get_object(elem[1],
                                        **{'xml_function_list': kwargs['xml_function_list'],
                                            'xml_state_list': kwargs['xml_state_list'],
                                           'xml_data_list': kwargs['xml_data_list'],
                                           'xml_fun_elem_list': kwargs['xml_fun_elem_list'],
                                           'xml_fun_inter_list': kwargs['xml_fun_inter_list'],
                                           })
        check_obj = check_allocation_objects_types(alloc_obj, obj_to_alloc, elem)
        if not check_obj:
            continue
        check_rule, alloc = check_allocation_rules(alloc_obj, obj_to_alloc, **kwargs)
        if check_rule and alloc:
            new_allocation[alloc[0]].append(alloc[1])

    update = add_allocation(new_allocation, kwargs['output_xml'])

    return update


def check_allocation_objects_types(alloc_obj, obj_to_alloc, elem):
    """Check that alloc_obj within is FunctionalElement or FunctionalInterface or State or
    PhysicalElement or PhysicalInterface AND obj_to_alloc is Function/State or Data or
    FunctionalElement or FunctionalInterface"""
    check = True
    if alloc_obj is None and obj_to_alloc is None:
        print_wrong_obj_allocation(elem)
        check = False
    elif alloc_obj is None or obj_to_alloc is None:
        if alloc_obj is None:
            print_wrong_obj_allocation(elem[0])
            check = False
        elif obj_to_alloc is None:
            print_wrong_obj_allocation(elem[1])
            check = False

    return check


def print_wrong_obj_allocation(obj_str):
    """Print relative message to wrong pair allocations"""
    if isinstance(obj_str, tuple):
        name_str = f"Objects {obj_str[0]} and {obj_str[1]}"
    else:
        name_str = f"Object {obj_str}"
    print(name_str + " not found or can not be allocated, "
                     "available allocations are: \n"
                     "(Functional Element allocates State/Function) OR \n"
                     "(State allocates Function) OR \n"
                     "(Functional Interface allocates Data) OR \n"
                     "(Physical Element allocates Functional Element) OR \n"
                     "(Physical Interface allocates Functional Interface)\n")


def check_allocation_rules(alloc_obj, obj_to_alloc, **kwargs):
    """Check "good" combinations, trigger specific check and then return check and new tuple
    allocation"""
    check = False
    new_alloc = None
    if isinstance(alloc_obj, datamodel.FunctionalElement):
        if isinstance(obj_to_alloc, (datamodel.Function, datamodel.State)):
            check = True
            pair = check_fun_elem_allocation(alloc_obj, obj_to_alloc, kwargs['xml_fun_elem_list'])
            if pair:
                new_alloc = [0, pair]
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.State):
        if isinstance(obj_to_alloc, datamodel.Function):
            check = True
            pair = check_state_allocation(alloc_obj, obj_to_alloc, kwargs['xml_state_list'])
            if pair:
                new_alloc = [1, pair]
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.FunctionalInterface):
        if isinstance(obj_to_alloc, datamodel.Data):
            check = True
            pair = check_fun_inter_allocation(alloc_obj, obj_to_alloc, **kwargs)
            if pair:
                new_alloc = [2, pair]
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.PhysicalElement):
        if isinstance(obj_to_alloc, datamodel.FunctionalElement):
            check = True
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.PhysicalInterface):
        if isinstance(obj_to_alloc, datamodel.FunctionalInterface):
            check = True
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)

    return check, new_alloc


def check_fun_elem_allocation(fun_elem, obj_to_alloc, fun_elem_list):
    """Check allocation rules for fun_elem then returns objects if check"""
    count = None
    out = None
    check_allocation = get_allocation_object(obj_to_alloc, fun_elem_list)
    if check_allocation is not None:
        count = len(check_allocation)
        for item in check_allocation:
            # Checks if they are in the same family
            if not check_not_family(item, fun_elem) and item != fun_elem:
                count -= 1

    if count in (None, 0):
        if isinstance(obj_to_alloc, datamodel.State):
            fun_elem.add_allocated_state(obj_to_alloc.id)
        else:
            fun_elem.add_allocated_function(obj_to_alloc.id)
        out = [fun_elem, obj_to_alloc]

    return out


def check_state_allocation(state, function, state_list):
    """Check allocation rules for state then returns objects if check"""
    out = None
    check_allocation = get_allocation_object(function, state_list)
    if check_allocation is None:
        state.add_allocated_function(function.id)
        out = [state, function]
    else:
        if state not in check_allocation:
            state.add_allocated_function(function.id)
            out = [state, function]

    return out


def check_fun_inter_allocation(fun_inter, data, **kwargs):
    """Check allocation rules for fun_inter then returns objects if check"""
    out = None
    check_allocation_fun_inter = get_allocation_object(data, kwargs['xml_fun_inter_list'])
    if check_allocation_fun_inter is None:
        check_fe = check_fun_elem_data_consumption(
            data, fun_inter,
            kwargs['xml_fun_elem_list'],
            kwargs['xml_function_list'],
            kwargs['xml_consumer_function_list'],
            kwargs['xml_producer_function_list'])
        if all(i for i in check_fe):
            out = [fun_inter, data]
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
    return out


def check_fun_elem_data_consumption(data, fun_inter, fun_elem_list, function_list,
                                    xml_consumer_function_list, xml_producer_function_list):
    """Check if for a fun_inter, the fun_elem exposing it has allocated functions producing and
    consumming that data"""
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


def add_allocation(allocation_dict, output_xml):
    """
    Check if allocation_lists is not empty, write in xml for each list and return 0/1
    if some update has been made.

        Parameters:
            allocation_dict : Containing all allocation to write within xml
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(allocation_dict.values()):
        for _, k in enumerate(allocation_dict):
            if allocation_dict[k]:
                output_xml.write_objects_allocation(allocation_dict[k])
                # Warn the user once added within xml
                for elem in allocation_dict[k]:
                    print(f"{elem[1].__class__.__name__} {elem[1].name} is allocated to "
                          f"{elem[0].__class__.__name__} {elem[0].name}")
                    # Check the dict length, if this method is called from viewpoint_orchestrator
                    # or functional_orchestrator for View => Only key[0] and no recursion wanted
                    if k in (0, 1):
                        recursive_allocation(elem, output_xml)
        return 1
    return 0


def check_parent_allocation(elem, output_xml):
    """Check if parent's Function/Sate are allocated to parent's Fucntional Element:
    if not print message to user asking if he wants to, if yes write it in xml then continue
    with parents"""
    if elem[0].parent is not None and elem[1].parent is not None:
        fun_elem_parent = elem[0].parent
        object_parent = elem[1].parent
        check = False
        if isinstance(elem[1], datamodel.State):
            if object_parent.id in fun_elem_parent.allocated_state_list:
                check = True
        elif isinstance(elem[1], datamodel.Function):
            if object_parent.id in fun_elem_parent.allocated_function_list:
                check = True
        if not check:
            answer = input(f"Do you also want to allocate parents(i.e. {object_parent.name} "
                           f"to {fun_elem_parent.name}) ?(Y/N)")
            if answer.lower() == "y":
                if isinstance(elem[1], datamodel.State):
                    fun_elem_parent.add_allocated_state(object_parent.id)
                else:
                    fun_elem_parent.add_allocated_function(object_parent.id)

                add_allocation({5: [[fun_elem_parent, object_parent]]}, output_xml)
                check_parent_allocation([fun_elem_parent, object_parent], output_xml)
            else:
                print(f"Error: {object_parent.name} is not allocated despite at least one "
                      f"of its child is")


def recursive_allocation(elem, output_xml):
    """Recursive allocation for childs of State/Function"""
    check_parent_allocation(elem, output_xml)
    object_type = get_object_type(elem[1])
    if elem[1].child_list:
        for i in elem[1].child_list:
            parent_child = [elem[1], i]
            allocated_child_list = get_allocated_child(parent_child, [elem[0]])
            if allocated_child_list:
                for item in allocated_child_list:
                    if isinstance(elem[1], datamodel.State):
                        item[0].add_allocated_state(item[1].id)
                    else:
                        item[0].add_allocated_function(item[1].id)
                # We want recursivety so it trigger for (0, 1) keys in the dict
                add_allocation({0: allocated_child_list}, output_xml)
    else:
        # TBT/TBC
        if object_type == "state" and elem[1].id not in elem[0].allocated_state_list:
            elem[0].add_allocated_state(elem[1].id)
            print(f"State {elem[1].name} is allocated to functional "
                  f"element {elem[0].name}")
        elif object_type == "function" and elem[1].id not in elem[0].allocated_function_list:
            elem[0].add_allocated_function(elem[1].id)
            print(f"Function {elem[1].name} is allocated to functional "
                  f"element {elem[0].name}")


def get_allocated_child(elem, xml_fun_elem_list):
    """
    Check if the parent state/function is already allocated to a fun elem and create list to add
    its child also (if not already allocated)

        Parameters:
            elem ([State/Function]) : parent object, child object
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing

        Returns:
            output_list ([FunctionalElement, State/Function]) : Allocation Relationships that need
            to be added
    """
    output_list = []
    for fun_elem in xml_fun_elem_list:
        if isinstance(elem[0], datamodel.State):
            # To avoid "RuntimeError: Set changed size during iteration" copy()
            allocated_list = fun_elem.allocated_state_list.copy()
        else:
            allocated_list = fun_elem.allocated_function_list.copy()
        if allocated_list:
            for allocated_object in allocated_list:
                if allocated_object == elem[0].id:
                    if elem[1].id not in allocated_list:
                        if isinstance(elem[0], datamodel.State):
                            fun_elem.add_allocated_state(elem[1].id)
                        else:
                            fun_elem.add_allocated_function(elem[1].id)
                        output_list.append([fun_elem, elem[1]])

    return output_list


def check_add_inheritance(inherit_str_list, **kwargs):
    """
    Check if each string in allocation_str_list are corresponding to an actual object's name/alias,
    set_derive, create lists of objets.
    Send lists to add_derived() to write them within xml and then returns update from it.

        Parameters:
            inherit_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    new_list = []
    for elem in inherit_str_list:
        # elem_0: inheriting object
        elem_0 = check_get_object(elem[0],
                                  **{'xml_function_list': kwargs['xml_function_list'],
                                     'xml_fun_elem_list': kwargs['xml_fun_elem_list'],
                                     'xml_fun_inter_list': kwargs['xml_fun_inter_list'],
                                     'xml_phy_elem_list': kwargs['xml_phy_elem_list'],
                                     'xml_phy_inter_list': kwargs['xml_phy_inter_list'],
                                     })
        # elem_1: object to inherit from
        elem_1 = check_get_object(elem[1],
                                  **{'xml_function_list': kwargs['xml_function_list'],
                                     'xml_fun_elem_list': kwargs['xml_fun_elem_list'],
                                     'xml_fun_inter_list': kwargs['xml_fun_inter_list'],
                                     'xml_phy_elem_list': kwargs['xml_phy_elem_list'],
                                     'xml_phy_inter_list': kwargs['xml_phy_inter_list'],
                                     })
        if not elem_0 or not elem_1:
            if not elem_0 and not elem_1:
                print_wrong_object_inheritance(elem[0], elem[1])
            elif not elem_0:
                print_wrong_object_inheritance(elem[0])
            else:
                print_wrong_object_inheritance(elem[1])
            continue
        if elem_0 == elem_1:
            print(f"Same object {elem_0.name}")
            continue
        if elem_0.derived == elem_1:
            continue

        check_obj = check_inheritance(elem_0, elem_1)
        if not check_obj:
            continue
        new_list.append(elem_0)

    if not new_list:
        return 0

    add_derived(new_list, kwargs['output_xml'])
    return 1


def print_wrong_object_inheritance(*obj):
    """Prints wrong object(s) message for inheritance from input string"""
    if len(obj) == 2:
        user_message = f"{obj[0]} and {obj[1]}"
    else:
        user_message = f"{obj[0]}"
    print(f"{user_message} not found, available objects for inheritance are:\n"
          "- Function\n"
          "- Functional element\n"
          "- Functional interface\n"
          "- Physical element\n"
          "- Physical element\n")


def check_inheritance(elem_0, elem_1):
    """Returns check if pair are compatible and object list have been updated"""
    inheritance_type_list = [datamodel.Function, datamodel.FunctionalElement,
                             datamodel.FunctionalInterface, datamodel.PhysicalElement,
                             datamodel.PhysicalInterface]

    type_found = None
    for idx, inheritance_type in enumerate(inheritance_type_list):
        if isinstance(elem_0, inheritance_type) and isinstance(elem_1, inheritance_type):
            type_found = idx
            break
    if type_found is None:
        print(f"{elem_0.__class__.__name__} and {elem_1.__class__.__name__} "
              f"are not of the same type")
        return False
    elem_0.set_derived(elem_1)
    return True


def add_derived(object_list, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update if some
    updates has been made.
        Parameters:
            object_list ([Object]) : object with new derived
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_list):
        output_xml.write_derived(object_list)
        for obj in object_list:
            print(f"{obj.name} inherited from {obj.derived.name}")
        return 1
    return 0


def check_add_specific_obj_by_type(obj_type_str_list, **kwargs):
    """
    Check if each string in obj_type_str_list are corresponding to an actual object's name/alias,
    set_derive, create object_lists with list per obj. Send lists to add_obj_to_xml()
    write them within xml and then returns update from it.

        Parameters:
            obj_type_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    object_lists = [[] for _ in range(6)]
    for elem in obj_type_str_list:
        spec_obj_type = None
        if elem[1].capitalize() in [str(i) for i in datamodel.BaseType]:
            base_type = next((i for i in [str(i) for i in datamodel.BaseType]
                              if i == elem[1].capitalize()))
        else:
            spec_obj_type = check_get_object(elem[1],
                                             **{'xml_type_list': kwargs['xml_type_list']})
            base_type = get_base_type_recursively(spec_obj_type)
        if not base_type:
            print(f"No valid base type found for {elem[1]}")
            continue
        base_type = datamodel.BaseType.get_enum(str(base_type)).value
        switch_obj_list = {
            0: create_data_obj,
            1: create_function_obj,
            2: create_fun_elem_obj,
            3: create_fun_inter_obj,
            4: create_phy_elem_obj,
            5: create_phy_inter_obj,
        }
        call = switch_obj_list.get(base_type)
        new_obj = call(elem[0], spec_obj_type, **kwargs)
        if not isinstance(new_obj, int):
            object_lists[base_type].append(new_obj)
        # print(sepc_obj_type.name, sepc_obj_type.base)
    if any(object_lists):
        return add_obj_to_xml(object_lists, kwargs['output_xml'])
    return 0


def get_base_type_recursively(obj_type):
    """Checks type: if it's a BaseType or its base else recursively return """
    if isinstance(obj_type, datamodel.BaseType):
        return obj_type
    elif obj_type.name in [str(i) for i in datamodel.BaseType]:
        return obj_type.name
    elif obj_type.base in [str(i) for i in datamodel.BaseType]:
        return obj_type.base
    return get_base_type_recursively(obj_type.base)


def get_unique_id():
    """Generate and set unique identifier of length 10 integers"""
    identifier = uuid.uuid4()
    return str(identifier.int)[:10]


def add_obj_to_xml(object_lists, output_xml):
    """Send lists object to respective methods of GenerateXML, returns 1 if at least one obj has
    been written"""
    switch_write_obj = {
        0: output_xml.write_data,
        1: output_xml.write_function,
        2: output_xml.write_functional_element,
        3: output_xml.write_functional_interface,
        4: output_xml.write_physical_element,
        5: output_xml.write_physical_interface,
    }
    check = 0
    for idx, sub in enumerate(object_lists):
        if sub:
            switch_write_obj.get(idx)(sub)
            check = 1
    return check


# Inheritance start here - Should be moved/refactored after validation
def childs_inheritance(*xml_obj_set, level=None):
    """Check if object from xml_obj_set is derived, if yes:
    - call derived_childs()
    - returns derived_parent_dict of derived objects id, derived_child_set of derived objects and
    derived_child_id_list
    Parameter:
    - obj: set() of objects
    - level: diagram level"""
    derived_child_set = set()
    derived_parent_dict = {}
    derived_child_id_list = set()

    for xml_set in xml_obj_set:
        for elem in xml_set:
            if elem.derived:
                partial_child_set, partial_par_dict, partial_child_id_set = derived_childs(elem,
                                                                                           level)
                derived_child_set = derived_child_set.union(partial_child_set)
                derived_parent_dict.update(partial_par_dict)
                derived_child_id_list = derived_child_id_list.union(partial_child_id_set)

    return derived_child_set, derived_parent_dict, derived_child_id_list


def derived_childs(obj, level):
    """Add derived object childs to object and set derived parent to object"""
    derived_parent_dict = {}

    [obj.add_child(c) for c in obj.derived.child_list
     if c.parent == obj.derived]
    [c.set_parent(obj) for c in obj.derived.child_list
     if c.parent == obj.derived]
    for child in obj.derived.child_list:
        derived_parent_dict[str(child.id)] = str(obj.id)
    derived_child_set = get_children(obj.derived, level=level)[0]
    derived_child_id_list = {c.id for c in obj.derived.child_list}
    obj.derived.child_list.clear()
    derived_child_set.remove(obj.derived)

    return derived_child_set, derived_parent_dict, derived_child_id_list


def reset_childs_inheritance(*xml_obj_set, derived_child_id=None):
    """Check if there is first level derived child id list, if yes reset original child/parent
    relationships"""
    if derived_child_id:
        for xml_set in xml_obj_set:
            for elem in xml_set:
                if elem.derived:
                    child_pop = [c for c in elem.child_list
                                 if c.id in [f for f in derived_child_id]]
                    [elem.derived.add_child(c) for c in child_pop]
                    [c.set_parent(elem.derived) for c in child_pop]


def attribute_inheritance(xml_attribute_set, *xml_object_set):
    """Attribute inheritance"""
    modified_attrib_set = set()
    derived_elem = set()

    for xml_set in xml_object_set:
        [derived_elem.add(e) for e in xml_set if e.derived]

    for attribute in xml_attribute_set:
        for obj_id, value in attribute.described_item_list.copy():
            for der_obj in derived_elem:
                if obj_id == der_obj.derived.id:
                    attribute.add_described_item((der_obj.id, value))
                    modified_attrib_set.add((attribute.id, der_obj.id, value))

    return modified_attrib_set


def reset_attribute_inheritance(xml_attribute_set, to_be_reset_id_set):
    """Reset attributes"""
    for attribute in xml_attribute_set:
        [attribute.described_item_list.remove((e[1], e[2])) for e in to_be_reset_id_set
         if e[0] == attribute.id]


def view_inheritance(xml_view_set, *xml_obj_set):
    """View inheritance"""
    temp_view_set = set()
    derived_elem_set = set()

    for xml_set in xml_obj_set:
        [derived_elem_set.add(e) for e in xml_set if e.derived]

    for view in xml_view_set:
        for item_id in view.allocated_item_list.copy():
            for obj in derived_elem_set:
                if item_id == obj.derived.id:
                    temp_view_set.add((view.id, obj.id))
                    view.add_allocated_item(obj.id)

    return temp_view_set


def reset_view_inheritance(xml_view_set, to_be_removed_id):
    """Reset views"""
    for view in xml_view_set:
        for ids in to_be_removed_id:
            if view.id == ids[0]:
                view.allocated_item_list.remove(ids[1])


def allocation_inheritance(xml_obj_set, xml_allocated_obj_set):
    """Allocation Inheritance"""
    alloc_to_reset = []
    for elem in xml_obj_set:
        if elem.derived:
            if isinstance(elem, datamodel.FunctionalElement):
                pair = [elem, {i for i in elem.derived.allocated_function_list
                                  if i not in elem.allocated_function_list}]
                elem.allocated_function_list = elem.allocated_function_list.union(
                    elem.derived.allocated_function_list)
                alloc_to_reset.append(pair)

    return alloc_to_reset


def reset_alloc_inheritance(pairs_to_reset):
    """Reset Allocation Inheritance"""
    for pair in pairs_to_reset:
        if isinstance(pair[0], datamodel.FunctionalElement):
            [pair[0].allocated_function_list.remove(fun_id) for fun_id in pair[1]]