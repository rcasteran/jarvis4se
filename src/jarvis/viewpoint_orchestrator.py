#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module with methods relative to Viewpoint section"""
# Libraries
import uuid
import re

import datamodel
from . import shared_orchestrator
from .question_answer import get_objects_names, check_get_object


def add_view(view_name_str, xml_view_list, output_xml):
    """
        Check if each string in view_name_str is not already corresponding to an actual
        object's name, create new View() object, instantiate it, write it within XML and
        then returns update_list.

            Parameters:
                view_name_str ([str]) : Lists of string from jarvis cell
                xml_view_list ([Function]) : view list from xml parsing
                output_xml (GenerateXML object) : XML's file object

            Returns:
                1 if update, else 0
        """
    view_list = []
    # Create a list with all view names already in the xml
    xml_view_name_list = get_objects_names(xml_view_list)
    # Loop on the list and create set for functions
    if view_name_str not in xml_view_name_list:
        # Instantiate view class
        view = datamodel.View()
        # Set view's name
        view.set_name(str(view_name_str))
        # Set view's type
        view.set_type(datamodel.ViewType.UNKNOWN)
        # Generate and set unique identifier of length 10 integers
        identifier = uuid.uuid4()
        view.set_id(str(identifier.int)[:10])
        # Add view to new set() and existing et() from xml
        xml_view_list.add(view)
        view_list.append(view)
        activate_view(view.name, xml_view_list)
    elif view_name_str in xml_view_name_list:
        # print(view_name + " already exists (not added)")
        activate_view(view_name_str, xml_view_list)

    if not view_list:
        return 0

    output_xml.write_view(view_list)
    for view in view_list:
        print(view.name + " is a View")
    return 1


def activate_view(view_name, xml_view_list):
    """Activates View from view's name str"""
    for view in xml_view_list:
        if view_name == view.name:
            view.set_activation(True)
        else:
            view.set_activation(False)


def check_get_consider(consider_str_list, xml_function_list, xml_fun_elem_list, xml_data_list,
                       xml_view_list, output_xml):
    """
    Check and get all "consider xxx" strings. If corresponds to an actual object not yet added to
    the current view => add it to View object and as allocatedItem within xml
    Args:
        consider_str_list ([strings]): list of strings (separated by comma is possible)
        xml_function_list ([Function]) : Function list from xml parsing
        xml_fun_elem_list ([Fun Elem]) : Functional Element list from xml parsing
        xml_data_list ([Data]) : Data list from xml parsing
        xml_view_list ([View]) : View list from xml parsing
        output_xml (GenerateXML object) : XML's file object

    Returns:
        update ([0/1]) : 1 if update, else 0
    """
    allocated_item_list = []
    # Create lists with all object names/aliases already in the xml
    xml_fun_elem_name_list = get_objects_names(xml_fun_elem_list)
    xml_function_name_list = get_objects_names(xml_function_list)
    xml_data_name_list = get_objects_names(xml_data_list)

    consider_str_list = split_chain_from_string(consider_str_list)

    for consider_str in consider_str_list:
        if consider_str not in [*xml_fun_elem_name_list, *xml_function_name_list,
                                *xml_data_name_list]:
            print(f"Object {consider_str} does not exist, available object types are : "
                  f"Functional Element, Function and Data")
        else:
            result_function = any(item == consider_str for item in xml_function_name_list)
            result_fun_elem = any(item == consider_str for item in xml_fun_elem_name_list)
            result_data = any(item == consider_str for item in xml_data_name_list)

            if result_function:
                allocated_fun = shared_orchestrator.check_add_allocated_item(
                    consider_str, xml_function_list, xml_view_list)
                if allocated_fun:
                    allocated_item_list.append(allocated_fun)
            elif result_fun_elem:
                allocated_fun_elem = shared_orchestrator.check_add_allocated_item(
                    consider_str, xml_fun_elem_list, xml_view_list)
                if allocated_fun_elem:
                    allocated_item_list.append(allocated_fun_elem)
            elif result_data:
                allocated_data = shared_orchestrator.check_add_allocated_item(
                    consider_str, xml_data_list, xml_view_list)
                if allocated_data:
                    allocated_item_list.append(allocated_data)

    update = shared_orchestrator.add_allocation({5: allocated_item_list}, output_xml)

    return update


