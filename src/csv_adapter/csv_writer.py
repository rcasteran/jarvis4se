"""@defgroup csv_adapter
Module for 3SE csv parsing and writing
"""

# Libraries
import csv

# Modules
import datamodel
from . import util
from tools import Logger


class CsvWriter3SE:
    """@ingroup csv_adapter
    @anchor CsvWriter3SE
    3SE csv writer
    """

    def __init__(self, output_filename):
        """
        @var write_list
        List of write functions per data type

        @var file
        Reference to the XML file to be written
        """
        self.write_list = {
            0: self.write_function,
            1: self.write_data,
            2: self.write_data_consumer,
            3: self.write_data_producer,
            4: self.write_state,
            5: self.write_transition,
            6: self.write_functional_element,
            7: self.write_view,
            8: self.write_attribute,
            9: self.write_functional_interface,
            10: self.write_physical_element,
            11: self.write_physical_interface,
            12: self.write_type_element,
            13: self.write_requirement
        }

        self.file = output_filename

    def write_file(self, **kwargs):
        """Write the CSV file according the dictionaries
        @param[in] output_filename : CSV file name
        @param[in] **kwargs : dictionaries
        @return CSV dictionary
        """
        xml_dictionary_list = {
            0: kwargs['xml_function_list'],
            1: kwargs['xml_data_list'],
            2: kwargs['xml_consumer_function_list'],
            3: kwargs['xml_producer_function_list'],
            4: kwargs['xml_state_list'],
            5: kwargs['xml_transition_list'],
            6: kwargs['xml_fun_elem_list'],
            7: kwargs['xml_view_list'],
            8: kwargs['xml_attribute_list'],
            9: kwargs['xml_fun_inter_list'],
            10: kwargs['xml_phy_elem_list'],
            11: kwargs['xml_phy_inter_list'],
            12: kwargs['xml_type_list'],
            13: kwargs['xml_requirement_list']
        }

        try:
            # Write the CSV file
            with open(self.file, 'w', newline='', encoding='utf8') as file_writer:
                writer = csv.writer(file_writer, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')

                writer.writerow(['id',
                                 'base type',
                                 'extended type',
                                 'name',
                                 'alias',
                                 'description',
                                 'derived',
                                 'source',
                                 'dest',
                                 'consumer list',
                                 'producer list',
                                 'predecessor list',
                                 'children list',
                                 'data list',
                                 'condition list',
                                 'function list',
                                 'state list',
                                 'interface list',
                                 'functional element list',
                                 'described element list',
                                 'view element list'
                                 'requirement list'])

                array = []
                for i in range(0, len(xml_dictionary_list)):
                    call = self.write_list.get(i)
                    array = call(array, xml_dictionary_list.get(i))

                for row in array:
                    writer.writerow(row)

            Logger.set_info(__name__, f"{self.file} created")
        except OSError:
            Logger.set_error(__name__, f"Unable to write CSV file:{self.file}")

    @staticmethod
    def check_object_type(obj):
        """Check object type against 3SE base types
        @param[in] obj : object reference
        @return object type to be written in XML file
        """
        if isinstance(obj, datamodel.BaseType):
            # Object is a basic 3SE type
            type_str = str(obj).lower()
        else:
            type_str = obj.id

        return type_str

    def write_function(self, array, function_list):
        """Write functions from list of functions
        @param[in] array : CSV object array
        @param[in] function_list : list of functions
        @return updated CSV object array
        """
        for function in function_list:
            children_id_list = ''
            for function_child in function.child_list:
                children_id_list += function_child.id + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in function.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            if function.derived is not None:
                function_derived = function.derived.id
            else:
                function_derived = ''

            array.append([function.id,
                          util.CSV_BASE_TAG_FUNCTION,
                          self.check_object_type(function.type),
                          function.name,
                          function.alias,
                          '',  # Description list
                          function_derived,
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          children_id_list[:-1],  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_data(self, array, data_list):
        """Write data from list of data
        @param[in] array : CSV object array
        @param[in] data_list : list of data
        @return updated CSV object array
        """
        for data in data_list:
            predecessor_id_list = ''
            for predecessor in data.predecessor_list:
                predecessor_id_list += predecessor.id + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in data.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            array.append([data.id,
                          util.CSV_BASE_TAG_DATA,
                          self.check_object_type(data.type),
                          data.name,
                          '',  # Alias
                          '',  # Description list
                          '',  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          predecessor_id_list[:-1],  # Predecessor list
                          '',  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    @staticmethod
    def write_data_consumer(array, consumer_list):
        """Write consumers by list [data_name, function]
        @param[in] array : CSV object array
        @param[in] consumer_list : list of consumers
        @return updated CSV object array
        """
        for consumer in consumer_list:
            for row in array:
                if row[util.CSV_NAME_IDX] == consumer[0].name:
                    if len(row[util.CSV_CONSUMER_LIST_IDX]) > 0:
                        if consumer[1].operand is not None:
                            row[util.CSV_CONSUMER_LIST_IDX] += util.CSV_MEMBER_SPLIT + consumer[1].id \
                                                               + util.CSV_MEMBER_ATTRIBUTE_SPLIT + consumer[1].operand
                        else:
                            row[util.CSV_CONSUMER_LIST_IDX] += util.CSV_MEMBER_SPLIT + consumer[1].id \
                                                               + util.CSV_MEMBER_ATTRIBUTE_SPLIT + "none"
                    else:
                        if consumer[1].operand is not None:
                            row[util.CSV_CONSUMER_LIST_IDX] += consumer[1].id + util.CSV_MEMBER_ATTRIBUTE_SPLIT \
                                                               + consumer[1].operand
                        else:
                            row[util.CSV_CONSUMER_LIST_IDX] += consumer[1].id + util.CSV_MEMBER_ATTRIBUTE_SPLIT \
                                                               + "none"
                # Else do nothing

        return array

    @staticmethod
    def write_data_producer(array, producer_list):
        """Write producers by list [data_name, function]
        @param[in] array : CSV object array
        @param[in] producer_list : list of producers
        @return updated CSV object array
        """
        for producer in producer_list:
            for row in array:
                if row[util.CSV_NAME_IDX] == producer[0].name:
                    if len(row[util.CSV_PRODUCER_LIST_IDX]) > 0:
                        row[util.CSV_PRODUCER_LIST_IDX] += util.CSV_MEMBER_SPLIT + producer[1].id
                    else:
                        row[util.CSV_PRODUCER_LIST_IDX] += producer[1].id
                # Else do nothing

        return array

    def write_state(self, array, state_list):
        """Write states from list of states
        @param[in] array : CSV object array
        @param[in] state_list : list of states
        @return updated CSV object array
        """
        for state in state_list:
            children_id_list = ''
            for state_child in state.child_list:
                children_id_list += state_child.id + util.CSV_MEMBER_SPLIT

            allocated_function_id_list = ''
            for allocated_function_id in state.allocated_function_list:
                allocated_function_id_list += allocated_function_id + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in state.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            array.append([state.id,
                          util.CSV_BASE_TAG_STATE,
                          self.check_object_type(state.type),
                          state.name,
                          state.alias,
                          '',  # Description list
                          '',  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          children_id_list[:-1],  # Children list
                          '',  # Data list
                          '',  # Condition list
                          allocated_function_id_list[:-1],  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_transition(self, array, transition_list):
        """Write transitions from list of transitions
        @param[in] array : CSV object array
        @param[in] transition_list : list of transitions
        @return updated CSV object array
        """
        for transition in transition_list:
            condition_text_list = ''
            for condition_text in transition.condition_list:
                condition_text_list += condition_text + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in transition.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            array.append([transition.id,
                          util.CSV_BASE_TAG_TRANSITION,
                          self.check_object_type(transition.type),
                          transition.name,
                          transition.alias,
                          '',  # Description list
                          '',  # Derived
                          transition.source,  # Source
                          transition.destination,  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          '',  # Children list
                          '',  # Data list
                          condition_text_list[:-1],  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_functional_element(self, array, element_list):
        """Write functional elements from list of functional elements
        @param[in] array : CSV object array
        @param[in] element_list : list of functional elements
        @return updated CSV object array
        """
        for element in element_list:
            children_id_list = ''
            for element_child in element.child_list:
                children_id_list += element_child.id + util.CSV_MEMBER_SPLIT

            allocated_state_id_list = ''
            for allocated_state_id in element.allocated_state_list:
                allocated_state_id_list += allocated_state_id + util.CSV_MEMBER_SPLIT

            allocated_function_id_list = ''
            for allocated_function_id in element.allocated_function_list:
                allocated_function_id_list += allocated_function_id + util.CSV_MEMBER_SPLIT

            exposed_interface_id_list = ''
            for exposed_interface_id in element.exposed_interface_list:
                exposed_interface_id_list += exposed_interface_id + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in element.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            if element.derived is not None:
                element_derived = element.derived.id
            else:
                element_derived = ''

            array.append([element.id,
                          util.CSV_BASE_TAG_FUN_ELEM,
                          self.check_object_type(element.type),
                          element.name,
                          element.alias,
                          '',  # Description list
                          element_derived,  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          children_id_list[:-1],  # Children list
                          '',  # Data list
                          '',  # Condition list
                          allocated_function_id_list[:-1],  # Function list
                          allocated_state_id_list[:-1],  # State list
                          exposed_interface_id_list[:-1],  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_view(self, array, view_list):
        """Write views from list of views
        @param[in] array : CSV object array
        @param[in] view_list : list of views
        @return updated CSV object array
        """
        for view in view_list:
            allocated_element_id_list = ''
            for allocated_element_id in view.allocated_item_list:
                allocated_element_id_list += allocated_element_id + util.CSV_MEMBER_SPLIT

            array.append([view.id,
                          util.CSV_BASE_TAG_VIEW,
                          self.check_object_type(view.type),
                          view.name,
                          '',  # Alias
                          '',  # Description list
                          '',  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          '',  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          allocated_element_id_list[:-1],  # View element list
                          ''  # Requirement list
                          ])

        return array

    def write_attribute(self, array, attribute_list):
        """Write attributes from list of attributes
        @param[in] array : CSV object array
        @param[in] attribute_list : list of attributes
        @return updated CSV object array
        """
        for attribute in attribute_list:
            described_element_list = ''
            for described_element in attribute.described_item_list:
                described_element_list += described_element[0] + util.CSV_MEMBER_ATTRIBUTE_SPLIT \
                                          + described_element[1] + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in attribute.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            array.append([attribute.id,
                          util.CSV_BASE_TAG_ATTRIBUTE,
                          self.check_object_type(attribute.type),
                          attribute.name,
                          attribute.alias,  # Alias
                          '',  # Description list
                          '',  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          '',  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          described_element_list[:-1],  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_functional_interface(self, array, interface_list):
        """Write functional interfaces from list of functional interfaces
        @param[in] array : CSV object array
        @param[in] interface_list : list of functional interfaces
        @return updated CSV object array
        """
        for interface in interface_list:
            allocated_data_id_list = ''
            for allocated_data_id in interface.allocated_data_list:
                allocated_data_id_list += allocated_data_id + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in interface.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            if interface.derived is not None:
                interface_derived = interface.derived.id
            else:
                interface_derived = ''

            array.append([interface.id,
                          util.CSV_BASE_TAG_FUN_INTF,
                          self.check_object_type(interface.type),
                          interface.name,
                          interface.alias,  # Alias
                          '',  # Description list
                          interface_derived,  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          '',  # Children list
                          allocated_data_id_list[:-1],  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_physical_element(self, array, element_list):
        """Write physical elements from list of physical elements
        @param[in] array : CSV object array
        @param[in] element_list : list of physical elements
        @return updated CSV object array
        """
        for element in element_list:
            children_id_list = ''
            for element_child in element.child_list:
                children_id_list += element_child.id + util.CSV_MEMBER_SPLIT

            allocated_fun_elem_id_list = ''
            for allocated_fun_elem_id in element.allocated_fun_elem_list:
                allocated_fun_elem_id_list += allocated_fun_elem_id + util.CSV_MEMBER_SPLIT

            exposed_interface_id_list = ''
            for exposed_interface_id in element.exposed_interface_list:
                exposed_interface_id_list += exposed_interface_id + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in element.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            if element.derived is not None:
                element_derived = element.derived.id
            else:
                element_derived = ''

            array.append([element.id,
                          util.CSV_BASE_TAG_PHY_ELEM,
                          self.check_object_type(element.type),
                          element.name,
                          element.alias,
                          '',  # Description list
                          element_derived,  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          children_id_list[:-1],  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          exposed_interface_id_list[:-1],  # Interface list
                          allocated_fun_elem_id_list[:-1],  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_physical_interface(self, array, interface_list):
        """Write physical interfaces from list of physical interfaces
        @param[in] array : CSV object array
        @param[in] interface_list : list of physical interfaces
        @return updated CSV object array
        """
        for interface in interface_list:
            allocated_fun_intf_id_list = ''
            for allocated_fun_intf_id in interface.allocated_fun_inter_list:
                allocated_fun_intf_id_list += allocated_fun_intf_id + util.CSV_MEMBER_SPLIT

            allocated_requirement_id_list = ''
            for allocated_requirement_id in interface.allocated_req_list:
                allocated_requirement_id_list += allocated_requirement_id + util.CSV_MEMBER_SPLIT

            if interface.derived is not None:
                interface_derived = interface.derived.id
            else:
                interface_derived = ''

            array.append([interface.id,
                          util.CSV_BASE_TAG_PHY_INTF,
                          self.check_object_type(interface.type),
                          interface.name,
                          interface.alias,  # Alias
                          '',  # Description list
                          interface_derived,  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          '',  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          allocated_fun_intf_id_list[:-1],  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          allocated_requirement_id_list[:-1]  # Requirement list
                          ])

        return array

    def write_type_element(self, array, type_list):
        """Write types from list of types
        @param[in] array : CSV object array
        @param[in] type_list : list of types
        @return updated CSV object array
        """
        for type_element in type_list:
            array.append([type_element.id,
                          util.CSV_BASE_TAG_TYPE,
                          self.check_object_type(type_element.base),
                          type_element.name,
                          type_element.alias,  # Alias
                          '',  # Description list
                          '',  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          '',  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          ''  # Requirement list
                          ])

        return array

    def write_requirement(self, array, requirement_list):
        """Write requirements from list of requirements
        @param[in] array : CSV object array
        @param[in] requirement_list : list of requirements
        @return updated CSV object array
        """
        for requirement in requirement_list:
            children_id_list = ''
            for requirement_child in requirement.child_list:
                children_id_list += requirement_child.id + util.CSV_MEMBER_SPLIT

            array.append([requirement.id,
                          util.CSV_BASE_TAG_REQ,
                          self.check_object_type(requirement.type),
                          requirement.name,
                          requirement.alias,  # Alias
                          requirement.description,  # Description list
                          '',  # Derived
                          '',  # Source
                          '',  # Dest
                          '',  # Consumer list
                          '',  # Producer list
                          '',  # Predecessor list
                          children_id_list[:-1],  # Children list
                          '',  # Data list
                          '',  # Condition list
                          '',  # Function list
                          '',  # State list
                          '',  # Interface list
                          '',  # Functional element list
                          '',  # Described element list
                          '',  # View element list
                          ''  # Requirement list
                          ])

        return array
