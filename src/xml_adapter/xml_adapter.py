#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module for xml parsing and object lists creation"""
# Libraries
from lxml import etree

# Modules
import datamodel
from .xml_writer import GenerateXML


def generate_xml(xml_file):
    """Call for xml class"""
    xml = GenerateXML(xml_file)
    return xml


def parse_xml(input_filename):
    """Parses the whole xml then returns lists of objects/relationship"""
    # To speed up parsing (see lxml doc) : TBC if can be extended to xml_writer
    parser = etree.XMLParser(collect_ids=False)
    # Parse the XML file
    tree = etree.parse(input_filename, parser)
    # Get the XML tree
    root = tree.getroot()
    # Check xml root tag
    if not check_xml(root):
        user_msg = f"Xml's file structure has changed, please delete {input_filename} " \
                   f"and re-execute your whole notebook"
        return user_msg
    # Looking for Type
    type_list = get_type_list(root)
    # looking for elements with tag "function" and create function objects and list
    function_list = get_functions(root)
    # Create data(and set predecessors), consumers, producers lists
    data_list, producer_function_list, consumer_function_list = get_data(root, function_list)
    # Looking for elements with tag "state" and create state objects and list
    state_list = get_state(root)
    # Looking for elements with tag "transition"
    transition_list = get_transition(root)
    # Looking for functional elements
    functional_element_list = get_functional_element(root)
    # Looking for chains
    chain_list = get_chains(root)
    # Looking for attributes
    attribute_list = get_attributes(root)
    # Looking for functional interfaces
    functional_interface_list = get_functional_interface(root)
    # Looking for physical elements
    physical_element_list = get_physical_element(root)
    # Looking for physical interfaces
    physical_interface_list = get_physical_interface(root)

    all_lists = [function_list, consumer_function_list, producer_function_list, data_list,
                 state_list, transition_list, functional_element_list, chain_list, attribute_list,
                 functional_interface_list, physical_element_list, physical_interface_list,
                 type_list]
    return all_lists


def check_xml(root):
    """Check xml file root, since jarvis4se version 1.3 it's <systemAnalysis>"""
    if root.tag == "systemAnalysis":
        return True
    else:
        return False


def get_functions(root):
    """Get Function objects"""
    function_list = set()
    parent_list = {}
    xml_function_list = root.iter('function')
    for xml_function in xml_function_list:
        # Instantiate functions and add them to a list
        function = datamodel.Function(p_id=xml_function.get('id'),
                                      p_name=xml_function.get('name'),
                                      p_type=xml_function.get('type'),
                                      p_alias=xml_function.get('alias'),
                                      p_derived=xml_function.get('derived'))
        function.set_operand()

        function_list.add(function)
        # Looking for functions with "functionalPart" i.e childs and create a list
        xml_function_part_list = xml_function.iter('functionPart')
        for xml_function_part in xml_function_part_list:
            parent_list[xml_function_part.get('id')] = function.id

    # Loop to set parent() and add_child() to functions
    for child_id in parent_list:
        for child_function in function_list:
            if child_function.id == child_id:
                for parent_function in function_list:
                    if parent_function.id == parent_list[child_id]:
                        child_function.set_parent(parent_function)
                        parent_function.add_child(child_function)
                        break
                break

    for elem in function_list:
        for derived in function_list:
            if elem.derived == derived.id:
                elem.derived = derived
                break

    return function_list


