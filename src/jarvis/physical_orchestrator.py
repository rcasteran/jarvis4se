#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import sys
import uuid
import re

from . import functional_orchestrator
from .question_answer import get_object_name, check_get_object
sys.path.append("../datamodel")
import datamodel # noqa


def add_phy_elem_by_name(physical_elem_name_str_list, xml_phy_elem_list, output_xml):
    """
    Check if each string in physical_elem_name_str_list is not already corresponding to an actual
    object's name/alias, create new PhysicalElement() object, instantiate it, write it
    within XML and then returns update_list.

        Parameters:
            physical_elem_name_str_list ([str]) : Lists of string from jarvis cell
            xml_phy_elem_list ([PhysicalElement]) : PhysicalElement list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """
    phy_elem_list = set()

    for phy_elem_name in physical_elem_name_str_list:
        if check_get_object(phy_elem_name, **{'xml_phy_elem_list': xml_phy_elem_list}) is None:

            phy_elem = datamodel.PhysicalElement()
            phy_elem.set_name(str(phy_elem_name))
            alias_str = re.search(r"(.*)\s[-]\s", phy_elem_name, re.MULTILINE)
            if alias_str:
                phy_elem.set_alias(alias_str.group(1))
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            phy_elem.set_id(str(identifier.int)[:10])

            xml_phy_elem_list.add(phy_elem)
            phy_elem_list.add(phy_elem)
        else:
            # print(fun_elem_name + " already exists (not added)")
            pass

    if not phy_elem_list:
        return 0
    else:
        output_xml.write_physical_element(phy_elem_list)
        for phy_elem in phy_elem_list:
            print(phy_elem.name + " is a physical element")
        return 1


def add_phy_inter_by_name(physical_inter_name_str_list, xml_phy_inter_list, output_xml):
    """
    Check if each string in physical_inter_name_str_list is not already corresponding to an actual
    object's name/alias, create new PhysicalInterface() object, instantiate it, write it
    within XML and then returns update_list.

        Parameters:
            physical_inter_name_str_list ([str]) : Lists of string from jarvis cell
            xml_phy_inter_list ([PhysicalInterface]) : PhysicalInterface list from xml parsing
            output_xml (GenerateXML object) : XML's file object

        Returns:
            1 if update, else 0
    """

    physical_interface_list = set()

    for phy_inter_name in physical_inter_name_str_list:
        if check_get_object(phy_inter_name, **{'xml_phy_inter_list': xml_phy_inter_list}) is None:

            phy_inter = datamodel.PhysicalInterface()
            phy_inter.set_name(str(phy_inter_name))
            alias_str = re.search(r"(.*)\s[-]\s", phy_inter_name, re.MULTILINE)
            if alias_str:
                phy_inter.set_alias(alias_str.group(1))
            # Generate and set unique identifier of length 10 integers
            identifier = uuid.uuid4()
            phy_inter.set_id(str(identifier.int)[:10])

            xml_phy_inter_list.add(phy_inter)
            physical_interface_list.add(phy_inter)
        else:
            # print(fun_elem_name + " already exists (not added)")
            pass

    if not physical_interface_list:
        return 0
    else:
        output_xml.write_physical_interface(physical_interface_list)
        for phy_inter in physical_interface_list:
            print(phy_inter.name + " is a physical interface")

        return 1
