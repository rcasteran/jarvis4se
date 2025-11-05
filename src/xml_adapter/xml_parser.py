"""@defgroup xml_adapter
Module for 3SE xml parsing and writing
"""
# Libraries
from lxml import etree

# Modules
import datamodel
from tools import Logger
from . import util

# Type definition


class XmlParser3SE:
    """@ingroup xml_adapter
    @anchor XmlParser3SE
    3SE xml parser
    """

    def __init__(self):
        """ @var xml_dict
        XML dictionary

        @var root
        Reference to the XML root object
        """

        self.xml_dict = {util.XML_DICT_KEY_0_DATA_LIST: set(),
                         util.XML_DICT_KEY_1_FUNCTION_LIST: set(),
                         util.XML_DICT_KEY_2_FUN_ELEM_LIST: set(),
                         util.XML_DICT_KEY_3_FUN_INTF_LIST: set(),
                         util.XML_DICT_KEY_4_PHY_ELEM_LIST: set(),
                         util.XML_DICT_KEY_5_PHY_INTF_LIST: set(),
                         util.XML_DICT_KEY_6_STATE_LIST: set(),
                         util.XML_DICT_KEY_7_TRANSITION_LIST: set(),
                         util.XML_DICT_KEY_8_REQUIREMENT_LIST: set(),
                         util.XML_DICT_KEY_9_GOAL_LIST: set(),
                         util.XML_DICT_KEY_10_ACTIVITY_LIST: set(),
                         util.XML_DICT_KEY_11_INFORMATION_LIST: set(),
                         util.XML_DICT_KEY_12_ATTRIBUTE_LIST: set(),
                         util.XML_DICT_KEY_13_VIEW_LIST: set(),
                         util.XML_DICT_KEY_14_TYPE_LIST: set(),
                         util.XML_DICT_KEY_15_FUN_CONS_LIST: [],
                         util.XML_DICT_KEY_16_FUN_PROD_LIST: [],
                         util.XML_DICT_KEY_17_ACT_CONS_LIST: [],
                         util.XML_DICT_KEY_18_ACT_PROD_LIST: []
                         }
        self.root = None

    def parse_xml(self, input_filename):
        """Parse the XML file and returns the XML dictionary
        @param[in] input_filename : XML file name
        @return XML dictionary
        """
        # To speed up parsing (see lxml doc) : TBC if can be extended to xml_writer
        parser = etree.XMLParser(collect_ids=False)
        # Parse the XML file
        tree = etree.parse(input_filename, parser)
        # Get the XML tree
        self.root = tree.getroot()
        # Check xml root tag
        if self.check_xml():
            # First retrieve extended types
            self.xml_dict[util.XML_DICT_KEY_14_TYPE_LIST] = self.parse_type_list()
            self.xml_dict[util.XML_DICT_KEY_10_ACTIVITY_LIST] = self.parse_activity_list()
            self.xml_dict[util.XML_DICT_KEY_1_FUNCTION_LIST] = self.parse_function_list()
            self.xml_dict[util.XML_DICT_KEY_6_STATE_LIST] = self.parse_state_list()
            self.xml_dict[util.XML_DICT_KEY_7_TRANSITION_LIST] = self.parse_transition_list()
            self.xml_dict[util.XML_DICT_KEY_2_FUN_ELEM_LIST] = self.parse_functional_element_list()
            self.xml_dict[util.XML_DICT_KEY_13_VIEW_LIST] = self.parse_view_list()
            self.xml_dict[util.XML_DICT_KEY_12_ATTRIBUTE_LIST] = self.parse_attribute_list()
            self.xml_dict[util.XML_DICT_KEY_3_FUN_INTF_LIST] = self.parse_functional_interface_list()
            self.xml_dict[util.XML_DICT_KEY_4_PHY_ELEM_LIST] = self.parse_physical_element_list()
            self.xml_dict[util.XML_DICT_KEY_5_PHY_INTF_LIST] = self.parse_physical_interface_list()
            self.xml_dict[util.XML_DICT_KEY_8_REQUIREMENT_LIST] = self.parse_requirement_list()
            self.xml_dict[util.XML_DICT_KEY_9_GOAL_LIST] = self.parse_goal_list()

            # Then create data and set predecessors, consumers, producers lists
            self.xml_dict[util.XML_DICT_KEY_0_DATA_LIST], self.xml_dict[util.XML_DICT_KEY_16_FUN_PROD_LIST], \
                self.xml_dict[util.XML_DICT_KEY_15_FUN_CONS_LIST] = self.parse_data_list()

            # Then create information and set predecessors, consumers, producers lists
            self.xml_dict[util.XML_DICT_KEY_11_INFORMATION_LIST], self.xml_dict[util.XML_DICT_KEY_18_ACT_PROD_LIST], \
                self.xml_dict[util.XML_DICT_KEY_17_ACT_CONS_LIST] = self.parse_information_list()

            # Finally update object types
            self.update_object_type()
        else:
            Logger.set_error(__name__,
                             f"Xml's file structure has changed, please delete {input_filename} "
                             f"and re-execute your whole notebook")

        return self.xml_dict

    def check_xml(self):
        """Check XML file structure

        Since jarvis4se version 1.3 XML root element is <systemAnalysis>
        @return XML file is well-structured (True) or not (FALSE
        """
        if self.root.tag == "systemAnalysis":
            return True
        else:
            return False

    @staticmethod
    def update_parental_relationship(parent_id_list, element_list):
        """Update parental relationship between two elements

        The elements must implement the following methods:
        - set_parent()
        - add_child()

        @param[in] parent_id_list : list of parent element identifiers
        @param[in] element_list : list of element
        @return None
        """
        for child_id in parent_id_list:
            for element in element_list:
                if element.id == child_id:
                    # We have the child element, now search for the parent element
                    for parent_elem in element_list:
                        if parent_elem.id == parent_id_list[child_id]:
                            element.set_parent(parent_elem)
                            parent_elem.add_child(element)

                            Logger.set_debug(__name__, f"Element [{parent_elem.id}, {parent_elem.name}]"
                                                       f" is parent of "
                                                       f"element [{element.id}, {element.name}]")
                            break
                    break

    @staticmethod
    def update_derived_object(element_list):
        """Update derived objects of an element list based on their identifiers

        @param[in] element_list : list of element
        @return None
        """
        for elem in element_list:
            for derived in element_list:
                if elem.derived == derived.id:
                    elem.derived = derived
                    break

    def parse_activity_list(self):
        """Parse XML activity list
        @return activity list
        """
        activity_list = set()
        parent_list = {}
        xml_activity_list = self.root.iter('activity')
        for xml_activity in xml_activity_list:
            # Instantiate activities and add them to a list
            activity = datamodel.Activity(p_id=xml_activity.get('id'),
                                          p_name=util.denormalize_xml_string(xml_activity.get('name')),
                                          p_alias=xml_activity.get('alias'),
                                          p_type=xml_activity.get('type'))

            activity_list.add(activity)

            # Looking for allocated goals and add them to the activity
            xml_allocated_goal_list = xml_activity.iter('allocatedGoal')
            for xml_allocated_goal in xml_allocated_goal_list:
                activity.add_allocated_goal(xml_allocated_goal.get("id"))

                Logger.set_debug(__name__, f"Goal [{xml_allocated_goal.get('id')}]"
                                           f" is satisfied by "
                                           f"activity [{activity.id}, {activity.name}]")

        return activity_list

    def parse_function_list(self):
        """Parse XML function list
        @return function list
        """
        function_list = set()
        parent_list = {}
        xml_function_list = self.root.iter('function')
        for xml_function in xml_function_list:
            # Instantiate functions and add them to a list
            if len(xml_function.get('derived')) > 0:
                function = datamodel.Function(p_id=xml_function.get('id'),
                                              p_name=util.denormalize_xml_string(xml_function.get('name')),
                                              p_alias=xml_function.get('alias'),
                                              p_type=xml_function.get('type'),
                                              p_derived=xml_function.get('derived'))
            else:
                function = datamodel.Function(p_id=xml_function.get('id'),
                                              p_name=util.denormalize_xml_string(xml_function.get('name')),
                                              p_alias=xml_function.get('alias'),
                                              p_type=xml_function.get('type'))
            function.set_operand()

            function_list.add(function)

            # Looking for functions with "functionalPart" i.e childs and create a list
            xml_part_list = xml_function.iter('functionPart')
            for xml_part in xml_part_list:
                parent_list[xml_part.get('id')] = function.id

            # Looking for allocated activities and add them to the function
            xml_allocated_activity_list = xml_function.iter('allocatedActivity')
            for xml_allocated_activity in xml_allocated_activity_list:
                function.add_allocated_activity(xml_allocated_activity.get("id"))

                Logger.set_debug(__name__, f"Activity [{xml_allocated_activity.get('id')}]"
                                           f" is allocated to "
                                           f"function [{function.id}, {function.name}]")

            # Looking for allocated requirements and add them to the function
            xml_allocated_requirement_list = xml_function.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                function.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"function [{function.id}, {function.name}]")

        # Loop to set parent and child relationship
        self.update_parental_relationship(parent_list, function_list)

        # Loop to update derived functions according to their ids
        self.update_derived_object(function_list)

        return function_list

    def parse_data_list(self):
        """Parse XML data list
        @return data list, producer function list, consumer function list
        """
        data_list = set()
        consumer_function_list = []
        producer_function_list = []

        xml_data_list = self.root.iter('data')
        for xml_data in xml_data_list:
            # Instantiate data and add it to a list
            data = datamodel.Data(p_id=xml_data.get('id'),
                                  p_name=util.denormalize_xml_string(xml_data.get('name')),
                                  p_type=xml_data.get('type'))
            data_list.add(data)

            # Looking for allocated informations and add them to the data
            xml_allocated_information_list = xml_data.iter('allocatedInformation')
            for xml_allocated_information in xml_allocated_information_list:
                data.add_allocated_information(xml_allocated_information.get("id"))

                Logger.set_debug(__name__, f"Information [{xml_allocated_information.get('id')}]"
                                           f" is allocated to "
                                           f"data [{data.id}, {data.name}]")

            # Looking for allocated requirements and add them to the data
            xml_allocated_requirement_list = xml_data.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                data.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"data [{data.id}, {data.name}]")

            # looking for all elements with tag "consumer" and create a list [flow_name, consumer_function]
            xml_consumer_list = xml_data.iter('consumer')
            for xml_consumer in xml_consumer_list:
                for function in self.xml_dict[util.XML_DICT_KEY_1_FUNCTION_LIST]:
                    if xml_consumer.get('id') == function.id:
                        consumer_function_list.append([data, function])
                        Logger.set_debug(__name__, f"Data [{data.id}, {data.name}]"
                                                   f" is consumed by "
                                                   f"function [{function.id}, {function.name}]")

                        if xml_consumer.get('role') != 'none':
                            function.set_input_role(util.denormalize_xml_string(xml_data.get('name')))
                        # Avoid to reset the input role once already set
                        elif function.input_role is None:
                            function.set_input_role(None)

            # looking for all elements with tag "producer" and create a list [flow_name, producer_function]
            xml_producer_list = xml_data.iter('producer')
            for xml_producer in xml_producer_list:
                for function in self.xml_dict[util.XML_DICT_KEY_1_FUNCTION_LIST]:
                    if xml_producer.get('id') == function.id:
                        producer_function_list.append([data, function])
                        Logger.set_debug(__name__, f"Data [{data.id}, {data.name}]"
                                                   f" is produced by "
                                                   f"function [{function.id}, {function.name}]")

        # Loop on the data_list once created to find the predecessor and add it to list
        for object_data in data_list:
            xml_data_list = self.root.iter('data')
            for xml_data in xml_data_list:
                if xml_data.get('id') == object_data.id:
                    # looking for all elements with tag "predecessor"
                    xml_predecessor_list = xml_data.iter('predecessor')
                    for xml_predecessor in xml_predecessor_list:
                        for dodo in data_list:
                            if xml_predecessor.get('id') == dodo.id:
                                object_data.add_predecessor(dodo)

                                Logger.set_debug(__name__, f"Data [{dodo.id, dodo.name}]"
                                                           f" is predecessor of "
                                                           f"data [{object_data.id, object_data.name}]")

        return data_list, producer_function_list, consumer_function_list

    def parse_information_list(self):
        """Parse XML information list
        @return information list, producer activity list, consumer activity list
        """
        information_list = set()
        consumer_activity_list = []
        producer_activity_list = []

        xml_information_list = self.root.iter('information')
        for xml_information in xml_information_list:
            # Instantiate information and add it to a list
            information = datamodel.Information(p_id=xml_information.get('id'),
                                                p_name=util.denormalize_xml_string(xml_information.get('name')),
                                                p_type=xml_information.get('type'))
            information_list.add(information)

            # looking for all elements with tag "consumer" and create a list [flow_name, consumer_activity]
            xml_consumer_list = xml_information.iter('consumer')
            for xml_consumer in xml_consumer_list:
                for activity in self.xml_dict[util.XML_DICT_KEY_10_ACTIVITY_LIST]:
                    if xml_consumer.get('id') == activity.id:
                        consumer_activity_list.append([information, activity])
                        Logger.set_debug(__name__, f"Information [{information.id}, {information.name}]"
                                                   f" is consumed by "
                                                   f"activity [{activity.id}, {activity.name}]")
                    # Else do nothing

            # looking for all elements with tag "producer" and create a list [flow_name, producer_activity]
            xml_producer_list = xml_information.iter('producer')
            for xml_producer in xml_producer_list:
                for activity in self.xml_dict[util.XML_DICT_KEY_10_ACTIVITY_LIST]:
                    if xml_producer.get('id') == activity.id:
                        producer_activity_list.append([information, activity])
                        Logger.set_debug(__name__, f"Information [{information.id}, {information.name}]"
                                                   f" is produced by "
                                                   f"function [{activity.id}, {activity.name}]")

        # Loop on the information_list once created to find the predecessor and add it to list
        for object_information in information_list:
            xml_information_list = self.root.iter('information')
            for xml_information in xml_information_list:
                if xml_information.get('id') == object_information.id:
                    # looking for all elements with tag "predecessor"
                    xml_predecessor_list = xml_information.iter('predecessor')
                    for xml_predecessor in xml_predecessor_list:
                        for dodo in information_list:
                            if xml_predecessor.get('id') == dodo.id:
                                object_information.add_predecessor(dodo)

                                Logger.set_debug(__name__, f"Information [{dodo.id, dodo.name}]"
                                                           f" is predecessor of "
                                                           f"information [{object_information.id, object_information.name}]")

        return information_list, producer_activity_list, consumer_activity_list

    def parse_state_list(self):
        """Parse XML state list
        @return state list
        """
        state_list = set()
        parent_list = {}
        xml_state_list = self.root.iter('state')
        for xml_state in xml_state_list:
            # Instantiate states and add them to a list
            state = datamodel.State(p_id=xml_state.get('id'),
                                    p_name=util.denormalize_xml_string(xml_state.get('name')),
                                    p_alias=xml_state.get('alias'),
                                    p_type=xml_state.get('type'))
            state_list.add(state)

            # Looking for states with "statePart" i.e child and create a list
            xml_part_list = xml_state.iter('statePart')
            for xml_part in xml_part_list:
                parent_list[xml_part.get('id')] = state.id

            # Looking for allocated functions and add them to the state
            xml_allocated_function_list = xml_state.iter('allocatedFunction')
            for xml_function in xml_allocated_function_list:
                state.add_allocated_function(xml_function.get("id"))

                Logger.set_debug(__name__, f"Function [{xml_function.get('id')}]"
                                           f" is allocated to "
                                           f"state [{state.id}, {state.name}]")

            # Looking for allocated requirements and add them to the state
            xml_allocated_requirement_list = xml_state.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                state.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"state [{state.id}, {state.name}]")

        # Loop to set parent and child relationship
        self.update_parental_relationship(parent_list, state_list)

        return state_list

    def parse_transition_list(self):
        """Parse XML transition list
        @return transition list
        """
        transition_list = set()
        xml_transition_list = self.root.iter('transition')
        for xml_transition in xml_transition_list:
            # Instantiate transitions and add them to a list
            transition = datamodel.Transition(p_id=xml_transition.get('id'),
                                              p_name=util.denormalize_xml_string(xml_transition.get('name')),
                                              p_alias=xml_transition.get('alias'),
                                              p_type=xml_transition.get('type'),
                                              p_source=xml_transition.get('source'),
                                              p_destination=xml_transition.get('destination'))

            transition_list.add(transition)

            # Looking for conditions and add them to the transition
            xml_transition_condition_list = xml_transition.iter('condition')
            for xml_condition in xml_transition_condition_list:
                transition.add_condition(util.denormalize_xml_string(xml_condition.get("text")))

            # Looking for allocated requirements and add them to the transition
            xml_allocated_requirement_list = xml_transition.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                transition.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"transition [{transition.id}, {transition.name}]")

        return transition_list

    def parse_functional_element_list(self):
        """Parse XML functional element list
        @return functional element list
        """
        functional_element_list = set()
        parent_list = {}
        xml_functional_element_list = self.root.iter('functionalElement')
        for xml_func_elem in xml_functional_element_list:
            # Instantiate functional element and add them to a list
            if len(xml_func_elem.get('derived')) > 0:
                fun_elem = datamodel.FunctionalElement(p_id=xml_func_elem.get('id'),
                                                       p_name=util.denormalize_xml_string(xml_func_elem.get('name')),
                                                       p_alias=xml_func_elem.get('alias'),
                                                       p_type=xml_func_elem.get('type'),
                                                       p_derived=xml_func_elem.get('derived'))
            else:
                fun_elem = datamodel.FunctionalElement(p_id=xml_func_elem.get('id'),
                                                       p_name=util.denormalize_xml_string(xml_func_elem.get('name')),
                                                       p_alias=xml_func_elem.get('alias'),
                                                       p_type=xml_func_elem.get('type'))
            functional_element_list.add(fun_elem)

            # Looking for "functionalElementPart" i.e child and create a list
            xml_part_list = xml_func_elem.iter('functionalElementPart')
            for xml_part in xml_part_list:
                parent_list[xml_part.get('id')] = fun_elem.id

            # Looking for allocated states and add them to the functional element
            xml_allocated_state_list = xml_func_elem.iter('allocatedState')
            for xml_state in xml_allocated_state_list:
                fun_elem.add_allocated_state(xml_state.get("id"))
                Logger.set_debug(__name__, f"State [{xml_state.get('id')}]"
                                           f" is allocated to "
                                           f"functional element [{fun_elem.id}, {fun_elem.name}]")

            # Looking for allocated functions and add them to the functional element
            xml_allocated_function_list = xml_func_elem.iter('allocatedFunction')
            for xml_fun in xml_allocated_function_list:
                fun_elem.add_allocated_function(xml_fun.get("id"))
                Logger.set_debug(__name__, f"Function [{xml_fun.get('id')}]"
                                           f" is allocated to "
                                           f"functional element [{fun_elem.id}, {fun_elem.name}]")

            # Looking for exposed interface and add them to the functional element
            xml_exposed_interface_list = xml_func_elem.iter('exposedInterface')
            for xml_exp_inter in xml_exposed_interface_list:
                fun_elem.add_exposed_interface(xml_exp_inter.get("id"))
                Logger.set_debug(__name__, f"Functional interface [{xml_exp_inter.get('id')}]"
                                           f" is exposed by "
                                           f"functional element [{fun_elem.id}, {fun_elem.name}]")

            # Looking for allocated requirements and add them to the functional element
            xml_allocated_requirement_list = xml_func_elem.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                fun_elem.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"functional element [{fun_elem.id}, {fun_elem.name}]")

        # Loop to set parent and child relationship
        self.update_parental_relationship(parent_list, functional_element_list)

        # Loop to update derived functional elements according to their ids
        self.update_derived_object(functional_element_list)

        return functional_element_list

    def parse_view_list(self):
        """Parse XML view list
        @return view list
        """
        view_list = set()
        xml_view_list = self.root.iter('view')
        for xml_view in xml_view_list:
            # Instantiate view and add them to a list
            view = datamodel.View(uid=xml_view.get('id'),
                                  name=util.denormalize_xml_string(xml_view.get('name')),
                                  v_type=xml_view.get('type'))

            view_list.add(view)

            # Looking for allocated items and add them to the view
            xml_allocated_item_list = xml_view.iter('allocatedItem')
            for xml_item in xml_allocated_item_list:
                view.add_allocated_item(xml_item.get("id"))
                Logger.set_debug(__name__, f"Element [{xml_item.get('id')}]"
                                           f" is allocated to "
                                           f"view [{view.id}, {view.name}]")

                if len(xml_item.get("consumer")) > 0:
                    view.add_allocated_item_filter(xml_item.get('id'),
                                                   xml_item.get('consumer'),
                                                   xml_item.get('producer'))
                    Logger.set_debug(__name__, f"Element [{xml_item.get('id')}]"
                                               f" is filtered to consumer [{xml_item.get('consumer')}]"
                                               f" and producer [{xml_item.get('producer')}]")
                # Else do nothing

        return view_list

    def parse_attribute_list(self):
        """Parse XML attribute list
        @return attribute list
        """
        attribute_list = set()
        xml_attribute_list = self.root.iter('attribute')
        for xml_attribute in xml_attribute_list:
            # Instantiate Attribute and add them to a list
            attribute = datamodel.Attribute(p_id=xml_attribute.get('id'),
                                            p_name=util.denormalize_xml_string(xml_attribute.get('name')),
                                            p_alias=xml_attribute.get('alias'),
                                            p_type=xml_attribute.get('type'))

            attribute_list.add(attribute)

            # Looking for described items and add them to the attribute
            xml_described_item_list = xml_attribute.iter('describedItem')
            for xml_described_item in xml_described_item_list:
                attribute.add_described_item((xml_described_item.get("id"),
                                              util.denormalize_xml_string(xml_described_item.get("value"))))
                Logger.set_debug(__name__, f"Element [{xml_described_item.get('id')}] "
                                           f"is described by "
                                           f"attribute [{attribute.id}, {attribute.name}] "
                                           f"with the value : "
                                           f"{util.denormalize_xml_string(xml_described_item.get('value'))}")

            # Looking for allocated requirements and add them to the functional interface
            xml_allocated_requirement_list = xml_attribute.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                attribute.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"attribute [{attribute.id}, {attribute.name}]")

        return attribute_list

    def parse_functional_interface_list(self):
        """Parse XML functional interface list
        @return functional interface list
        """
        functional_interface_list = set()
        xml_fun_inter_list = self.root.iter('functionalInterface')
        for xml_fun_inter in xml_fun_inter_list:
            # Instantiate fun_inter and add them to a list
            if len(xml_fun_inter.get('derived')) > 0:
                fun_inter = datamodel.FunctionalInterface(p_id=xml_fun_inter.get('id'),
                                                          p_name=util.denormalize_xml_string(xml_fun_inter.get('name')),
                                                          p_alias=xml_fun_inter.get('alias'),
                                                          p_type=xml_fun_inter.get('type'),
                                                          p_derived=xml_fun_inter.get('derived'))
            else:
                fun_inter = datamodel.FunctionalInterface(p_id=xml_fun_inter.get('id'),
                                                          p_name=util.denormalize_xml_string(xml_fun_inter.get('name')),
                                                          p_alias=xml_fun_inter.get('alias'),
                                                          p_type=xml_fun_inter.get('type'))

            functional_interface_list.add(fun_inter)

            # Looking for allocated data and add them to the fun inter
            xml_allocated_data_list = xml_fun_inter.iter('allocatedData')
            for xml_data in xml_allocated_data_list:
                fun_inter.add_allocated_data(xml_data.get("id"))
                Logger.set_debug(__name__, f"Data [{xml_data.get('id')}]"
                                           f" is allocated to "
                                           f"functional interface [{fun_inter.id}, {fun_inter.name}]")

            # Looking for allocated requirements and add them to the functional interface
            xml_allocated_requirement_list = xml_fun_inter.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                fun_inter.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"functional interface [{fun_inter.id}, {fun_inter.name}]")

        # Loop to update derived functional elements according to their ids
        self.update_derived_object(functional_interface_list)

        return functional_interface_list

    def parse_physical_element_list(self):
        """Parse XML physical element list
        @return physical element list
        """
        physical_element_list = set()
        parent_list = {}
        xml_physical_element_list = self.root.iter('physicalElement')
        for xml_phy_elem in xml_physical_element_list:
            # Instantiate functional element and add them to a list
            if len(xml_phy_elem.get('derived')) > 0:
                phy_elem = datamodel.PhysicalElement(p_id=xml_phy_elem.get('id'),
                                                     p_name=util.denormalize_xml_string(xml_phy_elem.get('name')),
                                                     p_alias=xml_phy_elem.get('alias'),
                                                     p_type=xml_phy_elem.get('type'),
                                                     p_derived=xml_phy_elem.get('derived'))
            else:
                phy_elem = datamodel.PhysicalElement(p_id=xml_phy_elem.get('id'),
                                                     p_name=util.denormalize_xml_string(xml_phy_elem.get('name')),
                                                     p_alias=xml_phy_elem.get('alias'),
                                                     p_type=xml_phy_elem.get('type'))

            physical_element_list.add(phy_elem)

            # Looking for "physicalPart" i.e child and create a list
            xml_physical_part_list = xml_phy_elem.iter('physicalElementPart')
            for xml_part in xml_physical_part_list:
                parent_list[xml_part.get('id')] = phy_elem.id

            # Looking for allocated activities and add them to the physical element
            xml_allocated_activity_list = xml_phy_elem.iter('allocatedActivity')
            for xml_activity in xml_allocated_activity_list:
                phy_elem.add_allocated_activity(xml_activity.get("id"))
                Logger.set_debug(__name__, f"Activity [{xml_activity.get('id')}]"
                                           f" is allocated to "
                                           f"physical element [{phy_elem.id}, {phy_elem.name}]")

            # Looking for allocated functional elements and add them to the physical element
            xml_allocated_fun_elem_list = xml_phy_elem.iter('allocatedFunctionalElement')
            for xml_fun_elem in xml_allocated_fun_elem_list:
                phy_elem.add_allocated_fun_elem(xml_fun_elem.get("id"))
                Logger.set_debug(__name__, f"Functional element [{xml_fun_elem.get('id')}]"
                                           f" is allocated to "
                                           f"physical element [{phy_elem.id}, {phy_elem.name}]")

            # Looking for exposed interface and add them to the functional element
            xml_exposed_interface_list = xml_phy_elem.iter('exposedInterface')
            for xml_exp_inter in xml_exposed_interface_list:
                phy_elem.add_exposed_interface(xml_exp_inter.get("id"))
                Logger.set_debug(__name__, f"Physical interface [{xml_exp_inter.get('id')}]"
                                           f" is exposed by "
                                           f"physical element [{phy_elem.id}, {phy_elem.name}]")

            # Looking for allocated requirements and add them to the physical element
            xml_allocated_requirement_list = xml_phy_elem.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                phy_elem.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"physical element [{phy_elem.id}, {phy_elem.name}]")

            # Looking for allocated goals and add them to the physical element
            xml_allocated_goal_list = xml_phy_elem.iter('allocatedGoal')
            for xml_allocated_goal in xml_allocated_goal_list:
                phy_elem.add_allocated_goal(xml_allocated_goal.get("id"))

                Logger.set_debug(__name__, f"Goal [{xml_allocated_goal.get('id')}]"
                                           f" is satisfied by "
                                           f"physical element [{phy_elem.id}, {phy_elem.name}]")

        # Loop to set parent and child relationship
        self.update_parental_relationship(parent_list, physical_element_list)

        # Loop to update derived functions according to their ids
        self.update_derived_object(physical_element_list)

        return physical_element_list

    def parse_physical_interface_list(self):
        """Parse XML physical interface list
        @return physical interface list
        """
        physical_interface_list = set()
        xml_phy_inter_list = self.root.iter('physicalInterface')
        for xml_phy_inter in xml_phy_inter_list:
            # Instantiate phy_inter and add them to a list
            if len(xml_phy_inter.get('derived')) > 0:
                phy_inter = datamodel.PhysicalInterface(p_id=xml_phy_inter.get('id'),
                                                        p_name=util.denormalize_xml_string(xml_phy_inter.get('name')),
                                                        p_alias=xml_phy_inter.get('alias'),
                                                        p_type=xml_phy_inter.get('type'),
                                                        p_derived=xml_phy_inter.get('derived'))
            else:
                phy_inter = datamodel.PhysicalInterface(p_id=xml_phy_inter.get('id'),
                                                        p_name=util.denormalize_xml_string(xml_phy_inter.get('name')),
                                                        p_alias=xml_phy_inter.get('alias'),
                                                        p_type=xml_phy_inter.get('type'))

            physical_interface_list.add(phy_inter)

            # Looking for allocated fun_inter and add them to the phy inter
            xml_allocated_inter_list = xml_phy_inter.iter('allocatedFunctionalInterface')
            for xml_inter in xml_allocated_inter_list:
                phy_inter.add_allocated_fun_inter(xml_inter.get("id"))
                Logger.set_debug(__name__, f"Functional interface [{xml_inter.get('id')}]"
                                           f" is allocated to "
                                           f"physical interface [{phy_inter.id}, {phy_inter.name}]")

            # Looking for allocated requirements and add them to the physical interface
            xml_allocated_requirement_list = xml_phy_inter.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                phy_inter.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"physical interface [{phy_inter.id}, {phy_inter.name}]")

        # Loop to update derived functions according to their ids
        self.update_derived_object(physical_interface_list)

        return physical_interface_list

    def parse_type_list(self):
        """Parse XML type list
        @return type list
        """
        type_list = set()
        xml_type_list = self.root.iter('type')
        for xml_type in xml_type_list:
            # Instantiate Type and add them to a list
            type_obj = datamodel.Type(p_id=xml_type.get('id'),
                                      p_name=util.denormalize_xml_string(xml_type.get('name')),
                                      p_alias=xml_type.get('alias'),
                                      p_base=xml_type.get('base'))
            type_list.add(type_obj)

            # Looking for allocated requirements and add them to the type
            xml_allocated_requirement_list = xml_type.iter('allocatedRequirement')
            for xml_allocated_requirement in xml_allocated_requirement_list:
                type_obj.add_allocated_requirement(xml_allocated_requirement.get("id"))

                Logger.set_debug(__name__, f"Requirement [{xml_allocated_requirement.get('id')}]"
                                           f" is satisfied by "
                                           f"type [{type_obj.id}, {type_obj.name}]")

        # Update base type depending if it is a 3SE base type or if it is a custom one
        for obj_type in type_list:
            if any(obj_type.base in a for a in [str(i) for i in datamodel.BaseType]):
                obj_type.base = datamodel.BaseType[obj_type.base.upper().replace(" ", "_")]
            else:
                is_found = False
                for base in type_list:
                    if obj_type.base == base.id:
                        obj_type.base = base
                        is_found = True
                        break

                if not is_found:
                    Logger.set_error(__name__,
                                     f"Unknown type {obj_type} found when parsing xml")

        return type_list

    def update_object_type(self):
        """Update objects in the dictionary with their types.
        @return None
        """
        # Following lists does not contain any type definition
        unwanted_xml_list = (util.XML_DICT_KEY_14_TYPE_LIST, util.XML_DICT_KEY_15_FUN_CONS_LIST,
                             util.XML_DICT_KEY_16_FUN_PROD_LIST, util.XML_DICT_KEY_17_ACT_CONS_LIST,
                             util.XML_DICT_KEY_18_ACT_PROD_LIST)
        for key, xml_list in self.xml_dict.items():
            if key not in unwanted_xml_list:
                for obj in xml_list:
                    try:
                        # Base type are defined with their names
                        obj.type = datamodel.BaseType[obj.type.upper().replace(" ", "_")]
                    except KeyError:
                        # Extended types are defined in xml_type_list with their ids
                        is_found = False
                        for type_obj in self.xml_dict[util.XML_DICT_KEY_14_TYPE_LIST]:
                            if obj.type == type_obj.id:
                                obj.type = type_obj
                                is_found = True
                                break

                        if not is_found:
                            Logger.set_error(__name__,
                                             f"Unknown type {obj.type} found when parsing xml")

    def parse_requirement_list(self):
        """Parse XML requirement list
        @return requirement list
        """
        requirement_list = set()
        parent_list = {}
        xml_requirement_list = self.root.iter('requirement')
        for xml_requirement in xml_requirement_list:
            # Instantiate Requirement and add it to a list
            requirement = datamodel.Requirement(p_id=xml_requirement.get('id'),
                                                p_name=util.denormalize_xml_string(xml_requirement.get('name')),
                                                p_alias=xml_requirement.get('alias'),
                                                p_type=xml_requirement.get('type'))

            requirement_list.add(requirement)

            # Looking for requirement text
            xml_text_list = xml_requirement.iter('text')
            for xml_text in xml_text_list:
                requirement.set_text(util.denormalize_xml_string(xml_text.text))

            # Looking for requirement child
            xml_requirement_part_list = xml_requirement.iter('requirementPart')
            for xml_part in xml_requirement_part_list:
                parent_list[xml_part.get('id')] = requirement.id

        # Loop to set parent and child relationship
        self.update_parental_relationship(parent_list, requirement_list)

        return requirement_list

    def parse_goal_list(self):
        """Parse XML goal list
        @return goal list
        """
        goal_list = set()
        parent_list = {}
        xml_goal_list = self.root.iter('goal')
        for xml_goal in xml_goal_list:
            # Instantiate Goal and add it to a list
            goal = datamodel.Goal(p_id=xml_goal.get('id'),
                                  p_name=util.denormalize_xml_string(xml_goal.get('name')),
                                  p_alias=xml_goal.get('alias'),
                                  p_type=xml_goal.get('type'))

            goal_list.add(goal)

            # Looking for goal text
            xml_text_list = xml_goal.iter('text')
            for xml_text in xml_text_list:
                goal.set_text(util.denormalize_xml_string(xml_text.text))

            # Looking for goal child
            xml_goal_part_list = xml_goal.iter('goalPart')
            for xml_part in xml_goal_part_list:
                parent_list[xml_part.get('id')] = goal.id

        # Loop to set parent and child relationship
        self.update_parental_relationship(parent_list, goal_list)

        return goal_list


