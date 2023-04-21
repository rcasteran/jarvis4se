"""@defgroup xml_adapter
Module for 3SE xml parsing and writing
"""
# Libraries
from lxml import etree

# Modules
import datamodel
from tools import Logger


class XmlParser3SE:
    """@ingroup xml_adapter
    @anchor XmlParser3SE
    3SE XML parser
    """

    def __init__(self):
        """ @var xml_dict
        XML dictionary

        @var root
        Reference to the XML root object
        """

        self.xml_dict = {'xml_function_list': set(),
                         'xml_consumer_function_list': [],
                         'xml_producer_function_list': [],
                         'xml_data_list': set(),
                         'xml_state_list': set(),
                         'xml_transition_list': set(),
                         'xml_fun_elem_list': set(),
                         'xml_view_list': set(),
                         'xml_attribute_list': set(),
                         'xml_fun_inter_list': set(),
                         'xml_phy_elem_list': set(),
                         'xml_phy_inter_list': set(),
                         'xml_type_list': set()}
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
            self.xml_dict['xml_type_list'] = self.parse_type_list()
            self.xml_dict['xml_function_list'] = self.parse_function_list()
            self.xml_dict['xml_state_list'] = self.parse_state_list()
            self.xml_dict['xml_transition_list'] = self.parse_transition_list()
            self.xml_dict['xml_fun_elem_list'] = self.parse_functional_element_list()
            self.xml_dict['xml_view_list'] = self.parse_view_list()
            self.xml_dict['xml_attribute_list'] = self.parse_attribute_list()
            self.xml_dict['xml_fun_inter_list'] = self.parse_functional_interface_list()
            self.xml_dict['xml_phy_elem_list'] = self.parse_physical_element_list()
            self.xml_dict['xml_phy_inter_list'] = self.parse_physical_interface_list()

            # Then create data(and set predecessors), consumers, producers lists
            self.xml_dict['xml_data_list'], self.xml_dict['xml_producer_function_list'], self.xml_dict[
                'xml_consumer_function_list'] = self.parse_data_list()

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

    def parse_function_list(self):
        """Parse XML function list
        @return function list
        """
        function_list = set()
        parent_list = {}
        xml_function_list = self.root.iter('function')
        for xml_function in xml_function_list:
            # Instantiate functions and add them to a list
            function = datamodel.Function(p_id=xml_function.get('id'), p_name=xml_function.get('name'),
                                          p_alias=xml_function.get('alias'),
                                          p_type=xml_function.get('type'),
                                          p_derived=xml_function.get('derived'))
            function.set_operand()

            function_list.add(function)

            # Looking for functions with "functionalPart" i.e childs and create a list
            xml_part_list = xml_function.iter('functionPart')
            for xml_part in xml_part_list:
                parent_list[xml_part.get('id')] = function.id

        # Loop to set parent and child to functions
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
                                  p_name=xml_data.get('name'),
                                  p_type=xml_data.get('type'))
            data_list.add(data)

            # looking for all elements with tag "consumer" and create a list [flow_name, consumer_function]
            xml_consumer_list = xml_data.iter('consumer')
            for xml_consumer in xml_consumer_list:
                for function in self.xml_dict['xml_function_list']:
                    if xml_consumer.get('id') == function.id:
                        consumer_function_list.append([xml_data.get('name'), function])
                        Logger.set_debug(__name__, f"Data [{xml_data.get('id')}, {xml_data.get('name')}]"
                                                   f" is consumed by "
                                                   f"function [{function.id}, {function.name}]")

                        if xml_consumer.get('role') != 'none':
                            function.set_input_role(xml_data.get('name'))
                        # Avoid to reset the input role once already set
                        elif function.input_role is None:
                            function.set_input_role(None)

            # looking for all elements with tag "producer" and create a list [flow_name, producer_function]
            xml_producer_list = xml_data.iter('producer')
            for xml_producer in xml_producer_list:
                for function in self.xml_dict['xml_function_list']:
                    if xml_producer.get('id') == function.id:
                        producer_function_list.append([xml_data.get('name'), function])
                        Logger.set_debug(__name__, f"Data [{xml_data.get('id')}, {xml_data.get('name')}]"
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
                                    p_name=xml_state.get('name'),
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

        # Loop to set parent and child to states
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
                                              p_name=xml_transition.get('name'),
                                              p_alias=xml_transition.get('alias'),
                                              p_type=xml_transition.get('type'),
                                              p_source=xml_transition.get('source'),
                                              p_destination=xml_transition.get('destination'))

            transition_list.add(transition)

            # Looking for conditions and add them to the transition
            xml_transition_condition_list = xml_transition.iter('condition')
            for xml_condition in xml_transition_condition_list:
                transition.add_condition(xml_condition.get("text"))

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
            fun_elem = datamodel.FunctionalElement(p_id=xml_func_elem.get('id'),
                                                   p_name=xml_func_elem.get('name'),
                                                   p_alias=xml_func_elem.get('alias'),
                                                   p_type=xml_func_elem.get('type'),
                                                   p_derived=xml_func_elem.get('derived'))
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

        # Loop to set parent and child to functional elements
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
                                  name=xml_view.get('name'),
                                  v_type=xml_view.get('type'))

            view_list.add(view)

            # Looking for allocated items and add them to the view
            xml_allocated_item_list = xml_view.iter('allocatedItem')
            for xml_item in xml_allocated_item_list:
                view.add_allocated_item(xml_item.get("id"))
                Logger.set_debug(__name__, f"Element [{xml_item.get('id')}]"
                                           f" is allocated to "
                                           f"view [{view.id}, {view.name}]")

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
                                            p_name=xml_attribute.get('name'),
                                            p_alias=xml_attribute.get('alias'),
                                            p_type=xml_attribute.get('type'))

            attribute_list.add(attribute)

            # Looking for described items and add them to the attribute
            xml_described_item_list = xml_attribute.iter('describedItem')
            for xml_described_item in xml_described_item_list:
                attribute.add_described_item((xml_described_item.get("id"),
                                              xml_described_item.get("value")))
                Logger.set_debug(__name__, f"Element [{xml_described_item.get('id')}]"
                                           f" is described by "
                                           f"view [{attribute.id}, {attribute.name}]"
                                           f" with the value : {xml_described_item.get('value')}")

        return attribute_list

    def parse_functional_interface_list(self):
        """Parse XML functional interface list
        @return functional interface list
        """
        functional_interface_list = set()
        xml_fun_inter_list = self.root.iter('functionalInterface')
        for xml_fun_inter in xml_fun_inter_list:
            # Instantiate fun_inter and add them to a list
            fun_inter = datamodel.FunctionalInterface(p_id=xml_fun_inter.get('id'),
                                                      p_name=xml_fun_inter.get('name'),
                                                      p_alias=xml_fun_inter.get('alias'),
                                                      p_type=xml_fun_inter.get('type'),
                                                      p_derived=xml_fun_inter.get('derived'))

            functional_interface_list.add(fun_inter)

            # Looking for allocated data and add them to the fun inter
            xml_allocated_data_list = xml_fun_inter.iter('allocatedData')
            for xml_data in xml_allocated_data_list:
                fun_inter.add_allocated_data(xml_data.get("id"))
                Logger.set_debug(__name__, f"Data [{xml_data.get('id')}]"
                                           f" is allocated to "
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
            phy_elem = datamodel.PhysicalElement(p_id=xml_phy_elem.get('id'),
                                                 p_name=xml_phy_elem.get('name'),
                                                 p_alias=xml_phy_elem.get('alias'),
                                                 p_type=xml_phy_elem.get('type'),
                                                 p_derived=xml_phy_elem.get('derived'))
            physical_element_list.add(phy_elem)

            # Looking for "physicalPart" i.e child and create a list
            xml_functional_part_list = xml_phy_elem.iter('physicalElementPart')
            for xml_part in xml_functional_part_list:
                parent_list[xml_part.get('id')] = phy_elem.id

            # Looking for allocated functions and add them to the functional element
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

        # Loop to set parent and child to functions
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
            phy_inter = datamodel.PhysicalInterface(p_id=xml_phy_inter.get('id'),
                                                    p_name=xml_phy_inter.get('name'),
                                                    p_alias=xml_phy_inter.get('alias'),
                                                    p_type=xml_phy_inter.get('type'),
                                                    p_derived=xml_phy_inter.get('derived'))
            physical_interface_list.add(phy_inter)

            # Looking for allocated fun_inter and add them to the phy inter
            xml_allocated_inter_list = xml_phy_inter.iter('allocatedFunctionalInterface')
            for xml_inter in xml_allocated_inter_list:
                phy_inter.add_allocated_fun_inter(xml_inter.get("id"))
                Logger.set_debug(__name__, f"Functional interface [{xml_inter.get('id')}]"
                                           f" is allocated to "
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
                                      p_name=xml_type.get('name'),
                                      p_alias=xml_type.get('alias'),
                                      p_base=xml_type.get('base'))
            type_list.add(type_obj)

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
        unwanted_xml_list = ('xml_type_list', 'xml_consumer_function_list', 'xml_producer_function_list')
        for key, xml_list in self.xml_dict.items():
            if key not in unwanted_xml_list:
                for obj in xml_list:
                    try:
                        # Base type are defined with their names
                        obj.type = datamodel.BaseType[obj.type.upper().replace(" ", "_")]
                    except KeyError:
                        # Extended types are defined in xml_type_list with their ids
                        is_found = False
                        for type_obj in self.xml_dict['xml_type_list']:
                            if obj.type == type_obj.id:
                                obj.type = type_obj
                                is_found = True
                                break

                        if not is_found:
                            Logger.set_error(__name__,
                                             f"Unknown type {obj.type} found when parsing xml")
