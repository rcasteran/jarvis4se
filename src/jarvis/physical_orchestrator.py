#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import re

import datamodel
from .question_answer import get_objects_names
from . import shared_orchestrator


def create_phy_elem_obj(phy_elem_str, specific_obj_type, **kwargs):
    """
    Check if string phy_elem_str is not already corresponding to an actual object's name/alias,
    create new PhysicalElement() object, instantiate it, add it to xml_phy_elem_list.

        Parameters:
            phy_elem_str (str) : Lists of string from jarvis cell
            specific_obj_type ([Function]) : specific type or None
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update (0/fun_elem) : fun_elem if update, else 0
    """
    if any(n == phy_elem_str for n in get_objects_names(kwargs['xml_phy_elem_list'])):
        return 0
    if not specific_obj_type:
        phy_elem = datamodel.PhysicalElement(p_name=phy_elem_str)
    else:
        phy_elem = datamodel.PhysicalElement(p_name=phy_elem_str, p_type=specific_obj_type.name)

    alias_str = re.search(r"(.*)\s[-]\s", phy_elem_str, re.MULTILINE)
    if alias_str:
        phy_elem.set_alias(alias_str.group(1))
    phy_elem.set_id(shared_orchestrator.get_unique_id())

    kwargs['xml_phy_elem_list'].add(phy_elem)
    print(f"{phy_elem.name} is a {phy_elem.type}")
    if phy_elem:
        return phy_elem
    return 0


def create_phy_inter_obj(phy_inter_str, specific_obj_type, **kwargs):
    """
    Check if string phy_inter_str is not already corresponding to an actual object's name/alias,
    create new PhysicalElement() object, instantiate it, add it to xml_phy_inter_list.

        Parameters:
            phy_inter_str (str) : Lists of string from jarvis cell
            specific_obj_type ([Function]) : specific type or None
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update (0/fun_elem) : fun_elem if update, else 0
    """
    if any(n == phy_inter_str for n in get_objects_names(kwargs['xml_phy_inter_list'])):
        return 0
    if not specific_obj_type:
        phy_inter = datamodel.PhysicalInterface(p_name=phy_inter_str)
    else:
        phy_inter = datamodel.PhysicalInterface(p_name=phy_inter_str, p_type=specific_obj_type.name)

    alias_str = re.search(r"(.*)\s[-]\s", phy_inter_str, re.MULTILINE)
    if alias_str:
        phy_inter.set_alias(alias_str.group(1))
    phy_inter.set_id(shared_orchestrator.get_unique_id())

    kwargs['xml_phy_inter_list'].add(phy_inter)
    print(f"{phy_inter.name} is a {phy_inter.type}")
    if phy_inter:
        return phy_inter
    return 0