# Global variables definition
XmlDictKeyListForObjects = [util.XML_DICT_KEY_0_DATA_LIST,
                            util.XML_DICT_KEY_1_FUNCTION_LIST,
                            util.XML_DICT_KEY_2_FUN_ELEM_LIST,
                            util.XML_DICT_KEY_3_FUN_INTF_LIST,
                            util.XML_DICT_KEY_4_PHY_ELEM_LIST,
                            util.XML_DICT_KEY_5_PHY_INTF_LIST,
                            util.XML_DICT_KEY_6_STATE_LIST,
                            util.XML_DICT_KEY_7_TRANSITION_LIST,
                            util.XML_DICT_KEY_8_REQUIREMENT_LIST,
                            util.XML_DICT_KEY_9_GOAL_LIST,
                            util.XML_DICT_KEY_10_ACTIVITY_LIST,
                            util.XML_DICT_KEY_11_INFORMATION_LIST,
                            util.XML_DICT_KEY_12_ATTRIBUTE_LIST,
                            util.XML_DICT_KEY_13_VIEW_LIST,
                            util.XML_DICT_KEY_14_TYPE_LIST  # Type dictionary shall be the last one for query
                            ]

XmlDictKeyDictForObjectBaseTypes = {
    datamodel.BaseType.DATA: util.XML_DICT_KEY_0_DATA_LIST,
    datamodel.BaseType.FUNCTION: util.XML_DICT_KEY_1_FUNCTION_LIST,
    datamodel.BaseType.FUNCTIONAL_ELEMENT: util.XML_DICT_KEY_2_FUN_ELEM_LIST,
    datamodel.BaseType.FUNCTIONAL_INTERFACE: util.XML_DICT_KEY_3_FUN_INTF_LIST,
    datamodel.BaseType.PHYSICAL_ELEMENT: util.XML_DICT_KEY_4_PHY_ELEM_LIST,
    datamodel.BaseType.PHYSICAL_INTERFACE: util.XML_DICT_KEY_5_PHY_INTF_LIST,
    datamodel.BaseType.STATE: util.XML_DICT_KEY_6_STATE_LIST,
    datamodel.BaseType.TRANSITION: util.XML_DICT_KEY_7_TRANSITION_LIST,
    datamodel.BaseType.REQUIREMENT: util.XML_DICT_KEY_8_REQUIREMENT_LIST,
    datamodel.BaseType.GOAL: util.XML_DICT_KEY_9_GOAL_LIST,
    datamodel.BaseType.ACTIVITY: util.XML_DICT_KEY_10_ACTIVITY_LIST,
    datamodel.BaseType.INFORMATION: util.XML_DICT_KEY_11_INFORMATION_LIST,
    datamodel.BaseType.ATTRIBUTE: util.XML_DICT_KEY_12_ATTRIBUTE_LIST,
    datamodel.BaseType.VIEW: util.XML_DICT_KEY_13_VIEW_LIST,
}
