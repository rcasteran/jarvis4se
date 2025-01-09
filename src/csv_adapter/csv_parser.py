"""@defgroup csv_adapter
Module for 3SE csv parsing and writing
"""

# Libraries
import csv
import re

# Modules
import datamodel
from . import util
from tools import Logger


class CsvParser3SE:
    """@ingroup csv_adapter
    @anchor CsvParser3SE
    3SE csv parser
    """

    def __init__(self):
        """ @var csv_dict
        CSV dictionary

        @var array
        Array of CSV rows
        """

        self.csv_dict = {'csv_data_list': set(),
                         'csv_function_list': set(),
                         'csv_fun_elem_list': set(),
                         'csv_fun_inter_list': set(),
                         'csv_phy_elem_list': set(),
                         'csv_phy_inter_list': set(),
                         'csv_state_list': set(),
                         'csv_transition_list': set(),
                         'csv_requirement_list': set(),
                         'csv_activity_list': set(),
                         'csv_information_list': set(),
                         'csv_attribute_list': set(),
                         'csv_view_list': set(),
                         'csv_type_list': set(),
                         'csv_consumer_function_list': [],
                         'csv_producer_function_list': [],
                         'csv_consumer_activity_list': [],
                         'csv_producer_activity_list': []
                         }

        self.array = []

    def parse_csv(self, p_input_filename, p_data_column=0):
        """Parse the CSV file and returns the CSV dictionary
        @param[in] p_input_filename : CSV file name
        @param[in] p_data_column : CSV column number where requirements are defined
        @return CSV dictionary
        """
        self.array = []

        try:
            # Parse the CSV file
            with open(p_input_filename, 'r', encoding='utf8') as file_reader:
                reader = csv.reader(file_reader, delimiter=";", quoting=csv.QUOTE_NONE)

                for row in reader:
                    self.array.append(row)

            if p_data_column > 1:
                # CSV file is not a 3SE CSV format
                # It contains only requirement in the given data_column with:
                # - column 0 contains the requirement id
                # - column 1 contains the requirement title
                self.csv_dict['csv_requirement_list'] = self.parse_requirement_list(p_data_column)
            elif p_data_column == 0:
                # CSV file is a 3SE CSV format
                # First retrieve extended types
                self.csv_dict['csv_type_list'] = self.parse_type_list()
                self.csv_dict['csv_activity_list'] = self.parse_activity_list()
                self.csv_dict['csv_function_list'] = self.parse_function_list()
                self.csv_dict['csv_state_list'] = self.parse_state_list()
                self.csv_dict['csv_transition_list'] = self.parse_transition_list()
                self.csv_dict['csv_fun_elem_list'] = self.parse_functional_element_list()
                self.csv_dict['csv_view_list'] = self.parse_view_list()
                self.csv_dict['csv_attribute_list'] = self.parse_attribute_list()
                self.csv_dict['csv_fun_inter_list'] = self.parse_functional_interface_list()
                self.csv_dict['csv_phy_elem_list'] = self.parse_physical_element_list()
                self.csv_dict['csv_phy_inter_list'] = self.parse_physical_interface_list()
                self.csv_dict['csv_requirement_list'] = self.parse_requirement_list()

                # Then create data and set predecessors, consumers, producers lists
                self.csv_dict['csv_data_list'], self.csv_dict['csv_producer_function_list'], self.csv_dict[
                    'csv_consumer_function_list'] = self.parse_data_list()

                # Then create information and set predecessors, consumers, producers lists
                self.csv_dict['csv_information_list'], self.csv_dict['csv_producer_activity_list'], self.csv_dict[
                    'csv_consumer_activity_list'] = self.parse_information_list()

                # Finally update object types
                self.update_object_type()
            else:
                Logger.set_error(__name__,
                                 f"Importing requirements from a CSV file requires that first column "
                                 f"contains the requirement id and the second one the requirement title")
        except OSError:
            Logger.set_error(__name__, f"Unable to read CSV file: {p_input_filename}")

        return self.csv_dict

    def parse_type_list(self):
        """Parse CSV type list
        @return type list
        """
        type_list = set()
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_TYPE:
                # Instantiate Type and add them to a list
                type_obj = datamodel.Type(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                          p_name=row[util.CSV_NAME_IDX],
                                          p_alias=row[util.CSV_ALIAS_IDX],
                                          p_base=row[util.CSV_EXTENSION_IDX])
                type_list.add(type_obj)

        # Update base type depending if it is a 3SE base type or if it is a custom one
        for obj_type in type_list:
            if any(obj_type.base in a.lower() for a in [str(i) for i in datamodel.BaseType]):
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
                                     f"Unknown type {obj_type.name} found when parsing csv")

        return type_list

    def parse_activity_list(self):
        """Parse CSV activity list
        @return activity list
        """
        activity_list = set()
        parent_list = {}
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_ACTIVITY:
                # Instantiate activities and add them to a list
                activity = datamodel.Activity(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                              p_name=row[util.CSV_NAME_IDX],
                                              p_alias=row[util.CSV_ALIAS_IDX],
                                              p_type=row[util.CSV_EXTENSION_IDX])

                activity_list.add(activity)
            # Else do nothing

        # Loop to set parent and child relationship
        util.update_parental_relationship(parent_list, activity_list)

        return activity_list

    def parse_function_list(self):
        """Parse CSV function list
        @return function list
        """
        function_list = set()
        parent_list = {}
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_FUNCTION:
                # Instantiate functions and add them to a list
                if len(row[util.CSV_DERIVED_IDX]) > 0:
                    function = datamodel.Function(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                  p_name=row[util.CSV_NAME_IDX],
                                                  p_alias=row[util.CSV_ALIAS_IDX],
                                                  p_type=row[util.CSV_EXTENSION_IDX],
                                                  p_derived=row[util.CSV_DERIVED_IDX])
                else:
                    function = datamodel.Function(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                  p_name=row[util.CSV_NAME_IDX],
                                                  p_alias=row[util.CSV_ALIAS_IDX],
                                                  p_type=row[util.CSV_EXTENSION_IDX])

                function.set_operand()

                function_list.add(function)

                # Looking for functions with "functionalPart" i.e childs and create a list
                if len(row[util.CSV_CHILDREN_LIST_IDX]) > 0:
                    csv_part_id_list = row[util.CSV_CHILDREN_LIST_IDX].split("|")
                    for csv_part_id in csv_part_id_list:
                        parent_list[csv_part_id] = function.id
                # Else do nothing

                # Looking for allocated activities and add them to the function
                if len(row[util.CSV_ACTIVITY_LIST_IDX]) > 0:
                    csv_allocated_activity_id_list = row[util.CSV_ACTIVITY_LIST_IDX].split("|")
                    for csv_allocated_activity_id in csv_allocated_activity_id_list:
                        function.add_allocated_activity(csv_allocated_activity_id)

                        Logger.set_debug(__name__, f"Activity [{csv_allocated_activity_id}]"
                                                   f" is allocated to "
                                                   f"function [{function.id}, {function.name}]")
                # Else do nothing

                # Looking for allocated requirements and add them to the function
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split("|")
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        function.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"function [{function.id}, {function.name}]")
                # Else do nothing
            # Else do nothing

        # Loop to set parent and child relationship
        util.update_parental_relationship(parent_list, function_list)

        # Loop to update derived functions according to their ids
        util.update_derived_object(function_list)

        return function_list

    def parse_state_list(self):
        """Parse CSV state list
        @return state list
        """
        state_list = set()
        parent_list = {}
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_STATE:
                # Instantiate states and add them to a list
                state = datamodel.State(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                        p_name=row[util.CSV_NAME_IDX],
                                        p_alias=row[util.CSV_ALIAS_IDX],
                                        p_type=row[util.CSV_EXTENSION_IDX])
                state_list.add(state)

                # Looking for states with "statePart" i.e child and create a list
                if len(row[util.CSV_CHILDREN_LIST_IDX]) > 0:
                    csv_part_id_list = row[util.CSV_CHILDREN_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_part_id in csv_part_id_list:
                        parent_list[csv_part_id] = state.id
                # Else do nothing

                # Looking for allocated functions and add them to the state
                if len(row[util.CSV_FUNCTION_LIST_IDX]) > 0:
                    csv_function_id_list = row[util.CSV_FUNCTION_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_function_id in csv_function_id_list:
                        state.add_allocated_function(csv_function_id)

                        Logger.set_debug(__name__, f"Function [{csv_function_id}]"
                                                   f" is allocated to "
                                                   f"state [{state.id}, {state.name}]")
                # Else do nothing

                # Looking for allocated requirements and add them to the state
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        state.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"state [{state.id}, {state.name}]")
                # Else do nothing
            # Else do nothing

        # Loop to set parent and child relationship
        util.update_parental_relationship(parent_list, state_list)

        return state_list

    def parse_transition_list(self):
        """Parse CSV transition list
        @return transition list
        """
        transition_list = set()
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_TRANSITION:
                # Instantiate transitions and add them to a list
                transition = datamodel.Transition(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                  p_name=row[util.CSV_NAME_IDX],
                                                  p_alias=row[util.CSV_ALIAS_IDX],
                                                  p_type=row[util.CSV_EXTENSION_IDX],
                                                  p_source=row[util.CSV_SOURCE_IDX],
                                                  p_destination=row[util.CSV_DESTINATION_IDX])

                transition_list.add(transition)

                # Looking for conditions and add them to the transition
                if len(row[util.CSV_CONDITION_LIST_IDX]) > 0:
                    csv_condition_text_list = row[util.CSV_CONDITION_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_condition_text in csv_condition_text_list:
                        transition.add_condition(csv_condition_text)
                # Else do nothing

                # Looking for allocated requirements and add them to the transition
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        transition.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"transition [{transition.id}, {transition.name}]")
                # Else do nothing
            # Else do nothing

        return transition_list

    def parse_functional_element_list(self):
        """Parse CSV functional element list
        @return functional element list
        """
        functional_element_list = set()
        parent_list = {}
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_FUN_ELEM:
                # Instantiate functional element and add them to a list
                if len(row[util.CSV_DERIVED_IDX]) > 0:
                    fun_elem = datamodel.FunctionalElement(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                           p_name=row[util.CSV_NAME_IDX],
                                                           p_alias=row[util.CSV_ALIAS_IDX],
                                                           p_type=row[util.CSV_EXTENSION_IDX],
                                                           p_derived=row[util.CSV_DERIVED_IDX])
                else:
                    fun_elem = datamodel.FunctionalElement(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                           p_name=row[util.CSV_NAME_IDX],
                                                           p_alias=row[util.CSV_ALIAS_IDX],
                                                           p_type=row[util.CSV_EXTENSION_IDX])

                functional_element_list.add(fun_elem)

                # Looking for "functionalElementPart" i.e child and create a list
                if len(row[util.CSV_CHILDREN_LIST_IDX]) > 0:
                    csv_part_id_list = row[util.CSV_CHILDREN_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_part_id in csv_part_id_list:
                        parent_list[csv_part_id] = fun_elem.id
                # Else do nothing

                # Looking for allocated states and add them to the functional element
                if len(row[util.CSV_STATE_LIST_IDX]) > 0:
                    csv_state_id_list = row[util.CSV_STATE_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_state_id in csv_state_id_list:
                        fun_elem.add_allocated_state(csv_state_id)
                        Logger.set_debug(__name__, f"State [{csv_state_id}]"
                                                   f" is allocated to "
                                                   f"functional element [{fun_elem.id}, {fun_elem.name}]")
                # Else do nothing

                # Looking for allocated functions and add them to the functional element
                if len(row[util.CSV_FUNCTION_LIST_IDX]) > 0:
                    csv_function_id_list = row[util.CSV_FUNCTION_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_function_id in csv_function_id_list:
                        fun_elem.add_allocated_function(csv_function_id)
                        Logger.set_debug(__name__, f"Function [{csv_function_id}]"
                                                   f" is allocated to "
                                                   f"functional element [{fun_elem.id}, {fun_elem.name}]")
                # Else do nothing

                # Looking for exposed interface and add them to the functional element
                if len(row[util.CSV_INTERFACE_LIST_IDX]) > 0:
                    csv_interface_id_list = row[util.CSV_INTERFACE_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_interface_id in csv_interface_id_list:
                        fun_elem.add_exposed_interface(csv_interface_id)
                        Logger.set_debug(__name__, f"Functional interface [{csv_interface_id}]"
                                                   f" is exposed by "
                                                   f"functional element [{fun_elem.id}, {fun_elem.name}]")
                # Else do nothing

                # Looking for allocated requirements and add them to the functional element
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        fun_elem.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"functional element [{fun_elem.id}, {fun_elem.name}]")
                # Else do nothing
            # Else do nothing

        # Loop to set parent and child relationship
        util.update_parental_relationship(parent_list, functional_element_list)

        # Loop to update derived functional elements according to their ids
        util.update_derived_object(functional_element_list)

        return functional_element_list

    def parse_view_list(self):
        """Parse CSV view list
        @return view list
        """
        view_list = set()
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_VIEW:
                # Instantiate view and add them to a list
                view = datamodel.View(uid=util.check_uuid4(row[util.CSV_ID_IDX]),
                                      name=row[util.CSV_NAME_IDX],
                                      v_type=row[util.CSV_EXTENSION_IDX])

                view_list.add(view)

                # Looking for allocated items and add them to the view
                if len(row[util.CSV_VIEW_ELEMENT_LIST_IDX]) > 0:
                    csv_element_id_list = row[util.CSV_VIEW_ELEMENT_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_element_id in csv_element_id_list:
                        view.add_allocated_item(csv_element_id)
                        Logger.set_debug(__name__, f"Element [{csv_element_id}]"
                                                   f" is allocated to "
                                                   f"view [{view.id}, {view.name}]")
                # Else do nothing
            # Else do nothing

        return view_list

    def parse_attribute_list(self):
        """Parse CSV attribute list
        @return attribute list
        """
        attribute_list = set()
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_ATTRIBUTE:
                # Instantiate Attribute and add them to a list
                attribute = datamodel.Attribute(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                p_name=row[util.CSV_NAME_IDX],
                                                p_alias=row[util.CSV_ALIAS_IDX],
                                                p_type=row[util.CSV_EXTENSION_IDX])

                attribute_list.add(attribute)

                # Looking for described items and add them to the attribute
                if len(row[util.CSV_DESCRIBED_ELEMENT_LIST_IDX]) > 0:
                    csv_element_list = row[util.CSV_DESCRIBED_ELEMENT_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_element in csv_element_list:
                        csv_element_attribute = csv_element.split(util.CSV_MEMBER_ATTRIBUTE_SPLIT)
                        attribute.add_described_item((csv_element_attribute[0],
                                                      csv_element_attribute[1]))
                        Logger.set_debug(__name__, f"Element [{csv_element_attribute[0]}] "
                                                   f"is described by "
                                                   f"attribute [{attribute.id}, {attribute.name}] "
                                                   f"with the value : {csv_element_attribute[1]}")
                # Else do nothing

                # Looking for allocated requirements and add them to the functional interface
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        attribute.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"attribute [{attribute.id}, {attribute.name}]")
                # Else do nothing
            # Else do nothing

        return attribute_list

    def parse_functional_interface_list(self):
        """Parse CSV functional interface list
        @return functional interface list
        """
        functional_interface_list = set()
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_FUN_INTF:
                # Instantiate fun_inter and add them to a list
                if len(row[util.CSV_DERIVED_IDX]) > 0:
                    fun_inter = datamodel.FunctionalInterface(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                              p_name=row[util.CSV_NAME_IDX],
                                                              p_alias=row[util.CSV_ALIAS_IDX],
                                                              p_type=row[util.CSV_EXTENSION_IDX],
                                                              p_derived=row[util.CSV_DERIVED_IDX])
                else:
                    fun_inter = datamodel.FunctionalInterface(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                              p_name=row[util.CSV_NAME_IDX],
                                                              p_alias=row[util.CSV_ALIAS_IDX],
                                                              p_type=row[util.CSV_EXTENSION_IDX])

                functional_interface_list.add(fun_inter)

                # Looking for allocated data and add them to the fun inter
                if len(row[util.CSV_DATA_LIST_IDX]) > 0:
                    csv_allocated_data_id_list = row[util.CSV_DATA_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_data_id in csv_allocated_data_id_list:
                        fun_inter.add_allocated_data(csv_allocated_data_id)
                        Logger.set_debug(__name__, f"Data [{csv_allocated_data_id}]"
                                                   f" is allocated to "
                                                   f"functional interface [{fun_inter.id}, {fun_inter.name}]")
                # Else do nothing

                # Looking for allocated requirements and add them to the functional interface
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        fun_inter.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"functional interface [{fun_inter.id}, {fun_inter.name}]")
                # Else do nothing
            # Else do nothing

        # Loop to update derived functional elements according to their ids
        util.update_derived_object(functional_interface_list)

        return functional_interface_list

    def parse_physical_element_list(self):
        """Parse CSV physical element list
        @return physical element list
        """
        physical_element_list = set()
        parent_list = {}
        functional_interface_list = set()
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_PHY_ELEM:
                # Instantiate functional element and add them to a list
                if len(row[util.CSV_DERIVED_IDX]) > 0:
                    phy_elem = datamodel.PhysicalElement(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                         p_name=row[util.CSV_NAME_IDX],
                                                         p_alias=row[util.CSV_ALIAS_IDX],
                                                         p_type=row[util.CSV_EXTENSION_IDX],
                                                         p_derived=row[util.CSV_DERIVED_IDX])
                else:
                    phy_elem = datamodel.PhysicalElement(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                         p_name=row[util.CSV_NAME_IDX],
                                                         p_alias=row[util.CSV_ALIAS_IDX],
                                                         p_type=row[util.CSV_EXTENSION_IDX])

                physical_element_list.add(phy_elem)

                # Looking for "physicalPart" i.e child and create a list
                if len(row[util.CSV_CHILDREN_LIST_IDX]) > 0:
                    csv_part_id_list = row[util.CSV_CHILDREN_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_part_id in csv_part_id_list:
                        parent_list[csv_part_id] = phy_elem.id
                # Else do nothing

                # Looking for allocated activities and add them to the physical element
                if len(row[util.CSV_ACTIVITY_LIST_IDX]) > 0:
                    csv_activity_id_list = row[util.CSV_ACTIVITY_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_activity_id in csv_activity_id_list:
                        phy_elem.add_allocated_activity(csv_activity_id)
                        Logger.set_debug(__name__, f"Activity [{csv_activity_id}]"
                                                   f" is allocated to "
                                                   f"physical element [{phy_elem.id}, {phy_elem.name}]")
                # Else do nothing

                # Looking for allocated functional elements and add them to the physical element
                if len(row[util.CSV_FUN_ELEM_LIST_IDX]) > 0:
                    csv_fun_elem_id_list = row[util.CSV_FUN_ELEM_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_fun_elem_id in csv_fun_elem_id_list:
                        phy_elem.add_allocated_fun_elem(csv_fun_elem_id)
                        Logger.set_debug(__name__, f"Functional element [{csv_fun_elem_id}]"
                                                   f" is allocated to "
                                                   f"physical element [{phy_elem.id}, {phy_elem.name}]")
                # Else do nothing

                # Looking for exposed interface and add them to the functional element
                if len(row[util.CSV_INTERFACE_LIST_IDX]) > 0:
                    csv_interface_id_list = row[util.CSV_INTERFACE_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_interface_id in csv_interface_id_list:
                        phy_elem.add_exposed_interface(csv_interface_id)
                        Logger.set_debug(__name__, f"Physical interface [{csv_interface_id}]"
                                                   f" is exposed by "
                                                   f"physical element [{phy_elem.id}, {phy_elem.name}]")
                # Else do nothing

                # Looking for allocated requirements and add them to the physical element
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        phy_elem.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"physical element [{phy_elem.id}, {phy_elem.name}]")
                # Else do nothing
            # Else do nothing

        # Loop to set parent and child relationship
        util.update_parental_relationship(parent_list, physical_element_list)

        # Loop to update derived functions according to their ids
        util.update_derived_object(physical_element_list)

        return physical_element_list

    def parse_physical_interface_list(self):
        """Parse CSV physical interface list
        @return physical interface list
        """
        physical_interface_list = set()
        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_PHY_INTF:
                # Instantiate phy_inter and add them to a list
                if len(row[util.CSV_DERIVED_IDX]) > 0:
                    phy_inter = datamodel.PhysicalInterface(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                            p_name=row[util.CSV_NAME_IDX],
                                                            p_alias=row[util.CSV_ALIAS_IDX],
                                                            p_type=row[util.CSV_EXTENSION_IDX],
                                                            p_derived=row[util.CSV_DERIVED_IDX])
                else:
                    phy_inter = datamodel.PhysicalInterface(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                            p_name=row[util.CSV_NAME_IDX],
                                                            p_alias=row[util.CSV_ALIAS_IDX],
                                                            p_type=row[util.CSV_EXTENSION_IDX])

                physical_interface_list.add(phy_inter)

                # Looking for allocated fun_inter and add them to the phy inter
                if len(row[util.CSV_INTERFACE_LIST_IDX]) > 0:
                    csv_interface_id_list = row[util.CSV_INTERFACE_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_interface_id in csv_interface_id_list:
                        phy_inter.add_allocated_fun_inter(csv_interface_id)
                        Logger.set_debug(__name__, f"Functional interface [{csv_interface_id}] "
                                                   f"is allocated to "
                                                   f"physical interface [{phy_inter.id}, {phy_inter.name}]")
                # Else do nothing

                # Looking for allocated requirements and add them to the physical interface
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        phy_inter.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"physical interface [{phy_inter.id}, {phy_inter.name}]")
                # Else do nothing
            # Else do nothing

        # Loop to update derived functions according to their ids
        util.update_derived_object(physical_interface_list)

        return physical_interface_list

    def parse_requirement_list(self, p_data_column=0):
        """Parse CSV requirement list
        @param[in] p_data_column : CSV column number where requirements are defined
        @return requirement list
        """
        requirement_list = set()
        parent_list = {}
        for row in self.array:
            if p_data_column > 0:
                if len(row) > p_data_column:
                    if len(re.compile(r'([^. |\n][^.|\n]*) shall ([^.|\n]*)', re.IGNORECASE).split(row[p_data_column])) > 1:
                        # Instantiate Requirement and add them to a list
                        requirement = datamodel.Requirement(p_id=util.check_uuid4(row[0]),
                                                            p_name=row[1])

                        requirement_list.add(requirement)

                        # Looking for requirement description
                        requirement.set_description(row[p_data_column])
                    else:
                        Logger.set_warning(__name__,
                                       f"Following description is not a requirement: {row[p_data_column]}")
                # Else do nothing
            elif row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_REQ:
                # Instantiate Requirement and add them to a list
                requirement = datamodel.Requirement(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                    p_name=row[util.CSV_NAME_IDX],
                                                    p_alias=row[util.CSV_ALIAS_IDX],
                                                    p_type=row[util.CSV_EXTENSION_IDX])

                requirement_list.add(requirement)

                # Looking for requirement description
                requirement.set_description(row[util.CSV_DESCRIPTION_LIST_IDX])

                # Looking for requirement child
                if len(row[util.CSV_CHILDREN_LIST_IDX]) > 0:
                    csv_part_id_list = row[util.CSV_CHILDREN_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_part_id in csv_part_id_list:
                        parent_list[csv_part_id] = requirement.id
                # Else do nothing
            # Else do nothing

        # Loop to set parent and child relationship
        util.update_parental_relationship(parent_list, requirement_list)

        return requirement_list

    def parse_data_list(self):
        """Parse CSV data list
        @return data list, producer function list, consumer function list
        """
        data_list = set()
        consumer_function_list = []
        producer_function_list = []

        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_DATA:
                # Instantiate data and add it to a list
                data = datamodel.Data(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                      p_name=row[util.CSV_NAME_IDX],
                                      p_type=row[util.CSV_EXTENSION_IDX])
                data_list.add(data)

                # Looking for allocated requirements and add them to the data
                if len(row[util.CSV_REQ_LIST_IDX]) > 0:
                    csv_allocated_requirement_id_list = row[util.CSV_REQ_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_allocated_requirement_id in csv_allocated_requirement_id_list:
                        data.add_allocated_requirement(csv_allocated_requirement_id)

                        Logger.set_debug(__name__, f"Requirement [{csv_allocated_requirement_id}]"
                                                   f" is satisfied by "
                                                   f"data [{data.id}, {data.name}]")
                # Else do nothing

                # looking for all elements with tag "consumer" and create a list [data, consumer_function]
                if len(row[util.CSV_CONSUMER_LIST_IDX]) > 0:
                    csv_consumer_list = row[util.CSV_CONSUMER_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_consumer in csv_consumer_list:
                        csv_consumer_attribute = csv_consumer.split(util.CSV_MEMBER_ATTRIBUTE_SPLIT)
                        for function in self.csv_dict['csv_function_list']:
                            if csv_consumer_attribute[0] == function.id:
                                consumer_function_list.append([data, function])
                                Logger.set_debug(__name__, f"Data [{data.id}, {data.name}] "
                                                           f"is consumed by "
                                                           f"data [{function.id}, {function.name}]")

                                if csv_consumer_attribute[1] != 'none':
                                    function.set_input_role(data.name)
                                # Avoid to reset the input role once already set
                                elif function.input_role is None:
                                    function.set_input_role(None)
                # Else do nothing

                # looking for all elements with tag "producer" and create a list [data, producer_function]
                if len(row[util.CSV_PRODUCER_LIST_IDX]) > 0:
                    csv_producer_id_list = row[util.CSV_PRODUCER_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_producer_id in csv_producer_id_list:
                        for function in self.csv_dict['csv_function_list']:
                            if csv_producer_id == function.id:
                                producer_function_list.append([data, function])
                                Logger.set_debug(__name__, f"Data [{data.id}, {data.name}] "
                                                           f"is produced by "
                                                           f"function [{function.id}, {function.name}]")
                # Else do nothing

        # Loop on the data_list once created to find the predecessor and add it to list
        for object_data in data_list:
            for row in self.array:
                if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_DATA:
                    if row[util.CSV_ID_IDX] == object_data.id:
                        # looking for all elements with tag "predecessor"
                        if len(row[util.CSV_PREDECESSOR_LIST_IDX]) > 0:
                            csv_predecessor_id_list = row[util.CSV_PREDECESSOR_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                            for csv_predecessor_id in csv_predecessor_id_list:
                                for data in data_list:
                                    if csv_predecessor_id == data.id:
                                        object_data.add_predecessor(data)

                                        Logger.set_debug(__name__, f"Data [{data.id, data.name}]"
                                                                   f" is predecessor of "
                                                                   f"data [{object_data.id, object_data.name}]")
                        # Else do nothing

        return data_list, producer_function_list, consumer_function_list

    def parse_information_list(self):
        """Parse CSV information list
        @return information list, producer activity list, consumer activity list
        """
        information_list = set()
        consumer_activity_list = []
        producer_activity_list = []

        for row in self.array:
            if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_DATA:
                # Instantiate information and add it to a list
                information = datamodel.Information(p_id=util.check_uuid4(row[util.CSV_ID_IDX]),
                                                    p_name=row[util.CSV_NAME_IDX],
                                                    p_type=row[util.CSV_EXTENSION_IDX])
                information_list.add(information)

                # looking for all elements with tag "consumer" and create a list [information, consumer_activity]
                if len(row[util.CSV_CONSUMER_LIST_IDX]) > 0:
                    csv_consumer_list = row[util.CSV_CONSUMER_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_consumer in csv_consumer_list:
                        csv_consumer_attribute = csv_consumer.split(util.CSV_MEMBER_ATTRIBUTE_SPLIT)
                        for activity in self.csv_dict['csv_activity_list']:
                            if csv_consumer_attribute[0] == activity.id:
                                consumer_activity_list.append([information, activity])
                                Logger.set_debug(__name__, f"Information [{information.id}, {information.name}] "
                                                           f"is consumed by "
                                                           f"activity [{activity.id}, {activity.name}]")
                # Else do nothing

                # looking for all elements with tag "producer" and create a list [information, producer_function]
                if len(row[util.CSV_PRODUCER_LIST_IDX]) > 0:
                    csv_producer_id_list = row[util.CSV_PRODUCER_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                    for csv_producer_id in csv_producer_id_list:
                        for activity in self.csv_dict['csv_function_list']:
                            if csv_producer_id == activity.id:
                                producer_activity_list.append([information, activity])
                                Logger.set_debug(__name__, f"Data [{information.id}, {information.name}] "
                                                           f"is produced by "
                                                           f"activity [{activity.id}, {activity.name}]")
                # Else do nothing

        # Loop on the data_list once created to find the predecessor and add it to list
        for object_data in information_list:
            for row in self.array:
                if row[util.CSV_BASE_IDX] == util.CSV_BASE_TAG_DATA:
                    if row[util.CSV_ID_IDX] == object_data.id:
                        # looking for all elements with tag "predecessor"
                        if len(row[util.CSV_PREDECESSOR_LIST_IDX]) > 0:
                            csv_predecessor_id_list = row[util.CSV_PREDECESSOR_LIST_IDX].split(util.CSV_MEMBER_SPLIT)
                            for csv_predecessor_id in csv_predecessor_id_list:
                                for information in information_list:
                                    if csv_predecessor_id == information.id:
                                        object_data.add_predecessor(information)

                                        Logger.set_debug(__name__, f"Information [{information.id, information.name}]"
                                                                   f" is predecessor of "
                                                                   f"information [{object_data.id, object_data.name}]")
                        # Else do nothing

        return information_list, producer_activity_list, consumer_activity_list

    def update_object_type(self):
        """Update objects in the dictionary with their types.
        @return None
        """
        # Following lists does not contain any type definition
        unwanted_csv_list = ('csv_type_list', 'csv_consumer_function_list', 'csv_producer_function_list',
                             'csv_consumer_activity_list', 'csv_producer_activity_list')
        for key, csv_list in self.csv_dict.items():
            if key not in unwanted_csv_list:
                for obj in csv_list:
                    try:
                        # Base type are defined with their names
                        obj.type = datamodel.BaseType[obj.type.upper().replace(" ", "_")]
                    except KeyError:
                        # Extended types are defined in csv_type_list with their ids
                        is_found = False
                        for type_obj in self.csv_dict['csv_type_list']:
                            if obj.type == type_obj.id:
                                obj.type = type_obj
                                is_found = True
                                break

                        if not is_found:
                            Logger.set_error(__name__,
                                             f"Unknown type {obj.type} found when parsing csv")