def get_data(root, function_list):
    """Get Data objects"""
    data_list = set()
    consumer_function_list = []
    producer_function_list = []

    xml_data_list = root.iter('data')
    for xml_data in xml_data_list:
        # Instantiate data and add it to a list
        data = datamodel.Data(p_id=xml_data.get('id'),
                              p_name=xml_data.get('name'),
                              p_type=xml_data.get('type'))
        data_list.add(data)
        # looking for all elements with tag "consumer" and create a list [flow, consumer_function]
        xml_consumer_list = xml_data.iter('consumer')
        for xml_consumer in xml_consumer_list:
            for function in function_list:
                if xml_consumer.get('id') == function.id:
                    consumer_function_list.append([xml_data.get('name'), function])
                    if xml_consumer.get('role') != 'none':
                        function.set_input_role(xml_data.get('name'))
                    # Avoid to reset the input role once already set
                    elif function.input_role is None:
                        function.set_input_role(None)

        # looking for all elements with tag "producer" and create a list [flow, producer_function]
        xml_producer_list = xml_data.iter('producer')
        for xml_producer in xml_producer_list:
            for function in function_list:
                if xml_producer.get('id') == function.id:
                    producer_function_list.append([xml_data.get('name'), function])

    # Loop on the data_list once created to find the predecessor and add it to list
    for d in data_list:
        xml_data_list = root.iter('data')
        for xml_data in xml_data_list:
            if xml_data.get('id') == d.id:
                # looking for all elements with tag "predecessor" and create a
                # list [flow, producer_function]
                xml_predecessor_list = xml_data.iter('predecessor')
                for xml_predecessor in xml_predecessor_list:
                    for dodo in data_list:
                        if xml_predecessor.get('id') == dodo.id:
                            d.add_predecessor(dodo)

    return data_list, producer_function_list, consumer_function_list


def get_state(root):
    """Get State objects"""
    state_list = set()
    state_parent_dict = {}
    xml_state_list = root.iter('state')
    for xml_state in xml_state_list:
        # Instantiate states and add them to a list
        state = datamodel.State(p_id=xml_state.get('id'),
                                p_name=xml_state.get('name'),
                                p_alias=xml_state.get('alias'),
                                p_type=xml_state.get('type'))
        state_list.add(state)
        # Looking for states with "statePart" i.e child and create a list
        xml_state_part_list = xml_state.iter('statePart')
        for xml_state_part in xml_state_part_list:
            state_parent_dict[xml_state_part.get('id')] = state.id

        # Looking for allocated functions and add them to the state
        xml_allocated_function_list = xml_state.iter('allocatedFunction')
        for xml_allo_fun in xml_allocated_function_list:
            state.add_allocated_function(xml_allo_fun.get("id"))

    # Loop to set parent() and add_child() to states
    for child_id in state_parent_dict:
        for child_state in state_list:
            if child_state.id == child_id:
                for parent_state in state_list:
                    if parent_state.id == state_parent_dict[child_id]:
                        child_state.set_parent(parent_state)
                        parent_state.add_child(child_state)
                        break
                break

    return state_list


def get_transition(root):
    """Get Transition objects"""
    transition_list = set()
    xml_transition_list = root.iter('transition')
    for xml_transition in xml_transition_list:
        # Instantiate transitions and add them to a list
        transition = datamodel.Transition(p_id=xml_transition.get('id'),
                                          p_name=xml_transition.get('name'),
                                          p_alias=xml_transition.get('alias'),
                                          p_type=xml_transition.get('type'),
                                          p_source=xml_transition.get('source'),
                                          p_destination=xml_transition.get('destination'))
        # Looking for conditions and add them to the transition
        xml_transition_condition_list = xml_transition.iter('condition')
        for xml_condition in xml_transition_condition_list:
            transition.add_condition(xml_condition.get("text"))

        transition_list.add(transition)

    return transition_list


