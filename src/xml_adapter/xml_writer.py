#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
from lxml import etree

import datamodel


# Class to generate XML
class GenerateXML:
    def __init__(self, xml_file):
        # Initialize XML structure/tags
        self.root = etree.Element("systemAnalysis")
        fun_arch = etree.SubElement(self.root, "funcArch")
        fun_arch_tags = ['functionList', 'dataList', 'stateList', 'transitionList',
                         'functionalElementList', 'functionalInterfaceList']
        for tag in fun_arch_tags:
            etree.SubElement(fun_arch, tag)
        phy_arch = etree.SubElement(self.root, "phyArch")
        phy_arch_tags = ['physicalElementList', 'physicalInterfaceList']
        for tag in phy_arch_tags:
            etree.SubElement(phy_arch, tag)
        viewpoint = etree.SubElement(self.root, "viewPoint")
        viewpoint_tags = ['chainList', 'attributeList']
        for tag in viewpoint_tags:
            etree.SubElement(viewpoint, tag)
        self.tree = etree.ElementTree(self.root)

        if len(xml_file) > 0:
            self.file = xml_file
        else:
            self.file = "Output.xml"

    # Method to write functions from function's list
    def write_function(self, function_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//functionList') is None:
                etree.SubElement(root, 'functionList')
            # Loop on each flow/data
            for function_list_tag in root.findall(".//functionList"):
                # Loop on function's list
                for function in function_list:
                    function_tag = etree.SubElement(function_list_tag, "function",
                                                    {'id': function.id,
                                                     'name': function.name,
                                                     'type': str(function.type),
                                                     'alias': function.alias,
                                                     'derived': function.derived})

                    _functional_part_list_tag = etree.SubElement(function_tag, "functionalPartList")

        self.write()

    # Method to write function's alias by list [function, alias]
    def write_function_alias(self, function_alias_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on [function, type] list
            for function in function_alias_list:
                for function_tag in root.findall(".//function[@id='" + function[0].id + "']"):
                    function_tag.set('alias', function[1])
        self.write()

    # Method to write child by list [parent, child]
    def write_function_child(self, child_function_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each flow/data
            for function in root.findall(".//function"):
                for parent, child in child_function_list:
                    if function.get('id') == parent.id:
                        tag = function.find('functionalPartList')
                        _functional_part_tag = etree.SubElement(tag, "functionalPart",
                                                                {'id': child.id})
        self.write()

    # Method to add data flows
    def write_data(self, data_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//dataList') is None:
                etree.SubElement(root, 'dataList')
            for data_list_tag in root.findall('.//dataList'):
                for data in data_list:
                    existing_data_tag = data_list_tag.find('.//dataList/data')
                    if existing_data_tag is not None:
                        tag = existing_data_tag
                    else:
                        tag = data_list_tag
                    data_tag = etree.SubElement(tag, "data", {'name': data.name,
                                                              'type': str(data.type),
                                                              'id': data.id})

                    _consumer_list_tag = etree.SubElement(data_tag, "consumerList")

                    _producer_list_tag = etree.SubElement(data_tag, "producerList")

                    _predecessor_list_tag = etree.SubElement(data_tag, "predecessorList")

        self.write()

    # Method to write consumers by list [data_name, function]
    def write_consumer(self, consumer_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for i in consumer_list:
                for consumer_list_tag in root.findall(".//dataList/data[@name='" + str(i[0])
                                                      + "']/consumerList"):
                    if not i[1].operand:
                        _consumer_tag = etree.SubElement(consumer_list_tag, "consumer",
                                                         {'id': i[1].id, 'role': "none"})
                    else:
                        _consumer_tag = etree.SubElement(consumer_list_tag, "consumer",
                                                         {'id': i[1].id, 'role': i[1].operand})

        self.write()

    # Method to write producers by list [data_name, function]
    def write_producer(self, producer_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for i in producer_list:
                for producer_list_tag in root.findall(".//dataList/data[@name='" + str(i[0])
                                                      + "']/producerList"):

                    _producer_tag = etree.SubElement(producer_list_tag, "producer", {'id': i[1].id})

        self.write()

    # Method to write predecessors by list [data, predecessor]
    def write_predecessor(self, predecessor_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for i in predecessor_list:
                for predecessor_list_tag in root.findall(
                        ".//dataList/data[@name='" + str(i[0].name) + "']/predecessorList"):

                    _producer_tag = etree.SubElement(predecessor_list_tag, "predecessor",
                                                     {'id': i[1].id})

        self.write()

    # Method to remove function by list [function]
    def delete_function(self, delete_function_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for function in delete_function_list:
                for function_tag in root.findall(".//function[@id='" + function.id + "']"):
                    function_tag.getparent().remove(function_tag)
        self.write()

    # Method to remove data by list [data]
    def delete_data(self, delete_data_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for data in delete_data_list:
                for data_tag in root.findall(".//data[@name='" + data.name + "']"):
                    data_tag.getparent().remove(data_tag)
        self.write()

    # Method to delete the parents (consumer or producer) when flow is within a component
    def delete_single_consumer_producer(self, data, function, value):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Find specific consumer/producer to delete
            for tag in root.findall(
                    ".//data[@name='" + data + "']/" + value + "List/" + value + "[@id='"
                    + function.id + "']"):
                tag.getparent().remove(tag)
        self.write()

    # Method to write within XML file
    def write(self):
        with open(self.file, "wb") as file:
            self.tree.write(file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    # Method to write states from state's list
    def write_state(self, state_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//stateList') is None:
                etree.SubElement(root, 'stateList')
            for state_list_tag in root.findall(".//stateList"):
                for state in state_list:
                    state_tag = etree.SubElement(state_list_tag, "state",
                                                 {'id': state.id, 'name': state.name,
                                                  'type': str(state.type), 'alias': state.alias})

                    _state_part_list_tag = etree.SubElement(state_tag, "statePartList")
                    _allocated_function_list_tag = etree.SubElement(state_tag,
                                                                    "allocatedFunctionList")
        self.write()

    # Method to write state's alias by list [function, alias]
    def write_state_alias(self, state_alias_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for state in state_alias_list:
                for state_tag in root.findall(".//state[@id='" + state[0].id + "']"):
                    state_tag.set('alias', state[1])
        self.write()

    # Method to write child's state by list [parent, child]
    def write_state_child(self, child_state_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each state
            for state in root.findall(".//state"):
                for parent, child in child_state_list:
                    if state.get('id') == parent.id:
                        tag = state.find('statePartList')
                        _state_part_tag = etree.SubElement(tag, "statePart",
                                                           {'id': child.id})
        self.write()

    # Method to write allocated function by list [state, allocated_function]
    def write_allocated_function_to_state(self, state_function_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each flow/data
            for xml_state in root.findall(".//state"):
                for fun_elem, function in state_function_list:
                    if xml_state.get('id') == fun_elem.id:
                        tag = xml_state.find('allocatedFunctionList')
                        _allocated_state_tag = etree.SubElement(tag, "allocatedFunction",
                                                                {'id': function.id})
        self.write()

    # Method to delete state by list [state]
    def delete_state(self, delete_state_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for state in delete_state_list:
                for state_tag in root.findall(".//state[@id='" + state.id + "']"):
                    state_tag.getparent().remove(state_tag)
        self.write()

    # Method to write transition from transition's list
    def write_transition(self, transition_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//transitionList') is None:
                etree.SubElement(root, 'transitionList')
            for transition_list_tag in root.findall(".//transitionList"):
                for transition in transition_list:
                    transition_tag = etree.SubElement(transition_list_tag, "transition",
                                                      {'id': transition.id,
                                                       'name': transition.name,
                                                       'type': str(transition.type),
                                                       'alias': transition.alias,
                                                       'source': str(transition.source),
                                                       'destination': str(transition.destination)})
                    _transition_part_list_tag = etree.SubElement(transition_tag, "conditionList")
        self.write()

    # Method to write transition's alias by list [transition, alias]
    def write_transition_alias(self, transition_alias_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for transition in transition_alias_list:
                for transition_tag in root.findall(".//transition[@id='" + transition[0].id + "']"):
                    transition_tag.set('alias', transition[1])
        self.write()

    # Method to write transition's condition by list [transition, condition]
    def write_transition_condition(self, transition_condition_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for transition in root.findall(".//transition"):
                for tra, condition in transition_condition_list:
                    if transition.get('id') == tra.id:
                        tag = transition.find('conditionList')
                        _state_part_tag = etree.SubElement(tag, "condition",
                                                           {'text': str(condition)})
        self.write()

    # Method to write transition's source by list [transition, source]
    def write_source(self, transition_source_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for transition_src in transition_source_list:
                for state_tag in root.findall(".//transition[@id='" + transition_src[0].id + "']"):
                    state_tag.set('source', transition_src[1].id)
        self.write()

    # Method to write transition's destination by list [transition, destination]
    def write_destination(self, transition_destination_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for transition_dest in transition_destination_list:
                for state_tag in root.findall(".//transition[@id='" + transition_dest[0].id + "']"):
                    state_tag.set('destination', transition_dest[1].id)
        self.write()

    # Method to delete transition by list [transition]
    def delete_transition(self, delete_transition_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for transition in delete_transition_list:
                for transition_tag in root.findall(".//transition[@id='" + transition.id + "']"):
                    transition_tag.getparent().remove(transition_tag)
        self.write()

    # Method to write functional element from functional elements list
    def write_functional_element(self, functional_element_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//functionalElementList') is None:
                etree.SubElement(root, 'functionalElementList')
            for functional_element_list_tag in root.findall(".//functionalElementList"):
                for functional_element in functional_element_list:
                    functional_element_tag = etree.SubElement(
                        functional_element_list_tag, "functionalElement",
                        {
                            'id': functional_element.id,
                            'name': functional_element.name,
                            'type': str(
                                functional_element.type),
                            'alias': functional_element.alias,
                            'derived': functional_element.derived}
                    )

                    _fun_elem_part_list_tag = etree.SubElement(functional_element_tag,
                                                               "functionalElementPartList")
                    _allocated_state_list_tag = etree.SubElement(functional_element_tag,
                                                                 "allocatedStateList")
                    _allocated_function_list_tag = etree.SubElement(functional_element_tag,
                                                                    "allocatedFunctionList")
                    _exposed_interface_list_tag = etree.SubElement(functional_element_tag,
                                                                   "exposedInterfaceList")
        self.write()

    # Method to write child by list [parent, child]
    def write_functional_element_child(self, fun_elem_child_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each flow/data
            for functional_element in root.findall(".//functionalElement"):
                for parent, child in fun_elem_child_list:
                    if functional_element.get('id') == parent.id:
                        tag = functional_element.find('functionalElementPartList')
                        _functional_element_part_tag = etree.SubElement(tag,
                                                                        "functionalElementPart",
                                                                        {'id': child.id})
        self.write()

    # Method to write allocated state by list [fun_elem, allocated_state]
    def write_allocated_state(self, fun_elem_state_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each flow/data
            for functional_element in root.findall(".//functionalElement"):
                for fun_elem, state in fun_elem_state_list:
                    if functional_element.get('id') == fun_elem.id:
                        tag = functional_element.find('allocatedStateList')
                        _allocated_state_tag = etree.SubElement(tag, "allocatedState",
                                                                {'id': state.id})
        self.write()

    # Method to write allocated function by list [fun_elem, allocated_function]
    def write_allocated_function(self, fun_elem_function_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each flow/data
            for functional_element in root.findall(".//functionalElement"):
                for fun_elem, function in fun_elem_function_list:
                    if functional_element.get('id') == fun_elem.id:
                        tag = functional_element.find('allocatedFunctionList')
                        _allocated_state_tag = etree.SubElement(tag, "allocatedFunction",
                                                                {'id': function.id})
        self.write()

    # Method to write exposed interfaces by list [fun_elem, exposed_interface]
    def write_exposed_interface(self, fun_elem_inter_list):
        if isinstance(fun_elem_inter_list[0][0], datamodel.FunctionalElement):
            string_tag = ".//functionalElement"
        else:
            string_tag = ".//physicalElement"
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for functional_element in root.findall(string_tag):
                if functional_element.find('exposedInterfaceList') is None:
                    etree.SubElement(functional_element, 'exposedInterfaceList')

                for fun_elem, inter in fun_elem_inter_list:
                    if functional_element.get('id') == fun_elem.id:
                        tag = functional_element.find('exposedInterfaceList')
                        _exposed_interface_tag = etree.SubElement(tag, "exposedInterface",
                                                                  {'id': inter.id})
        self.write()

    # Method to delete functional element by list [functional element]
    def delete_functional_element(self, delete_fun_elem_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for fun_elem in delete_fun_elem_list:
                for fun_elem_tag in root.findall(".//functionalElement[@id='" + fun_elem.id + "']"):
                    fun_elem_tag.getparent().remove(fun_elem_tag)
        self.write()

    # Method to write fun_elem's alias by list [fun_elem, alias]
    def write_fun_elem_alias(self, fun_elem_alias_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for fun_elem in fun_elem_alias_list:
                for fun_elem_tag in root.findall(".//functionalElement[@id='" + fun_elem[0].id
                                                 + "']"):
                    fun_elem_tag.set('alias', fun_elem[1])
        self.write()

    # Method to write chains from chain's list
    def write_chain(self, chain_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//chainList') is None:
                etree.SubElement(root, 'chainList')
            for chain_list_tag in root.findall(".//chainList"):
                for chain in chain_list:
                    chain_tag = etree.SubElement(chain_list_tag, "chain",
                                                 {'id': chain.id, 'name': chain.name,
                                                  'type': str(chain.type)})
                    _allocated_item_list_tag = etree.SubElement(chain_tag, "allocatedItemList")
        self.write()

    # Method to write allocated item by list [chain, allocated_item]
    def write_allocated_chain_item(self, chain_item_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each flow/data
            for chain_element in root.findall(".//chain"):
                for chain, item in chain_item_list:
                    if chain_element.get('id') == chain.id:
                        tag = chain_element.find('allocatedItemList')
                        _allocated_item_tag = etree.SubElement(tag, "allocatedItem",
                                                               {'id': item.id})
        self.write()

    # Method to write attributes from attribute's list
    def write_attribute(self, attribute_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//attributeList') is None:
                etree.SubElement(root, 'attributeList')
            for attribute_list_tag in root.findall(".//attributeList"):
                for attribute in attribute_list:
                    attribute_tag = etree.SubElement(attribute_list_tag, "attribute",
                                                     {'id': attribute.id, 'name': attribute.name,
                                                      'type': str(attribute.type),
                                                      'alias': attribute.alias})

                    _described_item_list_tag = etree.SubElement(attribute_tag, "describedItemList")

        self.write()

    # Method to write described item by list [attribute, (described_item, value)]
    def write_described_attribute_item(self, attribute_item_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each attribute
            for attribute_element in root.findall(".//attribute"):
                for attribute, item in attribute_item_list:
                    if attribute_element.get('id') == attribute.id:
                        tag = attribute_element.find('describedItemList')
                        _allocated_item_tag = etree.SubElement(tag, "describedItem",
                                                               {'id': item[0].id, 'value': item[1]})
        self.write()

    # Method to write functional interfaces from interface's list
    def write_functional_interface(self, functional_interface_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//functionalInterfaceList') is None:
                etree.SubElement(root, 'functionalInterfaceList')
            for fun_interface_list_tag in root.findall(".//functionalInterfaceList"):
                for fun_interface in functional_interface_list:
                    fun_interface_tag = etree.SubElement(fun_interface_list_tag,
                                                         "functionalInterface",
                                                         {'id': fun_interface.id,
                                                          'name': fun_interface.name,
                                                          'type': str(fun_interface.type),
                                                          'alias': fun_interface.alias,
                                                          'derived': fun_interface.derived})
                    _allocated_data_list_tag = etree.SubElement(fun_interface_tag,
                                                                "allocatedDataList")
        self.write()

    # Method to write allocated data by list [Functional Interface, allocated_data]
    def write_fun_interface_allocated_data(self, fun_inter_data_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Loop on each flow/data
            for fun_interface_tag in root.findall(".//functionalInterface"):
                for fun_interface, data in fun_inter_data_list:
                    if fun_interface_tag.get('id') == fun_interface.id:
                        tag = fun_interface_tag.find('allocatedDataList')
                        _allocated_data_tag = etree.SubElement(tag, "allocatedData",
                                                               {'id': data.id})
        self.write()

    # Method to write fun_inter's alias by list [fun_inter, alias]
    def write_fun_interface_alias(self, fun_inter_alias_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for fun_inter_alias in fun_inter_alias_list:
                for fun_inter_tag in root.findall(".//functionalInterface[@id='" +
                                                  fun_inter_alias[0].id + "']"):
                    fun_inter_tag.set('alias', fun_inter_alias[1])
        self.write()

    # Method to write physical element from physical elements list
    def write_physical_element(self, physical_element_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//physicalElementList') is None:
                etree.SubElement(root, 'physicalElementList')
            for physical_element_list_tag in root.findall(".//physicalElementList"):
                for physical_element in physical_element_list:
                    physical_element_tag = etree.SubElement(
                        physical_element_list_tag, "physicalElement",
                        {
                            'id': physical_element.id,
                            'name': physical_element.name,
                            'type': str(
                                physical_element.type),
                            'alias': physical_element.alias,
                            'derived': physical_element.derived}
                    )

                    _phy_elem_part_list_tag = etree.SubElement(physical_element_tag,
                                                               "physicalElementPartList")
                    _allocated_fun_elem_list_tag = etree.SubElement(
                        physical_element_tag, "allocatedFunctionalElementList")
                    _exposed_interface_list_tag = etree.SubElement(physical_element_tag,
                                                                   "exposedInterfaceList")
        self.write()

    # Method to write child by list [parent, child]
    def write_physical_element_child(self, phy_elem_child_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)

            for physical_element in root.findall(".//physicalElement"):
                for parent, child in phy_elem_child_list:
                    if physical_element.get('id') == parent.id:
                        tag = physical_element.find('physicalElementPartList')
                        _phy_element_part_tag = etree.SubElement(tag,
                                                                 "physicalElementPart",
                                                                 {'id': child.id})
        self.write()

    # Method to write allocated fun_elem by list [phy_elem, allocated_fun_elem]
    def write_allocated_fun_elem(self, phy_elem_fun_elem_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)

            for physical_element in root.findall(".//physicalElement"):
                for phy_elem, fun_elem in phy_elem_fun_elem_list:
                    if physical_element.get('id') == phy_elem.id:
                        tag = physical_element.find('allocatedFunctionalElementList')
                        _allocated_fun_elem_tag = etree.SubElement(
                            tag, "allocatedFunctionalElement", {'id': fun_elem.id})
        self.write()

    # Method to delete functional element by list [physical element]
    def delete_physical_element(self, delete_phy_elem_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for phy_elem in delete_phy_elem_list:
                for phy_elem_tag in root.findall(".//physicalElement[@id='" + phy_elem.id + "']"):
                    phy_elem_tag.getparent().remove(phy_elem_tag)
        self.write()

    # Method to write phy_elem's alias by list [phy_elem]
    def write_phy_elem_alias(self, phy_elem_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for phy_elem in phy_elem_list:
                for phy_elem_tag in root.findall(".//physicalElement[@id='" + phy_elem.id
                                                 + "']"):
                    phy_elem_tag.set('alias', str(phy_elem.alias))
        self.write()

    # Method to write physical interfaces from interface's list
    def write_physical_interface(self, physical_interface_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//physicalInterfaceList') is None:
                etree.SubElement(root, 'physicalInterfaceList')
            for phy_interface_list_tag in root.findall(".//physicalInterfaceList"):
                for phy_interface in physical_interface_list:
                    phy_interface_tag = etree.SubElement(phy_interface_list_tag,
                                                         "physicalInterface",
                                                         {'id': phy_interface.id,
                                                          'name': phy_interface.name,
                                                          'type': str(phy_interface.type),
                                                          'alias': phy_interface.alias,
                                                          'derived': phy_interface.derived})
                    _allocated_fun_inter_list_tag = etree.SubElement(
                        phy_interface_tag, "allocatedFunctionalInterfaceList")
        self.write()

    # Method to write allocated fun_inter by list [Physical Interface, allocated_fun_inter]
    def write_phy_interface_allocated_fun_inter(self, phy_inter_fun_inter_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)

            for phy_interface_tag in root.findall(".//physicalInterface"):
                for phy_interface, fun_inter in phy_inter_fun_inter_list:
                    if phy_interface_tag.get('id') == phy_interface.id:
                        tag = phy_interface_tag.find('allocatedFunctionalInterfaceList')
                        _allocated_fun_inter_tag = etree.SubElement(
                            tag, "allocatedFunctionalInterface", {'id': str(fun_inter.id)})
        self.write()

    # Method to write phy_inter's alias by list [phy_inter]
    def write_phy_interface_alias(self, phy_inter_alias_list):
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for phy_inter in phy_inter_alias_list:
                for phy_inter_tag in root.findall(".//physicalInterface[@id='" +
                                                  phy_inter.id + "']"):
                    phy_inter_tag.set('alias', str(phy_inter.alias))
        self.write()

    # Method to write derived by list [Object]
    def write_derived(self, derived_list):
        elem_tag = get_object_tag(derived_list[0])
        if elem_tag in derived_obj_tag:
            with open(self.file, 'rb') as file:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(file, parser)
                for elem in derived_list:
                    for fun_inter_tag in root.findall(".//" + elem_tag + "[@id='" +
                                                      elem.id + "']"):
                        fun_inter_tag.set('derived', str(elem.derived.id))
            self.write()

    def write_object_type(self, object_list):
        elem_tag = get_object_tag(object_list[0])
        if elem_tag:
            with open(self.file, 'rb') as file:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(file, parser)
                for obj in object_list:
                    for object_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                        object_tag.set('type', obj.type)
            self.write()


derived_obj_tag = ("physicalInterface",
                   "physicalElement",
                   "function",
                   "functionalElement",
                   "functionalInterface")


def get_object_tag(wanted_object):
    elem_tag = None
    if isinstance(wanted_object, datamodel.PhysicalInterface):
        elem_tag = "physicalInterface"
    elif isinstance(wanted_object, datamodel.PhysicalElement):
        elem_tag = "physicalElement"
    elif isinstance(wanted_object, datamodel.Function):
        elem_tag = "function"
    elif isinstance(wanted_object, datamodel.FunctionalElement):
        elem_tag = "functionalElement"
    elif isinstance(wanted_object, datamodel.FunctionalInterface):
        elem_tag = "functionalInterface"
    elif isinstance(wanted_object, datamodel.Attribute):
        elem_tag = "attribute"
    elif isinstance(wanted_object, datamodel.Transition):
        elem_tag = "transition"
    elif isinstance(wanted_object, datamodel.State):
        elem_tag = "state"
    elif isinstance(wanted_object, datamodel.Data):
        elem_tag = "data"
    return elem_tag