def split_chain_from_string(consider_str_list):
    """Creates flatten list : from ["A", "B, C, D"] to ["A", "B", "C", "D"]"""
    output_list = []
    for consider_str in consider_str_list:
        if "," in consider_str:
            clean_diagram_object_str = consider_str.replace(" ", "")
            output_list += re.split(r',(?![^[]*\])', clean_diagram_object_str)
        else:
            output_list.append(consider_str)

    return output_list


def add_attribute(attribute_str_list, xml_attribute_list, output_xml):
    """
    Check if each string in xml_attribute_list is not already corresponding to an actual object's
    name/alias, create new Attribute() object, instantiate it, write it within XML and then returns
    update_list.

        Parameters:
            attribute_str_list ([str]) : Lists of string from jarvis cell
            xml_attribute_list ([Attribute]) : Attribute list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    new_attribute_list = []
    # Create attribute names list already in xml
    xml_attribute_name_list = get_objects_names(xml_attribute_list)
    # Filter attribute_list, keeping only the the ones not already in the xml
    for attribute_name in attribute_str_list:
        if attribute_name not in xml_attribute_name_list:
            new_attribute = datamodel.Attribute()
            new_attribute.set_name(str(attribute_name))
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            new_attribute.set_id(str(identifier.int)[:10])
            # Not needed, by default unknown
            # new_data.set_type(datamodel.DataType.UNKNOWN)
            # alias is 'none' by default
            new_attribute_list.append(new_attribute)

    if not new_attribute_list:
        return 0

    output_xml.write_attribute(new_attribute_list)
    for attribute in new_attribute_list:
        xml_attribute_list.add(attribute)
        print(attribute.name + " is an attribute")
    return 1


def check_add_object_attribute(described_attribute_list, xml_attribute_list, xml_function_list,
                               xml_fun_elem_list, xml_fun_inter_list, output_xml):
    """
    Check if each string in described_attribute_list are corresponding to an actual object and
    attribute, create new [Attribute, (Object, value)] objects list for object's type : Function
    and Functional Element.
    Send lists to add_object_attribute() to write them within xml and then returns update_list
    from it.

        Parameters:
            described_attribute_list ([str]) : Lists of string from jarvis cell
            xml_attribute_list ([Attribute]) : Attribute's list from xml
            xml_function_list ([Function]) : Function list from xml parsing
            xml_fun_elem_list ([Fun Elem]) : Functional Element list from xml parsing
            xml_fun_inter_list ([FunctionalInterface]) : FunctionalInterface list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    new_described_attribute_list = []
    # Create objects names/aliases list
    xml_attribute_name_list = get_objects_names(xml_attribute_list)
    xml_function_name_list = get_objects_names(xml_function_list)
    xml_fun_elem_name_list = get_objects_names(xml_fun_elem_list)
    xml_fun_inter_name_list = get_objects_names(xml_fun_inter_list)
    whole_list = xml_function_name_list + xml_fun_elem_name_list + xml_fun_inter_name_list

    # Loop to filter attributes and create a new list
    for elem in described_attribute_list:
        is_elem_found = True
        if not any(item == elem[1] for item in whole_list) and \
                not any(item == elem[0] for item in xml_attribute_name_list):
            is_elem_found = False
            print(f"{elem[1]} and {elem[0]} do not exist")
        elif not any(item == elem[1] for item in whole_list) or \
                not any(item == elem[0] for item in xml_attribute_name_list):
            is_elem_found = False
            if any(item == elem[1] for item in whole_list) and \
                    not any(item == elem[0] for item in xml_attribute_name_list):
                print(f"{elem[0]} does not exist")
            elif any(item == elem[0] for item in xml_attribute_name_list) and not \
                    any(item == elem[1] for item in whole_list):
                print(f"{elem[1]} does not exist")

        if is_elem_found:
            current_attrib = None
            for attribute in xml_attribute_list:
                if elem[0] == attribute.name or elem[0] == attribute.alias:
                    current_attrib = attribute
            # Loop to filter attribute and create a new list
            result_function = any(item == elem[1] for item in xml_function_name_list)
            result_fun_elem = any(item == elem[1]for item in xml_fun_elem_name_list)
            result_fun_inter = any(item == elem[1]for item in xml_fun_inter_name_list)

            if result_function and current_attrib:
                for function in xml_function_list:
                    if elem[1] == function.name or elem[1] == function.alias:
                        if (function.id, elem[2]) not in current_attrib.described_item_list:
                            new_described_attribute_list.append(
                                [current_attrib, (function, str(elem[2]))])

            if result_fun_elem and current_attrib:
                for fun_elem in xml_fun_elem_list:
                    if elem[1] == fun_elem.name or elem[1] == fun_elem.alias:
                        if (fun_elem.id, elem[2]) not in current_attrib.described_item_list:
                            new_described_attribute_list.append(
                                [current_attrib, (fun_elem, str(elem[2]))])

            if result_fun_inter and current_attrib:
                for fun_inter in xml_fun_inter_list:
                    if elem[1] == fun_inter.name or elem[1] == fun_inter.alias:
                        if (fun_inter.id, elem[2]) not in current_attrib.described_item_list:
                            new_described_attribute_list.append(
                                [current_attrib, (fun_inter, str(elem[2]))])

    update = add_object_attribute(new_described_attribute_list, output_xml)

    return update