def get_functional_element(root):
    """Get Functional Element objects"""
    functional_element_list = set()
    fun_elem_parent_dict = {}
    xml_functional_element_list = root.iter('functionalElement')
    for xml_func_elem in xml_functional_element_list:
        # Instantiate functional element and add them to a list
        fun_elem = datamodel.FunctionalElement(p_id=xml_func_elem.get('id'),
                                               p_name=xml_func_elem.get('name'),
                                               p_alias=xml_func_elem.get('alias'),
                                               p_type=xml_func_elem.get('type'),
                                               p_derived=xml_func_elem.get('derived'))
        functional_element_list.add(fun_elem)
        # Looking for "functionalElementPart" i.e child and create a list
        xml_functional_part_list = xml_func_elem.iter('functionalElementPart')
        for xml_state_part in xml_functional_part_list:
            fun_elem_parent_dict[xml_state_part.get('id')] = fun_elem.id

        # Looking for allocated states and add them to the functional element
        xml_allocated_state_list = xml_func_elem.iter('allocatedState')
        for xml_allo_state in xml_allocated_state_list:
            fun_elem.add_allocated_state(xml_allo_state.get("id"))

        # Looking for allocated functions and add them to the functional element
        xml_allocated_function_list = xml_func_elem.iter('allocatedFunction')
        for xml_allo_fun in xml_allocated_function_list:
            fun_elem.add_allocated_function(xml_allo_fun.get("id"))

        # Looking for exposed interface and add them to the functional element
        xml_exposed_interface_list = xml_func_elem.iter('exposedInterface')
        for xml_exp_inter in xml_exposed_interface_list:
            fun_elem.add_exposed_interface(xml_exp_inter.get("id"))

    # Loop to set parent() and add_child() to fun elem
    for child_id in fun_elem_parent_dict:
        for child_state in functional_element_list:
            if child_state.id == child_id:
                for parent_state in functional_element_list:
                    if parent_state.id == fun_elem_parent_dict[child_id]:
                        child_state.set_parent(parent_state)
                        parent_state.add_child(child_state)
                        break
                break

    for elem in functional_element_list:
        for derived in functional_element_list:
            if elem.derived == derived.id:
                elem.derived = derived
                break

    return functional_element_list


def get_chains(root):
    """Get Chain objects"""
    chain_list = set()
    xml_chain_list = root.iter('chain')
    for xml_chain in xml_chain_list:
        # Instantiate chain and add them to a list
        chain = datamodel.Chain(p_id=xml_chain.get('id'),
                                p_name=xml_chain.get('name'),
                                p_type=xml_chain.get('type'))
        # Looking for allocated items and add them to the chain
        xml_allocated_item_list = xml_chain.iter('allocatedItem')
        for xml_allo_item in xml_allocated_item_list:
            chain.add_allocated_item(xml_allo_item.get("id"))

        chain_list.add(chain)

    return chain_list


def get_attributes(root):
    """Get Attribute objects"""
    attribute_list = set()
    xml_attribute_list = root.iter('attribute')
    for xml_attribute in xml_attribute_list:
        # Instantiate Attribute and add them to a list
        attribute = datamodel.Attribute(p_id=xml_attribute.get('id'),
                                        p_name=xml_attribute.get('name'),
                                        p_alias=xml_attribute.get('alias'),
                                        p_type=xml_attribute.get('type'))
        # Looking for described items and add them to the attribute
        xml_described_item_list = xml_attribute.iter('describedItem')
        for xml_described_item in xml_described_item_list:
            attribute.add_described_item((xml_described_item.get("id"),
                                          xml_described_item.get("value")))

        attribute_list.add(attribute)

    return attribute_list


def get_functional_interface(root):
    """Get Functional Interface objects"""
    functional_interface_list = set()
    xml_fun_inter_list = root.iter('functionalInterface')
    for xml_fun_inter in xml_fun_inter_list:
        # Instantiate fun_inter and add them to a list
        fun_inter = datamodel.FunctionalInterface(p_id=xml_fun_inter.get('id'),
                                                  p_name=xml_fun_inter.get('name'),
                                                  p_alias=xml_fun_inter.get('alias'),
                                                  p_type=xml_fun_inter.get('type'),
                                                  p_derived=xml_fun_inter.get('derived'))
        # Looking for allocated data and add them to the fun inter
        xml_allocated_data_list = xml_fun_inter.iter('allocatedData')
        for xml_allo_data in xml_allocated_data_list:
            fun_inter.add_allocated_data(xml_allo_data.get("id"))

        functional_interface_list.add(fun_inter)

    for elem in functional_interface_list:
        for derived in functional_interface_list:
            if elem.derived == derived.id:
                elem.derived = derived
                break

    return functional_interface_list


