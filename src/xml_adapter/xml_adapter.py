#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import sys
from lxml import etree

# Modules
from . import xml_writer # noqa
sys.path.append("../datamodel")
import datamodel # noqa


def generate_xml(xml_file):
    xml = xml_writer.GenerateXML(xml_file)
    return xml


# TODO: Delete dict not useful -> TBC
def parse_xml(input_filename):
    # Parse the XML file
    tree = etree.parse(input_filename)
    # Get the XML tree
    root = tree.getroot()
    # looking for elements with tag "function" and create function objects and list
    function_list, function_parent_list = get_functions(root)
    # Create data(and set predecessors), consumers, producers lists
    data_list, producer_function_list, consumer_function_list = get_data(root, function_list)
    # Looking for elements with tag "state" and create state objects and list
    state_list, state_parent_dict = get_state(root)
    # Looking for elements with tag "transition"
    transition_list = get_transition(root)
    # Looking for functional elements
    functional_element_list, fun_elem_parent_dict = get_functional_element(root)
    # Looking for chains
    chain_list = get_chains(root)
    # Looking for attributes
    attribute_list = get_attributes(root)

    all_lists = [function_list, consumer_function_list, producer_function_list,
                 function_parent_list, data_list, state_list, state_parent_dict, transition_list,
                 functional_element_list, fun_elem_parent_dict, chain_list, attribute_list]
    return all_lists


def get_functions(root):
    function_list = set()
    parent_list = {}
    xml_function_list = root.iter('function')
    for xml_function in xml_function_list:
        # Instantiate functions and add them to a list
        function = datamodel.Function()
        function.set_id(xml_function.get('id'))
        function.set_name(xml_function.get('name'))
        function.set_alias(xml_function.get('alias'))
        function_type = datamodel.FunctionType.get_name(xml_function.get('type'))
        function.set_type(function_type)
        function.set_operand()

        function_list.add(function)
        # Looking for functions with "functionalPart" i.e childs and create a list
        xml_function_part_list = xml_function.iter('functionalPart')
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

    return function_list, parent_list


# TODO: Change consumer/producer list from [data_name, function] to [data, function] and
#  extend it to all scripts
def get_data(root, function_list):
    data_list = set()
    consumer_function_list = []
    producer_function_list = []

    xml_data_list = root.iter('data')
    for xml_data in xml_data_list:
        # Instantiate data and add it to a list
        data = datamodel.Data()
        data.set_id(xml_data.get('id'))
        data.set_name(xml_data.get('name'))
        data_type = datamodel.DataType.get_name(xml_data.get('type'))
        data.set_type(data_type)

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
    state_list = set()
    state_parent_dict = {}
    xml_state_list = root.iter('state')
    for xml_state in xml_state_list:
        # Instantiate states and add them to a list
        state = datamodel.State()
        state.set_id(xml_state.get('id'))
        state.set_name(xml_state.get('name'))
        state.set_alias(xml_state.get('alias'))
        state_type = datamodel.StateType.get_name(xml_state.get('type'))
        state.set_type(state_type)

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

    return state_list, state_parent_dict


def get_transition(root):
    transition_list = set()
    xml_transition_list = root.iter('transition')
    for xml_transition in xml_transition_list:
        # Instantiate transitions and add them to a list
        transition = datamodel.Transition()
        transition.set_id(xml_transition.get('id'))
        transition.set_name(xml_transition.get('name'))
        transition.set_alias(xml_transition.get('alias'))
        transition_type = datamodel.TransitionType.get_name(xml_transition.get('type'))
        transition.set_type(transition_type)
        transition.set_source(xml_transition.get('source'))
        transition.set_destination(xml_transition.get('destination'))

        # Looking for conditions and add them to the transition
        xml_transition_condition_list = xml_transition.iter('condition')
        for xml_condition in xml_transition_condition_list:
            transition.add_condition(xml_condition.get("text"))

        transition_list.add(transition)

    return transition_list


def get_functional_element(root):
    functional_element_list = set()
    fun_elem_parent_dict = {}
    xml_functional_element_list = root.iter('functionalElement')
    for xml_func_elem in xml_functional_element_list:
        # Instantiate functional element and add them to a list
        fun_elem = datamodel.FunctionalElement()
        fun_elem.set_id(xml_func_elem.get('id'))
        fun_elem.set_name(xml_func_elem.get('name'))
        fun_elem.set_alias(xml_func_elem.get('alias'))
        fun_elem_type = datamodel.FunctionalElementType.get_name(xml_func_elem.get('type'))
        fun_elem.set_type(fun_elem_type)

        functional_element_list.add(fun_elem)
        # Looking for states with "functionalElementPart" i.e child and create a list
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

    return functional_element_list, fun_elem_parent_dict


def get_chains(root):
    chain_list = set()
    xml_chain_list = root.iter('chain')
    for xml_chain in xml_chain_list:
        # Instantiate chain and add them to a list
        chain = datamodel.Chain()
        chain.set_id(xml_chain.get('id'))
        chain.set_name(xml_chain.get('name'))
        chain_type = datamodel.ChainType.get_name(xml_chain.get('type'))
        chain.set_type(chain_type)

        # Looking for allocated items and add them to the chain
        xml_allocated_item_list = xml_chain.iter('allocatedItem')
        for xml_allo_item in xml_allocated_item_list:
            chain.add_allocated_item(xml_allo_item.get("id"))

        chain_list.add(chain)

    return chain_list


def get_attributes(root):
    attribute_list = set()
    xml_attribute_list = root.iter('attribute')
    for xml_attribute in xml_attribute_list:
        # Instantiate Attribute and add them to a list
        attribute = datamodel.Attribute()
        attribute.set_id(xml_attribute.get('id'))
        attribute.set_name(xml_attribute.get('name'))
        attribute.set_alias(xml_attribute.get('alias'))
        # No AttritubeType defined in datamodel yet
        # attribute_type = datamodel.AttributeType.get_name(xml_attribute.get('type'))
        attribute.set_type(xml_attribute.get('type'))

        # Looking for described items and add them to the attribute
        xml_described_item_list = xml_attribute.iter('describedItem')
        for xml_described_item in xml_described_item_list:
            attribute.add_described_item((xml_described_item.get("id"),
                                          xml_described_item.get("value")))

        attribute_list.add(attribute)

    return attribute_list
