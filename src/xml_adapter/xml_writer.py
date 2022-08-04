#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module containing class methods to write within xml"""
# Libraries
from lxml import etree

import datamodel


class GenerateXML:
    """Class to generate XML"""
    def __init__(self, xml_file):
        """Initialize XML structure/tags and file's object"""
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
        viewpoint_tags = ['viewList', 'attributeList', 'typeList']
        for tag in viewpoint_tags:
            etree.SubElement(viewpoint, tag)
        self.tree = etree.ElementTree(self.root)

        if len(xml_file) > 0:
            self.file = xml_file
        else:
            self.file = "Output.xml"

    def write_function(self, function_list):
        """Method to write functions from function's list"""
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

                    _functional_part_list_tag = etree.SubElement(function_tag, "functionPartList")

        self.write()

    def write_data(self, data_list):
        """Method to add data flows"""
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

    def write_consumer(self, consumer_list):
        """Method to write consumers by list [data_name, function]"""
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

    def write_producer(self, producer_list):
        """Method to write producers by list [data_name, function]"""
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for i in producer_list:
                for producer_list_tag in root.findall(".//dataList/data[@name='" + str(i[0])
                                                      + "']/producerList"):

                    _producer_tag = etree.SubElement(producer_list_tag, "producer", {'id': i[1].id})

        self.write()

    def write_predecessor(self, predecessor_list):
        """Method to write predecessors by list [data, predecessor]"""
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for i in predecessor_list:
                for predecessor_list_tag in root.findall(
                        ".//dataList/data[@name='" + str(i[0].name) + "']/predecessorList"):

                    _producer_tag = etree.SubElement(predecessor_list_tag, "predecessor",
                                                     {'id': i[1].id})

        self.write()

    def delete_single_consumer_producer(self, data, function, value):
        """Method to delete the parents (consumer or producer) when flow is within a component"""
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            # Find specific consumer/producer to delete
            for tag in root.findall(
                    ".//data[@name='" + data + "']/" + value + "List/" + value + "[@id='"
                    + function.id + "']"):
                tag.getparent().remove(tag)
        self.write()

    def write(self):
        """Method to write within XML file"""
        with open(self.file, "wb") as file:
            self.tree.write(file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_state(self, state_list):
        """Method to write states from state's list"""
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

    def write_transition(self, transition_list):
        """Method to write transition from transition's list"""
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

    def write_transition_condition(self, transition_condition_list):
        """Method to write transition's condition by list [transition, condition]"""
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

    def write_source(self, transition_source_list):
        """Method to write transition's source by list [transition, source]"""
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for transition_src in transition_source_list:
                for state_tag in root.findall(".//transition[@id='" + transition_src[0].id + "']"):
                    state_tag.set('source', transition_src[1].id)
        self.write()

    def write_destination(self, transition_destination_list):
        """Method to write transition's destination by list [transition, destination]"""
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            for transition_dest in transition_destination_list:
                for state_tag in root.findall(".//transition[@id='" + transition_dest[0].id + "']"):
                    state_tag.set('destination', transition_dest[1].id)
        self.write()

    def write_functional_element(self, functional_element_list):
        """Method to write functional element from functional elements list"""
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

    def write_exposed_interface(self, fun_elem_inter_list):
        """Method to write exposed interfaces by list [fun_elem/phy_elem, exposed_interface]"""
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

    def write_view(self, view_list):
        """Method to write views from view's list"""
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//viewList') is None:
                etree.SubElement(root, 'viewList')
            for view_list_tag in root.findall(".//viewList"):
                for view in view_list:
                    view_tag = etree.SubElement(view_list_tag, "view",
                                                 {'id': view.id, 'name': view.name,
                                                  'type': str(view.type)})
                    _allocated_item_list_tag = etree.SubElement(view_tag, "allocatedItemList")
        self.write()

    def write_attribute(self, attribute_list):
        """Method to write attributes from attribute's list"""
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

    def write_described_attribute_item(self, attribute_item_list):
        """Method to write described item by list [attribute, (described_item, value)]"""
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

    def write_functional_interface(self, functional_interface_list):
        """Method to write functional interfaces from interface's list"""
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

    def write_physical_element(self, physical_element_list):
        """Method to write physical element from physical elements list"""
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

    def write_physical_interface(self, physical_interface_list):
        """Method to write physical interfaces from interface's list"""
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

    def write_object_alias(self, object_list):
        """Method to write object's alias by list [object]"""
        elem_tag = get_object_tag(object_list[0])
        if elem_tag:
            with open(self.file, 'rb') as file:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(file, parser)
                for obj in object_list:
                    for obj_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                        obj_tag.set('alias', str(obj.alias))
            self.write()

    def write_derived(self, derived_list):
        """Method to write derived by list [Object]"""
        for obj in derived_list:
            elem_tag = get_object_tag(obj)
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
        """Method to write object's type by list [object]"""
        elem_tag = get_object_tag(object_list[0])
        if elem_tag:
            with open(self.file, 'rb') as file:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(file, parser)
                for obj in object_list:
                    for object_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                        object_tag.set('type', obj.type)
            self.write()

    def write_object_child(self, object_child_list):
        """Method to write child by list [parent, child]"""
        elem_tag = get_object_tag(object_child_list[0][0])
        if elem_tag:
            with open(self.file, 'rb') as file:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(file, parser)
                for obj in root.findall(".//" + elem_tag):
                    for parent, child in object_child_list:
                        if obj.get('id') == parent.id:
                            tag = obj.find(elem_tag + 'PartList')
                            _obj_element_part_tag = etree.SubElement(tag,
                                                                     elem_tag + 'Part',
                                                                     {'id': child.id})
            self.write()

    def delete_object(self, object_list):
        """Method to delete objects by list [object]"""
        elem_tag = get_object_tag(object_list[0])
        if elem_tag:
            with open(self.file, 'rb') as file:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(file, parser)
                for obj in object_list:
                    for obj_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                        obj_tag.getparent().remove(obj_tag)
            self.write()

    def write_objects_allocation(self, objects_list):
        """Method to write allocated objects from list [Object, Object]"""
        elem_tag = get_object_tag(objects_list[0][0])
        if elem_tag:
            with open(self.file, 'rb') as file:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(file, parser)
                for obj_tag in root.findall(".//" + elem_tag):
                    for obj, obj_to_alloc in objects_list:
                        if obj_tag.get('id') == obj.id:
                            if elem_tag == "view":
                                alloc_tag = get_allocation_tag(obj)
                            else:
                                alloc_tag = get_allocation_tag(obj_to_alloc)
                            tag = obj_tag.find(alloc_tag + 'List')
                            _allocated_obj_tag = etree.SubElement(
                                tag, alloc_tag, {'id': str(obj_to_alloc.id)})
            self.write()

    def write_type_element(self, type_list):
        """Method to write type element from type's list"""
        with open(self.file, 'rb') as file:
            parser = etree.XMLParser(remove_blank_text=True)
            root = self.tree.parse(file, parser)
            if root.find('.//typeList') is None:
                etree.SubElement(root.find('./viewPoint'), 'typeList')
            for type_list_tag in root.findall(".//typeList"):
                for type_elem in type_list:
                    if isinstance(type_elem.base, datamodel.Type):
                        base_type = type_elem.base.name
                    else:
                        base_type = type_elem.base
                    elem_tag = etree.SubElement(type_list_tag, "type",
                                                {'id': type_elem.id, 'name': type_elem.name,
                                                 'alias': type_elem.alias,
                                                 'base': str(base_type)})

                    # _described_item_list_tag = etree.SubElement(elem_tag, "describedItemList")

        self.write()


derived_obj_tag = ("physicalInterface",
                   "physicalElement",
                   "function",
                   "functionalElement",
                   "functionalInterface")


def get_object_tag(wanted_object):
    """Get xml element tag corresponding to wanted_object"""
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
    elif isinstance(wanted_object, datamodel.View):
        elem_tag = "view"
    elif isinstance(wanted_object, datamodel.Type):
        elem_tag = "type"
    return elem_tag


def get_allocation_tag(wanted_object):
    """Get xml allocation tag corresponding to wanted_object"""
    elem_tag = None
    if isinstance(wanted_object, datamodel.Function):
        elem_tag = "allocatedFunction"
    elif isinstance(wanted_object, datamodel.FunctionalElement):
        elem_tag = "allocatedFunctionalElement"
    elif isinstance(wanted_object, datamodel.FunctionalInterface):
        elem_tag = "allocatedFunctionalInterface"
    elif isinstance(wanted_object, datamodel.State):
        elem_tag = "allocatedState"
    elif isinstance(wanted_object, datamodel.Data):
        elem_tag = "allocatedData"
    elif isinstance(wanted_object, datamodel.View):
        elem_tag = "allocatedItem"
    return elem_tag
