#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
from lxml import etree


# Class to generate XML
class GenerateXML:
    def __init__(self, xml_file):
        # Initialize XML structure/tags
        root = etree.Element("funcArch")
        etree.SubElement(root, "functionList")
        etree.SubElement(root, "dataList")
        etree.SubElement(root, "stateList")
        etree.SubElement(root, "transitionList")
        etree.SubElement(root, "functionalElementList")
        etree.SubElement(root, "chainList")
        etree.SubElement(root, "attributeList")
        self.tree = etree.ElementTree(root)

        if len(xml_file) > 0:
            self.file = xml_file
        else:
            self.file = "Output.xml"

    # Method to write functions from function's list
    def write_function(self, function_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each flow/data
            for function_list_tag in root.findall("./functionList"):
                # Loop on function's list
                for function in function_list:
                    function_list_tag.text = "\n\t\t"
                    function_tag = etree.SubElement(function_list_tag, "function",
                                                    {'id': function.id, 'name': function.name,
                                                     'type': str(function.type), 'alias': function.alias})
                    function_tag.text = "\n\t\t\t"
                    function_tag.tail = "\n\t\t"
                    functional_part_list_tag = etree.SubElement(function_tag, "functionalPartList")
                    functional_part_list_tag.tail = "\n\t\t"
        self.write()

    # Method to write function's type by list [function, type]
    def write_function_type(self, function_type_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on [function, type] list
            for function in function_type_list:
                for function_tag in root.findall(".//function[@id='" + function[0].id + "']"):
                    function_tag.set('type', function[1])
        self.write()

    # Method to write function's alias by list [function, alias]
    def write_function_alias(self, function_alias_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on [function, type] list
            for function in function_alias_list:
                for function_tag in root.findall(".//function[@id='" + function[0].id + "']"):
                    function_tag.set('alias', function[1])
        self.write()

    # Method to write child by list [parent, child]
    def write_function_child(self, child_function_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each flow/data
            for function in root.findall(".//function"):
                for parent, child in child_function_list:
                    if function.get('id') == parent.id:
                        tag = function.find('functionalPartList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        functional_part_tag = etree.SubElement(tag, "functionalPart",
                                                               {'id': child.id})
                        functional_part_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to add data flows
    def write_data(self, data_list):
        with open(self.file, 'rb') as file:
            # Loop on data list
            root = self.tree.parse(file)
            for data_list_tag in root.findall('dataList'):
                for data in data_list:
                    existing_data_tag = data_list_tag.find('./dataList/data')
                    if existing_data_tag is not None:
                        tag = existing_data_tag
                    else:
                        tag = data_list_tag
                    tag.text = "\n\t" # Go to next line and indent 2 tab
                    data_tag = etree.SubElement(tag, "data", {'name': data.name, 'type': str(data.type), 'id': data.id})
                    data_tag.text = "\n\t\t"
                    data_tag.tail = "\n\t"
                    consumer_list_tag = etree.SubElement(data_tag, "consumerList")
                    consumer_list_tag.tail = "\n\t\t"
                    producer_list_tag = etree.SubElement(data_tag, "producerList")
                    producer_list_tag.tail = "\n\t\t"
                    predecessor_list_tag = etree.SubElement(data_tag, "predecessorList")
                    predecessor_list_tag.tail = "\n\t"
        self.write()

    # Method to write data's type by list [data, type]
    def write_data_type(self, data_type_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on [function, type] list
            for data in data_type_list:
                for data_tag in root.findall(".//data[@name='" + data[0].name + "']"):
                    data_tag.set('type', data[1])
        self.write()

    # Method to write consumers by list [data_name, function]
    def write_consumer(self, consumer_list):
        with open(self.file, 'rb') as file:
            # Loop on data list
            root = self.tree.parse(file)
            for i in consumer_list:
                for consumer_list_tag in root.findall("./dataList/data[@name='" + str(i[0]) + "']/consumerList"):
                    consumer_list_tag.text = "\n\t\t\t"
                    if not i[1].operand:
                        consumer_tag = etree.SubElement(consumer_list_tag, "consumer",
                                                        {'id': i[1].id, 'role': "none"})
                    else:
                        consumer_tag = etree.SubElement(consumer_list_tag, "consumer",
                                                        {'id': i[1].id, 'role': i[1].operand})
                    consumer_tag.tail = "\n\t\t"

        self.write()

    # Method to write producers by list [data_name, function]
    def write_producer(self, producer_list):
        with open(self.file, 'rb') as file:
            # Loop on data list
            root = self.tree.parse(file)
            for i in producer_list:
                for producer_list_tag in root.findall("./dataList/data[@name='" + str(i[0]) + "']/producerList"):
                    producer_list_tag.text = "\n\t\t\t"
                    producer_tag = etree.SubElement(producer_list_tag, "producer", {'id': i[1].id})
                    producer_tag.tail = "\n\t\t"
        self.write()

    # Method to write predecessors by list [data, predecessor]
    def write_predecessor(self, predecessor_list):
        with open(self.file, 'rb') as file:
            # Loop on data list
            root = self.tree.parse(file)
            for i in predecessor_list:
                for predecessor_list_tag in root.findall(
                        "./dataList/data[@name='" + str(i[0].name) + "']/predecessorList"):
                    predecessor_list_tag.text = "\n\t\t\t"
                    producer_tag = etree.SubElement(predecessor_list_tag, "predecessor", {'id': i[1].id})
                    producer_tag.tail = "\n\t\t"
        self.write()

    # Method to remove function by list [function]
    def delete_function(self, delete_function_list):
        with open(self.file, 'rb') as file:
            # Loop on data list
            root = self.tree.parse(file)
            for function in delete_function_list:
                for function_tag in root.findall(".//function[@id='" + function.id + "']"):
                    function_tag.getparent().remove(function_tag)
        self.write()

    # Method to remove data by list [data]
    def delete_data(self, delete_data_list):
        with open(self.file, 'rb') as file:
            # Loop on data list
            root = self.tree.parse(file)
            for data in delete_data_list:
                for data_tag in root.findall(".//data[@name='" + data.name + "']"):
                    data_tag.getparent().remove(data_tag)
        self.write()

    # Method to delete the parents (consumer or producer) when flow is within a component
    def delete_single_consumer_producer(self, data, function, value):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Find specific consumer/producer to delete
            for tag in root.findall(
                    ".//data[@name='" + data + "']/" + value + "List/" + value + "[@id='" + function.id + "']"):
                tag.getparent().remove(tag)
        self.write()

    # Method to write within XML file
    def write(self):
        with open(self.file, "wb") as file:
            self.tree.write(file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    # Method to write states from state's list
    def write_state(self, state_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for state_list_tag in root.findall("./stateList"):
                for state in state_list:
                    state_list_tag.text = "\n\t\t"
                    state_tag = etree.SubElement(state_list_tag, "state",
                                                    {'id': state.id, 'name': state.name,
                                                     'type': str(state.type), 'alias': state.alias})
                    state_tag.text = "\n\t\t\t"
                    state_tag.tail = "\n\t\t"
                    state_part_list_tag = etree.SubElement(state_tag, "statePartList")
                    state_part_list_tag.tail = "\n\t\t\t"
                    allocated_function_list_tag = etree.SubElement(state_tag,
                                                                   "allocatedFunctionList")
                    allocated_function_list_tag.tail = "\n\t\t"
        self.write()

    # Method to write state's type by list [state, type]
    def write_state_type(self, state_type_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for state in state_type_list:
                for state_tag in root.findall(".//state[@id='" + state[0].id + "']"):
                    state_tag.set('type', state[1])
        self.write()

    # Method to write state's alias by list [function, alias]
    def write_state_alias(self, state_alias_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for state in state_alias_list:
                for state_tag in root.findall(".//state[@id='" + state[0].id + "']"):
                    state_tag.set('alias', state[1])
        self.write()

    # Method to write child's state by list [parent, child]
    def write_state_child(self, child_state_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each state
            for state in root.findall(".//state"):
                for parent, child in child_state_list:
                    if state.get('id') == parent.id:
                        tag = state.find('statePartList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        state_part_tag = etree.SubElement(tag, "statePart",
                                                               {'id': child.id})
                        state_part_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to write allocated function by list [state, allocated_function]
    def write_allocated_function_to_state(self, state_function_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each flow/data
            for xml_state in root.findall(".//state"):
                for fun_elem, function in state_function_list:
                    if xml_state.get('id') == fun_elem.id:
                        tag = xml_state.find('allocatedFunctionList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        allocated_state_tag = etree.SubElement(tag, "allocatedFunction",
                                                               {'id': function.id})
                        allocated_state_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to delete state by list [state]
    def delete_state(self, delete_state_list):
        with open(self.file, 'rb') as file:
            # Loop on state list
            root = self.tree.parse(file)
            for state in delete_state_list:
                for state_tag in root.findall(".//state[@id='" + state.id + "']"):
                    state_tag.getparent().remove(state_tag)
        self.write()

    # Method to write transition from transition's list
    def write_transition(self, transition_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for transition_list_tag in root.findall("./transitionList"):
                for transition in transition_list:
                    transition_list_tag.text = "\n\t\t"
                    transition_tag = etree.SubElement(transition_list_tag, "transition",
                                                      {'id': transition.id, 'name': transition.name,
                                                       'type': str(transition.type), 'alias': transition.alias,
                                                       'source': str(transition.source),
                                                       'destination': str(transition.destination)})
                    transition_tag.text = "\n\t\t\t"
                    transition_tag.tail = "\n\t\t"
                    transition_part_list_tag = etree.SubElement(transition_tag, "conditionList")
                    transition_part_list_tag.tail = "\n\t\t"
        self.write()

    # Method to write transition's type by list [transition, type]
    def write_transition_type(self, transition_type_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for transition in transition_type_list:
                for transition_tag in root.findall(".//transition[@id='" + transition[0].id + "']"):
                    transition_tag.set('type', transition[1])
        self.write()

    # Method to write transition's alias by list [transition, alias]
    def write_transition_alias(self, transition_alias_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for transition in transition_alias_list:
                for transition_tag in root.findall(".//transition[@id='" + transition[0].id + "']"):
                    transition_tag.set('alias', transition[1])
        self.write()

    # Method to write transition's condition by list [transition, condition]
    def write_transition_condition(self, transition_condition_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for transition in root.findall(".//transition"):
                for tra, condition in transition_condition_list:
                    if transition.get('id') == tra.id:
                        tag = transition.find('conditionList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        state_part_tag = etree.SubElement(tag, "condition",
                                                          {'text': str(condition)})
                        state_part_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to write transition's source by list [transition, source]
    def write_source(self, transition_source_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for transition_src in transition_source_list:
                for state_tag in root.findall(".//transition[@id='" + transition_src[0].id + "']"):
                    state_tag.set('source', transition_src[1].id)
        self.write()

    # Method to write transition's destination by list [transition, destination]
    def write_destination(self, transition_destination_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for transition_dest in transition_destination_list:
                for state_tag in root.findall(".//transition[@id='" + transition_dest[0].id + "']"):
                    state_tag.set('destination', transition_dest[1].id)
        self.write()

    # Method to delete transition by list [transition]
    def delete_transition(self, delete_transition_list):
        with open(self.file, 'rb') as file:
            # Loop on state list
            root = self.tree.parse(file)
            for transition in delete_transition_list:
                for transition_tag in root.findall(".//transition[@id='" + transition.id + "']"):
                    transition_tag.getparent().remove(transition_tag)
        self.write()

    # Method to write functional element from functional elements list
    def write_functional_element(self, functional_element_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for functional_element_list_tag in root.findall("./functionalElementList"):
                for functional_element in functional_element_list:
                    functional_element_list_tag.text = "\n\t\t"
                    functional_element_tag = etree.SubElement(functional_element_list_tag,
                                                              "functionalElement", {
                                                                  'id': functional_element.id,
                                                                  'name': functional_element.name,
                                                                  'type': str(
                                                                      functional_element.type),
                                                                  'alias': functional_element.alias})
                    functional_element_tag.text = "\n\t\t\t"
                    functional_element_tag.tail = "\n\t\t"
                    fun_elem_part_list_tag = etree.SubElement(functional_element_tag,
                                                              "functionalElementPartList")
                    fun_elem_part_list_tag.tail = "\n\t\t\t"
                    allocated_state_list_tag = etree.SubElement(functional_element_tag,
                                                                "allocatedStateList")
                    allocated_state_list_tag.tail = "\n\t\t\t"
                    allocated_function_list_tag = etree.SubElement(functional_element_tag,
                                                                   "allocatedFunctionList")
                    allocated_function_list_tag.tail = "\n\t\t"

        self.write()

    # Method to write child by list [parent, child]
    def write_functional_element_child(self, fun_elem_child_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each flow/data
            for functional_element in root.findall(".//functionalElement"):
                for parent, child in fun_elem_child_list:
                    if functional_element.get('id') == parent.id:
                        tag = functional_element.find('functionalElementPartList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        functional_element_part_tag = etree.SubElement(tag, "functionalElementPart", {'id': child.id})
                        functional_element_part_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to write allocated state by list [fun_elem, allocated_state]
    def write_allocated_state(self, fun_elem_state_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each flow/data
            for functional_element in root.findall(".//functionalElement"):
                for fun_elem, state in fun_elem_state_list:
                    if functional_element.get('id') == fun_elem.id:
                        tag = functional_element.find('allocatedStateList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        allocated_state_tag = etree.SubElement(tag, "allocatedState",
                                                               {'id': state.id})
                        allocated_state_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to write allocated function by list [fun_elem, allocated_function]
    def write_allocated_function(self, fun_elem_function_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each flow/data
            for functional_element in root.findall(".//functionalElement"):
                for fun_elem, function in fun_elem_function_list:
                    if functional_element.get('id') == fun_elem.id:
                        tag = functional_element.find('allocatedFunctionList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        allocated_state_tag = etree.SubElement(tag, "allocatedFunction",
                                                               {'id': function.id})
                        allocated_state_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to delete functional element by list [functional element]
    def delete_functional_element(self, delete_fun_elem_list):
        with open(self.file, 'rb') as file:
            # Loop on state list
            root = self.tree.parse(file)
            for fun_elem in delete_fun_elem_list:
                for fun_elem_tag in root.findall(".//functionalElement[@id='" + fun_elem.id + "']"):
                    fun_elem_tag.getparent().remove(fun_elem_tag)
        self.write()

    # Method to write fun_elem's type by list [fun_elem, type]
    def write_fun_elem_type(self, fun_elem_type_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for fun_elem in fun_elem_type_list:
                for fun_elem_tag in root.findall(".//functionalElement[@id='" + fun_elem[0].id + "']"):
                    fun_elem_tag.set('type', fun_elem[1])
        self.write()

    # Method to write fun_elem's alias by list [fun_elem, alias]
    def write_fun_elem_alias(self, fun_elem_alias_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for fun_elem in fun_elem_alias_list:
                for fun_elem_tag in root.findall(".//functionalElement[@id='" + fun_elem[0].id + "']"):
                    fun_elem_tag.set('alias', fun_elem[1])
        self.write()

    # Method to write chains from chain's list
    def write_chain(self, chain_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for chain_list_tag in root.findall("./chainList"):
                for chain in chain_list:
                    chain_list_tag.text = "\n\t\t"
                    chain_tag = etree.SubElement(chain_list_tag, "chain",
                                                 {'id': chain.id, 'name': chain.name,
                                                  'type': str(chain.type)})
                    chain_tag.text = "\n\t\t\t"
                    chain_tag.tail = "\n\t\t"
                    allocated_item_list_tag = etree.SubElement(chain_tag,
                                                               "allocatedItemList")
                    allocated_item_list_tag.tail = "\n\t\t"
        self.write()

    # Method to write allocated item by list [chain, allocated_item]
    def write_allocated_chain_item(self, chain_item_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each flow/data
            for chain_element in root.findall(".//chain"):
                for chain, item in chain_item_list:
                    if chain_element.get('id') == chain.id:
                        tag = chain_element.find('allocatedItemList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        allocated_item_tag = etree.SubElement(tag, "allocatedItem",
                                                              {'id': item.id})
                        allocated_item_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to write attributes from attribute's list
    def write_attribute(self, attribute_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for attribute_list_tag in root.findall("./attributeList"):
                for attribute in attribute_list:
                    attribute_list_tag.text = "\n\t\t"
                    attribute_tag = etree.SubElement(attribute_list_tag, "attribute",
                                                     {'id': attribute.id, 'name': attribute.name,
                                                      'type': str(attribute.type),
                                                      'alias': attribute.alias})
                    attribute_tag.text = "\n\t\t\t"
                    attribute_tag.tail = "\n\t\t"
                    described_item_list_tag = etree.SubElement(attribute_tag,
                                                               "describedItemList")
                    described_item_list_tag.tail = "\n\t\t"
        self.write()

    # Method to write described item by list [attribute, (described_item, value)]
    def write_described_attribute_item(self, attribute_item_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            # Loop on each attribute
            for attribute_element in root.findall(".//attribute"):
                for attribute, item in attribute_item_list:
                    if attribute_element.get('id') == attribute.id:
                        tag = attribute_element.find('describedItemList')
                        tag.text = "\n\t\t\t\t"  # Go to next line and indent 4 tab
                        allocated_item_tag = etree.SubElement(tag, "describedItem",
                                                              {'id': item[0].id, 'value': item[1]})
                        allocated_item_tag.tail = "\n\t\t\t"  # Go to next line, indent 3 tab
        self.write()

    # Method to write attribute's type by list [Attribute, type_str]
    def write_attribute_type(self, attribute_type_list):
        with open(self.file, 'rb') as file:
            root = self.tree.parse(file)
            for attribute in attribute_type_list:
                for attribute_tag in root.findall(".//attribute[@id='" + attribute[0].id
                                                  + "']"):
                    attribute_tag.set('type', attribute[1])
        self.write()
