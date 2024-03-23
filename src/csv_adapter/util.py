"""@defgroup csv_adapter
Module for 3SE csv parsing and writing
"""

# Libraries
import math
import uuid

# Modules
from tools import Logger

# Constants
CSV_ID_IDX = 0
CSV_BASE_IDX = 1
CSV_BASE_TAG_TYPE = "type"
CSV_BASE_TAG_FUNCTION = "function"
CSV_BASE_TAG_STATE = "state"
CSV_BASE_TAG_TRANSITION = "transition"
CSV_BASE_TAG_FUN_ELEM = "functional element"
CSV_BASE_TAG_VIEW = "view"
CSV_BASE_TAG_ATTRIBUTE = "attribute"
CSV_BASE_TAG_FUN_INTF = "functional interface"
CSV_BASE_TAG_PHY_ELEM = "physical element"
CSV_BASE_TAG_PHY_INTF = "physical interface"
CSV_BASE_TAG_REQ = "requirement"
CSV_BASE_TAG_DATA = "data"
CSV_EXTENSION_IDX = 2
CSV_NAME_IDX = 3
CSV_ALIAS_IDX = 4
CSV_DESCRIPTION_LIST_IDX = 5
CSV_DERIVED_IDX = 6
CSV_SOURCE_IDX = 7
CSV_DESTINATION_IDX = 8
CSV_CONSUMER_LIST_IDX = 9
CSV_PRODUCER_LIST_IDX = 10
CSV_PREDECESSOR_LIST_IDX = 11
CSV_CHILDREN_LIST_IDX = 12
CSV_DATA_LIST_IDX = 13
CSV_CONDITION_LIST_IDX = 14
CSV_FUNCTION_LIST_IDX = 15
CSV_STATE_LIST_IDX = 16
CSV_INTERFACE_LIST_IDX = 17
CSV_FUN_ELEM_LIST_IDX = 18
CSV_DESCRIBED_ELEMENT_LIST_IDX = 19
CSV_VIEW_ELEMENT_LIST_IDX = 20
CSV_REQ_LIST_IDX = 21


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


def check_uuid4(p_uuid4):
    uuid_obj = p_uuid4
    try:
        identifier_length = int(math.log10(int(p_uuid4)))+1
        if identifier_length != 10:
            Logger.set_warning(__name__,
                               f'Identifier "{p_uuid4}" is not a valid uuid4 (length of {identifier_length} digits) '
                               f'and will be replaced')
            identifier = uuid.uuid4()
            uuid_obj = str(identifier.int)[:10]
        # Else do nothing
    except ValueError:
        if p_uuid4 is not None:
            Logger.set_warning(__name__,
                               f'Identifier "{p_uuid4}" is not a valid uuid4 and will be replaced')

        identifier = uuid.uuid4()
        uuid_obj = str(identifier.int)[:10]

    return uuid_obj
