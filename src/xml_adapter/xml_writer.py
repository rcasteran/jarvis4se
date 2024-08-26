"""@defgroup xml_adapter
Module for 3SE xml parsing and writing
"""
# Libraries
from lxml import etree
import os

# Modules
import datamodel
from . import util
from tools import Logger


class XmlWriter3SE:
    """@ingroup xml_adapter
    @anchor XmlWriter3SE
    3SE XML writer
    """

    def __init__(self, xml_file):
        """@var root
        Reference to the XML root object

        @var tree
        Reference to the XML elements tree

        @var file
        Reference to the XML file to be written
        """

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
        viewpoint_tags = ['viewList', 'attributeList', 'requirementList', 'typeList']
        for tag in viewpoint_tags:
            etree.SubElement(viewpoint, tag)

        self.tree = etree.ElementTree(self.root)

        if len(xml_file) > 0:
            self.file = xml_file
        else:
            self.file = "Output.xml"

    @staticmethod
    def check_object_type(obj):
        """Check object type against 3SE base types
        @param[in] obj : object reference
        @return object type to be written in XML file
        """
        if isinstance(obj, datamodel.BaseType):
            # Object is a basic 3SE type
            type_str = str(obj)
        else:
            type_str = obj.id

        return type_str

    def write_function(self, function_list):
        """Write functions from list of functions
        @param[in] function_list : list of functions
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//functionList') is None:
            etree.SubElement(root, 'functionList')

        for function_list_tag in root.findall(".//functionList"):
            for function in function_list:
                if function.derived is not None:
                    derived_elem_id = function.derived.id
                else:
                    derived_elem_id = ''
                
                function_tag = etree.SubElement(function_list_tag, "function",
                                                {'id': function.id,
                                                 'name': util.normalize_xml_string(function.name),
                                                 'type': self.check_object_type(function.type),
                                                 'alias': function.alias,
                                                 'derived': derived_elem_id})

                functional_part_list_tag = etree.SubElement(function_tag, "functionPartList")
                for child in function.child_list:
                    _obj_element_part_tag = etree.SubElement(functional_part_list_tag,
                                                             'functionPart',
                                                             {'id': child.id})

                allocated_req_list_tag = etree.SubElement(function_tag, "allocatedRequirementList")
                for allocated_req in function.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': str(allocated_req.id)})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_data(self, data_list):
        """Write data from list of data
        @param[in] data_list : list of data
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//dataList') is None:
            etree.SubElement(root, 'dataList')

        for data_list_tag in root.findall('.//dataList'):
            for data in data_list:
                data_tag = etree.SubElement(data_list_tag, "data",
                                            {'name': util.normalize_xml_string(data.name),
                                             'type': self.check_object_type(data.type),
                                             'id': data.id})

                # Consumer list is handled in a separate dictionary
                _consumer_list_tag = etree.SubElement(data_tag, "consumerList")

                # Producer list is handled in a separate dictionary
                _producer_list_tag = etree.SubElement(data_tag, "producerList")

                predecessor_list_tag = etree.SubElement(data_tag, "predecessorList")
                for predecessor in data.predecessor_list:
                    _predecessor_tag = etree.SubElement(predecessor_list_tag,
                                                        "predecessor",
                                                        {'id': predecessor.id})

                allocated_req_list_tag = etree.SubElement(data_tag, "allocatedRequirementList")
                for allocated_req_id in data.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': str(allocated_req_id)})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_data_consumer(self, consumer_list):
        """Write consumers by list [data, function]
        @param[in] consumer_list : list of consumers
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for consumer in consumer_list:
            for xml_element in root.findall(".//dataList/data[@name='" + util.normalize_xml_string(consumer[0].name)
                                            + "']"):
                if xml_element.find('consumerList') is None:
                    etree.SubElement(xml_element, 'consumerList')
                    if xml_element.find('producerList') is None:
                        etree.SubElement(xml_element, 'producerList')

            for consumer_list_tag in root.findall(".//dataList/data[@name='"
                                                  + util.normalize_xml_string(consumer[0].name)
                                                  + "']/consumerList"):
                if not consumer[1].operand:
                    _consumer_tag = etree.SubElement(consumer_list_tag, "consumer",
                                                     {'id': consumer[1].id, 'role': "none"})
                else:
                    _consumer_tag = etree.SubElement(consumer_list_tag, "consumer",
                                                     {'id': consumer[1].id,
                                                      'role': util.normalize_xml_string(consumer[1].operand)})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_data_producer(self, producer_list):
        """Write producers by list [data, function]
        @param[in] producer_list : list of producers
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for producer in producer_list:
            for xml_element in root.findall(".//dataList/data[@name='" + util.normalize_xml_string(producer[0].name)
                                            + "']"):
                if xml_element.find('producerList') is None:
                    etree.SubElement(xml_element, 'producerList')
                    if xml_element.find('consumerList') is None:
                        etree.SubElement(xml_element, 'consumerList')

            for producer_list_tag in root.findall(".//dataList/data[@name='"
                                                  + util.normalize_xml_string(producer[0].name)
                                                  + "']/producerList"):
                _producer_tag = etree.SubElement(producer_list_tag, "producer", {'id': producer[1].id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_data_predecessor(self, predecessor_list):
        """Write predecessors by list [data, predecessor]
        @param[in] predecessor_list : list of predecessors
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for predecessor in predecessor_list:
            for xml_element in root.findall(".//dataList/data[@name='"
                                            + util.normalize_xml_string(predecessor[0].name)
                                            + "']"):
                if xml_element.find('predecessorList') is None:
                    etree.SubElement(xml_element, 'predecessorList')

            for predecessor_list_tag in root.findall(".//dataList/data[@name='"
                                                     + util.normalize_xml_string(predecessor[0].name)
                                                     + "']/predecessorList"):
                _predecessor_tag = etree.SubElement(predecessor_list_tag, "predecessor",
                                                    {'id': predecessor[1].id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_data_relationship(self, flow_function, relationship_type):
        """Write data relationship (either consumer or producer or predecessor)

        @param[in] object : [flow, function] to be deleted
        @param[in] relationship_type : "consumer" or "producer" or "predecessor"
        @return None
        """
        flow_function_list = [flow_function]

        if relationship_type == "consumer":
            self.write_data_consumer(flow_function_list)
        elif relationship_type == "producer":
            self.write_data_producer(flow_function_list)
        elif relationship_type == "predecessor":
            self.write_data_predecessor(flow_function_list)
        else:
            Logger.set_error(__name__, f"Unknown data relationship type: {relationship_type}")

    def delete_data_relationship(self, flow_function, relationship_type):
        """Delete data relationship (either consumer or producer or predecessor)

        @param[in] object : [flow, function] to be deleted
        @param[in] relationship_type : "consumer" or "producer" or "predecessor"
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for tag in root.findall(".//data[@name='"
                                + util.normalize_xml_string(flow_function[0].name)
                                + "']/"
                                + relationship_type
                                + "List/"
                                + relationship_type
                                + "[@id='"
                                + flow_function[1].id
                                + "']"):
            tag.getparent().remove(tag)

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write(self):
        """Write within the XML file
        @return None
        """
        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_state(self, state_list):
        """Write state from list of states
        @param[in] state_list : list of states
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//stateList') is None:
            etree.SubElement(root, 'stateList')

        for state_list_tag in root.findall(".//stateList"):
            for state in state_list:
                state_tag = etree.SubElement(state_list_tag, "state",
                                             {'id': state.id,
                                              'name': util.normalize_xml_string(state.name),
                                              'type': self.check_object_type(state.type),
                                              'alias': state.alias})

                state_part_list_tag = etree.SubElement(state_tag, "statePartList")
                for child in state.child_list:
                    _obj_element_part_tag = etree.SubElement(state_part_list_tag,
                                                             'statePart',
                                                             {'id': child.id})

                allocated_function_list_tag = etree.SubElement(state_tag, "allocatedFunctionList")
                for allocated_function_id in state.allocated_function_list:
                    _allocated_obj_tag = etree.SubElement(allocated_function_list_tag,
                                                          'allocatedFunction',
                                                          {'id': allocated_function_id})

                allocated_req_list_tag = etree.SubElement(state_tag, "allocatedRequirementList")
                for allocated_req_id in state.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': allocated_req_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_transition(self, transition_list):
        """Write transition from list of transitions
        @param[in] transition_list : list of transitions
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//transitionList') is None:
            etree.SubElement(root, 'transitionList')

        for transition_list_tag in root.findall(".//transitionList"):
            for transition in transition_list:
                transition_tag = etree.SubElement(transition_list_tag, "transition",
                                                  {'id': transition.id,
                                                   'name': util.normalize_xml_string(transition.name),
                                                   'type': self.check_object_type(transition.type),
                                                   'alias': transition.alias,
                                                   'source': util.normalize_xml_string(transition.source),
                                                   'destination': util.normalize_xml_string(transition.destination)})

                transition_part_list_tag = etree.SubElement(transition_tag, "conditionList")
                for condition in transition.condition_list:
                    _state_part_tag = etree.SubElement(transition_part_list_tag,
                                                       "condition",
                                                       {'text': util.normalize_xml_string(condition)})

                allocated_req_list_tag = etree.SubElement(transition_tag, "allocatedRequirementList")
                for allocated_req_id in transition.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': allocated_req_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_transition_condition(self, transition_condition_list):
        """Write transitions by list [transition, condition]
        @param[in] transition_condition_list : list of transitions
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for transition_tag in root.findall(".//transition"):
            for transition, condition in transition_condition_list:
                if transition_tag.get('id') == transition.id:
                    tag = transition_tag.find('conditionList')
                    _state_part_tag = etree.SubElement(tag, "condition",
                                                       {'text': util.normalize_xml_string(condition)})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_transition_source(self, transition_source_list):
        """Write transition source by list [transition, source]
        @param[in] transition_source_list : list of sources
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for transition_src in transition_source_list:
            for state_tag in root.findall(".//transition[@id='" + transition_src[0].id + "']"):
                state_tag.set('source', transition_src[1].id)

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_transition_destination(self, transition_destination_list):
        """Write transition destination by list [transition, destination]
        @param[in] transition_destination_list : list of destinations
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for transition_dest in transition_destination_list:
            for state_tag in root.findall(".//transition[@id='" + transition_dest[0].id + "']"):
                state_tag.set('destination', transition_dest[1].id)

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_functional_element(self, functional_element_list):
        """Write functional element from list of functional elements
        @param[in] functional_element_list : list of functional elements
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//functionalElementList') is None:
            etree.SubElement(root, 'functionalElementList')

        for functional_element_list_tag in root.findall(".//functionalElementList"):
            for functional_element in functional_element_list:
                if functional_element.derived is not None:
                    derived_elem_id = functional_element.derived.id
                else:
                    derived_elem_id = ''
                
                functional_element_tag = etree.SubElement(
                    functional_element_list_tag, "functionalElement",
                    {'id': functional_element.id,
                     'name': util.normalize_xml_string(functional_element.name),
                     'type': self.check_object_type(functional_element.type),
                     'alias': functional_element.alias,
                     'derived': derived_elem_id})

                fun_elem_part_list_tag = etree.SubElement(functional_element_tag, "functionalElementPartList")
                for child in functional_element.child_list:
                    _obj_element_part_tag = etree.SubElement(fun_elem_part_list_tag,
                                                             'functionalElementPart',
                                                             {'id': child.id})

                allocated_state_list_tag = etree.SubElement(functional_element_tag, "allocatedStateList")
                for allocated_state_id in functional_element.allocated_state_list:
                    _allocated_obj_tag = etree.SubElement(allocated_state_list_tag,
                                                          'allocatedState',
                                                          {'id': allocated_state_id})

                allocated_function_list_tag = etree.SubElement(functional_element_tag, "allocatedFunctionList")
                for allocated_function_id in functional_element.allocated_function_list:
                    _allocated_obj_tag = etree.SubElement(allocated_function_list_tag,
                                                          'allocatedFunction',
                                                          {'id': allocated_function_id})

                exposed_interface_list_tag = etree.SubElement(functional_element_tag, "exposedInterfaceList")
                for exposed_interface_id in functional_element.exposed_interface_list:
                    _exposed_interface_tag = etree.SubElement(exposed_interface_list_tag,
                                                              'exposedInterface',
                                                              {'id': exposed_interface_id})

                allocated_req_list_tag = etree.SubElement(functional_element_tag, "allocatedRequirementList")
                for allocated_req_id in functional_element.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': allocated_req_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_element_exposed_interface(self, element_interface_list):
        """Write interface by list [element, interface]
        @param[in] element_interface_list : list of interfaces
        @return None
        """
        for element, inter in element_interface_list:
            element_tag = self.get_object_tag(element)
            if element_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)

                for xml_element in root.findall(".//" + element_tag):
                    if xml_element.find('exposedInterfaceList') is None:
                        etree.SubElement(xml_element, 'exposedInterfaceList')

                    if xml_element.get('id') == element.id:
                        tag = xml_element.find('exposedInterfaceList')
                        _exposed_interface_tag = etree.SubElement(tag, "exposedInterface",
                                                                  {'id': inter.id})

                self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_view(self, view_list):
        """Write view from list of views
        @param[in] view_list : list of views
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//viewList') is None:
            etree.SubElement(root, 'viewList')

        for view_list_tag in root.findall(".//viewList"):
            for view in view_list:
                if isinstance(view.type, datamodel.BaseType):
                    type_str = str(view.type)
                else:
                    type_str = view.type.id

                view_tag = etree.SubElement(view_list_tag, "view",
                                            {'id': view.id,
                                             'name': util.normalize_xml_string(view.name),
                                             'type': type_str})

                allocated_item_list_tag = etree.SubElement(view_tag, "allocatedItemList")
                for allocated_item_id in view.allocated_item_list:
                    _allocated_item_tag = etree.SubElement(allocated_item_list_tag,
                                                           'allocatedItem',
                                                           {'id': allocated_item_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_attribute(self, attribute_list):
        """Write attribute from list of attributes
        @param[in] attribute_list : list of attributes
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//attributeList') is None:
            etree.SubElement(root, 'attributeList')

        for attribute_list_tag in root.findall(".//attributeList"):
            for attribute in attribute_list:
                attribute_tag = etree.SubElement(attribute_list_tag, "attribute",
                                                 {'id': attribute.id,
                                                  'name': util.normalize_xml_string(attribute.name),
                                                  'type': self.check_object_type(attribute.type),
                                                  'alias': attribute.alias})

                described_item_list_tag = etree.SubElement(attribute_tag, "describedItemList")
                for described_item in attribute.described_item_list:
                    _allocated_item_tag = etree.SubElement(described_item_list_tag,
                                                           "describedItem",
                                                           {'id': described_item[0],
                                                            'value': util.normalize_xml_string(described_item[1])})

                allocated_req_list_tag = etree.SubElement(attribute_tag, "allocatedRequirementList")
                for allocated_req_id in attribute.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': allocated_req_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_attribute_described_item(self, attribute_item_list):
        """Write attribute described item by list [attribute, (described_item, value)]
        @param[in] attribute_item_list : list of attribute described items
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for attribute_element in root.findall(".//attribute"):
            for attribute, item in attribute_item_list:
                if attribute_element.get('id') == attribute.id:
                    tag = attribute_element.find('describedItemList')
                    _allocated_item_tag = etree.SubElement(tag, "describedItem",
                                                           {'id': item[0].id,
                                                            'value': util.normalize_xml_string(item[1])})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_functional_interface(self, functional_interface_list):
        """Write functional interface from list of functional interfaces
        @param[in] functional_interface_list : list of functional interfaces
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//functionalInterfaceList') is None:
            etree.SubElement(root, 'functionalInterfaceList')

        for fun_interface_list_tag in root.findall(".//functionalInterfaceList"):
            for fun_interface in functional_interface_list:
                if fun_interface.derived is not None:
                    derived_elem_id = fun_interface.derived.id
                else:
                    derived_elem_id = ''
                
                fun_interface_tag = etree.SubElement(fun_interface_list_tag,
                                                     "functionalInterface",
                                                     {'id': fun_interface.id,
                                                      'name': util.normalize_xml_string(fun_interface.name),
                                                      'type': self.check_object_type(fun_interface.type),
                                                      'alias': fun_interface.alias,
                                                      'derived': derived_elem_id})

                allocated_data_list_tag = etree.SubElement(fun_interface_tag, "allocatedDataList")
                for allocated_data_id in fun_interface.allocated_data_list:
                    _allocated_obj_tag = etree.SubElement(allocated_data_list_tag,
                                                          'allocatedData',
                                                          {'id': allocated_data_id})

                allocated_req_list_tag = etree.SubElement(fun_interface_tag, "allocatedRequirementList")
                for allocated_req_id in fun_interface.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': allocated_req_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_physical_element(self, physical_element_list):
        """Write physical element from list of physical elements
        @param[in] physical_element_list : list of physical elements
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//physicalElementList') is None:
            etree.SubElement(root, 'physicalElementList')

        for physical_element_list_tag in root.findall(".//physicalElementList"):
            for physical_element in physical_element_list:
                if physical_element.derived is not None:
                    derived_elem_id = physical_element.derived.id
                else:
                    derived_elem_id = ''
                
                physical_element_tag = etree.SubElement(
                    physical_element_list_tag, "physicalElement",
                    {'id': physical_element.id,
                     'name': util.normalize_xml_string(physical_element.name),
                     'type': self.check_object_type(physical_element.type),
                     'alias': physical_element.alias,
                     'derived': derived_elem_id})

                phy_elem_part_list_tag = etree.SubElement(physical_element_tag, "physicalElementPartList")
                for child in physical_element.child_list:
                    _obj_element_part_tag = etree.SubElement(phy_elem_part_list_tag,
                                                             'physicalElementPart',
                                                             {'id': child.id})

                allocated_fun_elem_list_tag = etree.SubElement(physical_element_tag, "allocatedFunctionalElementList")
                for allocated_fun_elem_id in physical_element.allocated_fun_elem_list:
                    _allocated_obj_tag = etree.SubElement(allocated_fun_elem_list_tag,
                                                          'allocatedFunctionalElement',
                                                          {'id': allocated_fun_elem_id})

                exposed_interface_list_tag = etree.SubElement(physical_element_tag, "exposedInterfaceList")
                for exposed_interface_id in physical_element.exposed_interface_list:
                    _exposed_interface_tag = etree.SubElement(exposed_interface_list_tag,
                                                              'exposedInterface',
                                                              {'id': exposed_interface_id})

                allocated_req_list_tag = etree.SubElement(physical_element_tag, "allocatedRequirementList")
                for allocated_req_id in physical_element.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': allocated_req_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_physical_interface(self, physical_interface_list):
        """Write physical interface from list of physical interfaces
        @param[in] physical_interface_list : list of physical interfaces
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//physicalInterfaceList') is None:
            etree.SubElement(root, 'physicalInterfaceList')

        for phy_interface_list_tag in root.findall(".//physicalInterfaceList"):
            for phy_interface in physical_interface_list:
                if phy_interface.derived is not None:
                    derived_elem_id = phy_interface.derived.id
                else:
                    derived_elem_id = ''
                
                phy_interface_tag = etree.SubElement(phy_interface_list_tag,
                                                     "physicalInterface",
                                                     {'id': phy_interface.id,
                                                      'name': util.normalize_xml_string(phy_interface.name),
                                                      'type': self.check_object_type(phy_interface.type),
                                                      'alias': phy_interface.alias,
                                                      'derived': derived_elem_id})

                allocated_fun_inter_list_tag = etree.SubElement(phy_interface_tag, "allocatedFunctionalInterfaceList")
                for allocated_fun_inter_id in phy_interface.allocated_fun_inter_list:
                    _allocated_obj_tag = etree.SubElement(allocated_fun_inter_list_tag,
                                                          'allocatedFunctionalInterface',
                                                          {'id': allocated_fun_inter_id})

                allocated_req_list_tag = etree.SubElement(phy_interface_tag, "allocatedRequirementList")
                for allocated_req_id in phy_interface.allocated_req_list:
                    _allocated_obj_tag = etree.SubElement(allocated_req_list_tag,
                                                          'allocatedRequirement',
                                                          {'id': allocated_req_id})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    @staticmethod
    def get_object_tag(obj):
        """Get the XML element tag corresponding to an object
        @param[in] obj : object reference
        @return XML tag (when retrieved) or None
        """
        elem_tag = None
        if isinstance(obj, datamodel.Data):
            elem_tag = "data"
        elif isinstance(obj, datamodel.Function):
            elem_tag = "function"
        elif isinstance(obj, datamodel.FunctionalElement):
            elem_tag = "functionalElement"
        elif isinstance(obj, datamodel.FunctionalInterface):
            elem_tag = "functionalInterface"
        elif isinstance(obj, datamodel.PhysicalElement):
            elem_tag = "physicalElement"
        elif isinstance(obj, datamodel.PhysicalInterface):
            elem_tag = "physicalInterface"
        elif isinstance(obj, datamodel.State):
            elem_tag = "state"
        elif isinstance(obj, datamodel.Transition):
            elem_tag = "transition"
        elif isinstance(obj, datamodel.Attribute):
            elem_tag = "attribute"
        elif isinstance(obj, datamodel.Requirement):
            elem_tag = "requirement"
        elif isinstance(obj, datamodel.View):
            elem_tag = "view"
        elif isinstance(obj, datamodel.Type):
            # Object is an extension of the previous 3SE basic types
            elem_tag = "type"
        else:
            Logger.set_error(__name__, f"Unsupported type for object {obj.id}")
        return elem_tag

    def write_object_alias(self, object_list):
        """Write object alias by list [object]
        @param[in] object_list : list of objects
        @return None
        """
        for obj in object_list:
            elem_tag = self.get_object_tag(obj)
            if elem_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)

                for obj_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                    obj_tag.set('alias', str(obj.alias))

                self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_object_derived(self, object_list):
        """Write object derived reference by list [object]
        @param[in] object_list : list of objects
        @return None
        """
        for obj in object_list:
            elem_tag = self.get_object_tag(obj)
            if elem_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)

                for obj_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                    obj_tag.set('derived', str(obj.derived.id))

                self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_object_type(self, object_list):
        """Write object type by list [object]
        @param[in] object_list : list of objects
        @return None
        """
        for obj in object_list:
            elem_tag = self.get_object_tag(obj)
            if elem_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)

                for obj_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                    obj_tag.set('type', self.check_object_type(obj.type))

                self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_object_child(self, object_child_list):
        """Write object child by list [parent, child]
        @param[in] object_child_list : list of children
        @return None
        """
        for parent, child in object_child_list:
            elem_tag = self.get_object_tag(parent)
            if elem_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)
                for obj in root.findall(".//" + elem_tag):
                    if obj.get('id') == parent.id:
                        tag = obj.find(elem_tag + 'PartList')
                        _obj_element_part_tag = etree.SubElement(tag,
                                                                 elem_tag + 'Part',
                                                                 {'id': child.id})

                self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def delete_object(self, object_list):
        """Delete object type by list [object]
        @param[in] object_list : list of objects
        @return None
        """
        for obj in object_list:
            elem_tag = self.get_object_tag(obj)
            if elem_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)

                for obj_tag in root.findall(".//" + elem_tag + "[@id='" + obj.id + "']"):
                    obj_tag.getparent().remove(obj_tag)

                self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    @staticmethod
    def get_allocation_tag(obj):
        """Get the XML allocation tag corresponding to an object
        @param[in] obj : object reference
        @return XML tag (when retrieved) or None
        """
        elem_tag = None
        if isinstance(obj, datamodel.Function):
            elem_tag = "allocatedFunction"
        elif isinstance(obj, datamodel.FunctionalElement):
            elem_tag = "allocatedFunctionalElement"
        elif isinstance(obj, datamodel.FunctionalInterface):
            elem_tag = "allocatedFunctionalInterface"
        elif isinstance(obj, datamodel.State):
            elem_tag = "allocatedState"
        elif isinstance(obj, datamodel.Data):
            elem_tag = "allocatedData"
        elif isinstance(obj, datamodel.View):
            elem_tag = "allocatedItem"
        elif isinstance(obj, datamodel.Requirement):
            elem_tag = "allocatedRequirement"
        else:
            Logger.set_error(__name__, f"Unsupported type for object {obj.id} allocation")

        return elem_tag

    def write_object_allocation(self, object_allocated_object_list):
        """Write allocated objects from list [Object, Allocated object]
        @param[in] object_allocated_object_list : list of allocated objects
        @return None
        """
        for obj, allocated_obj in object_allocated_object_list:
            elem_tag = self.get_object_tag(obj)
            if elem_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)

                for obj_tag in root.findall(".//" + elem_tag):
                    if obj_tag.get('id') == obj.id:
                        if elem_tag == "view":
                            allocated_tag = self.get_allocation_tag(obj)
                        else:
                            allocated_tag = self.get_allocation_tag(allocated_obj)

                        tag = obj_tag.find(allocated_tag + 'List')
                        if tag is None:
                            tag = etree.SubElement(obj_tag, allocated_tag + 'List')

                        _allocated_obj_tag = etree.SubElement(tag, allocated_tag, {'id': allocated_obj.id})

            self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def delete_object_allocation(self, object_allocated_object_list):
        """Delete allocated objects from list [Object, Allocated object]
        @param[in] object_allocated_object_list : list of allocated objects
        @return None
        """
        for obj, allocated_obj in object_allocated_object_list:
            elem_tag = self.get_object_tag(obj)
            if elem_tag:
                parser = etree.XMLParser(remove_blank_text=True)
                root = self.tree.parse(self.file, parser)

                for obj_tag in root.findall(".//" + elem_tag):
                    if obj_tag.get('id') == obj.id:
                        if elem_tag == "view":
                            allocated_tag = self.get_allocation_tag(obj)
                        else:
                            allocated_tag = self.get_allocation_tag(allocated_obj)

                        tag = obj_tag.find(allocated_tag + 'List')

                        for allocated_obj_tag in tag.findall(allocated_tag + "[@id='" + allocated_obj.id + "']"):
                            tag.remove(allocated_obj_tag)

            self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_type_element(self, type_list):
        """Write type element from list of types
        @param[in] type_list : list of types
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//typeList') is None:
            etree.SubElement(root.find('./viewPoint'), 'typeList')

        for type_list_tag in root.findall(".//typeList"):
            for type_elem in type_list:
                _elem_tag = etree.SubElement(type_list_tag, "type",
                                             {'id': type_elem.id,
                                              'name': util.normalize_xml_string(type_elem.name),
                                              'alias': type_elem.alias,
                                              'base': self.check_object_type(type_elem.base)})

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_requirement(self, requirement_list):
        """Write attribute from list of attributes
        @param[in] attribute_list : list of attributes
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        if root.find('.//requirementList') is None:
            etree.SubElement(root, 'requirementList')

        for requirement_list_tag in root.findall(".//requirementList"):
            for requirement in requirement_list:
                requirement_tag = etree.SubElement(requirement_list_tag, "requirement",
                                                 {'id': requirement.id,
                                                  'name': util.normalize_xml_string(requirement.name),
                                                  'type': self.check_object_type(requirement.type),
                                                  'alias': requirement.alias})

                description_tag = etree.SubElement(requirement_tag, "description")
                description_tag.text = requirement.description

                _req_part_list_tag = etree.SubElement(requirement_tag, "requirementPartList")

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)

    def write_requirement_description(self, p_description_list):
        """Write requirement description from list [requirement, description]
        @param[in] object_allocated_object_list : list of requirement description
        @return None
        """
        parser = etree.XMLParser(remove_blank_text=True)
        root = self.tree.parse(self.file, parser)

        for requirement_tag in root.findall(".//requirement"):
            for req, description_req in p_description_list:
                if requirement_tag.get('id') == req.id:
                    tag = requirement_tag.find('description')
                    tag.text = util.normalize_xml_string(description_req)
                # Else do nothing

        self.tree.write(self.file, encoding='utf-8', xml_declaration=True, pretty_print=True)