def get_physical_element(root):
    """Get Physical Element objects"""
    physical_element_list = set()
    phy_elem_parent_dict = {}
    xml_physical_element_list = root.iter('physicalElement')
    for xml_phy_elem in xml_physical_element_list:
        # Instantiate functional element and add them to a list
        phy_elem = datamodel.PhysicalElement(p_id=xml_phy_elem.get('id'),
                                             p_name=xml_phy_elem.get('name'),
                                             p_alias=xml_phy_elem.get('alias'),
                                             p_type=xml_phy_elem.get('type'),
                                             p_derived=xml_phy_elem.get('derived'))
        physical_element_list.add(phy_elem)
        # Looking for "physicalPart" i.e child and create a list
        xml_functional_part_list = xml_phy_elem.iter('physicalElementPart')
        for xml_state_part in xml_functional_part_list:
            phy_elem_parent_dict[xml_state_part.get('id')] = phy_elem.id

        # Looking for allocated functions and add them to the functional element
        xml_allocated_fun_elem_list = xml_phy_elem.iter('allocatedFunctionalElement')
        for xml_allo_fun_elem in xml_allocated_fun_elem_list:
            phy_elem.add_allocated_fun_elem(xml_allo_fun_elem.get("id"))

        # Looking for exposed interface and add them to the functional element
        xml_exposed_interface_list = xml_phy_elem.iter('exposedInterface')
        for xml_exp_inter in xml_exposed_interface_list:
            phy_elem.add_exposed_interface(xml_exp_inter.get("id"))

    # Loop to set parent() and add_child() to fun elem
    for child_id in phy_elem_parent_dict:
        for child_state in physical_element_list:
            if child_state.id == child_id:
                for parent_state in physical_element_list:
                    if parent_state.id == phy_elem_parent_dict[child_id]:
                        child_state.set_parent(parent_state)
                        parent_state.add_child(child_state)
                        break
                break

    for elem in physical_element_list:
        for derived in physical_element_list:
            if elem.derived == derived.id:
                elem.derived = derived
                break

    return physical_element_list


def get_physical_interface(root):
    """Get Physical Interface objects"""
    physical_interface_list = set()
    xml_phy_inter_list = root.iter('physicalInterface')
    for xml_phy_inter in xml_phy_inter_list:
        # Instantiate phy_inter and add them to a list
        phy_inter = datamodel.PhysicalInterface(p_id=xml_phy_inter.get('id'),
                                                p_name=xml_phy_inter.get('name'),
                                                p_alias=xml_phy_inter.get('alias'),
                                                p_type=xml_phy_inter.get('type'),
                                                p_derived=xml_phy_inter.get('derived'))
        # Looking for allocated fun_inter and add them to the phy inter
        xml_allocated_inter_list = xml_phy_inter.iter('allocatedFunctionalInterface')
        for xml_allo_inter in xml_allocated_inter_list:
            phy_inter.add_allocated_fun_inter(xml_allo_inter.get("id"))

        physical_interface_list.add(phy_inter)

    for inter in physical_interface_list:
        for derived in physical_interface_list:
            if inter.derived == derived.id:
                inter.derived = derived
                break

    return physical_interface_list


def get_type_list(root):
    """Get Type objects"""
    type_list = set()
    xml_type_list = root.iter('type')
    for xml_type in xml_type_list:
        # Instantiate Type and add them to a list
        type_obj = datamodel.Type(p_id=xml_type.get('id'),
                                  p_name=xml_type.get('name'),
                                  p_alias=xml_type.get('alias'),
                                  p_base=xml_type.get('base'))
        type_list.add(type_obj)

    for obj_type in type_list:
        for base in type_list:
            if obj_type.base == base.name:
                obj_type.base = base
                break

    return type_list