def add_object_attribute(new_obj_attribute_list, output_xml):
    """
    Check if input list is not empty, write in xml for each element and return update list if some
    updates has been made

        Parameters:
            new_obj_attribute_list ([Attribute, (Object, value)]) : New described attributes
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if not new_obj_attribute_list:
        return 0

    output_xml.write_described_attribute_item(new_obj_attribute_list)
    # Warn the user once added within xml
    for described_attribute in new_obj_attribute_list:
        described_attribute[0].add_described_item(described_attribute[1])
        print(f"Attribute {described_attribute[0].name} for {described_attribute[1][0].name} "
              f"with value {described_attribute[1][1]}")
    return 1


def check_set_extends(extends_str_list, xml_type_list, output_xml):
    """
    Check if each type_to_extend string in extends_str_list are corresponding to actual objects
    name/alias, create lists for all <type> objects that needs to be added.

        Parameters:
            extends_str_list ([str]) : Lists of string from jarvis cell
            xml_type_list ([Type]) : xml list of type
            output_xml : xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    new_type_list = []
    # Capitalyze the reference type for datamodel matching
    for elem in extends_str_list:
        if any(t == elem[0] for t in get_objects_names(xml_type_list)):
            # print(f"{elem[0]} already exists")
            continue
        type_to_extend = check_get_type_to_extend(elem[1], xml_type_list)
        if not type_to_extend:
            print(f"Enable to find referenced type '{elem[1]}'")
            continue
        new_type = datamodel.Type()
        new_type.set_name(elem[0])
        # Generate and set unique identifier of length 10 integers
        identifier = uuid.uuid4()
        new_type.set_id(str(identifier.int)[:10])
        if isinstance(type_to_extend, datamodel.Type):
            new_type.set_base(type_to_extend)
        else:
            new_type.set_base(type_to_extend.get_enum(elem[1].capitalize()))
        new_type_list.append(new_type)
        xml_type_list.add(new_type)

    if not new_type_list:
        return 0

    output_xml.write_type_element(new_type_list)
    for obj_type in new_type_list:
        if isinstance(obj_type.base, datamodel.Type):
            base_type = obj_type.base.name
        else:
            base_type = obj_type.base
        print(f"{obj_type.name} is a type extending {str(base_type)}")
    return 1


def check_get_type_to_extend(type_str, xml_type_list):
    """Checks if type_str is within BaseType or xml_type_list, then return Basetype or
    type object"""
    check = None
    if any(a == type_str.capitalize() for a in [str(i) for i in datamodel.BaseType]):
        check = datamodel.BaseType
        return check

    if any(a == type_str for a in get_objects_names(xml_type_list)):
        check = check_get_object(type_str, **{'xml_type_list': xml_type_list})
        return check

    return check
