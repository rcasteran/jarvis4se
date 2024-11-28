"""@defgroup diagram
Jarvis diagram module
"""
# Libraries

# Modules
import plantuml_adapter
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_ATTRIBUTE_LIST, XML_DICT_KEY_11_VIEW_LIST, \
    XML_DICT_KEY_12_TYPE_LIST, XML_DICT_KEY_13_FUN_CONS_LIST, XML_DICT_KEY_14_FUN_PROD_LIST
from jarvis.query import query_object
from tools import Logger


def show_phy_elem_decomposition(phy_elem_str, xml_phy_elem_list, xml_attribute_list, xml_phy_inter_list):
    """@ingroup diagram
    @anchor show_phy_elem_decomposition
    Creates lists with desired objects for physical element decomposition, send them to plantuml_adapter.py
    and returns plantuml text
    @param[in] phy_elem_str: name of the physical element
    @param[in] xml_fun_elem_list: list of all physical elements
    @param[in] xml_attribute_list: list of all attributes
    @param[in] xml_fun_inter_list: list of all physical interfaces
    @return plantuml text
    """
    plantuml_text = None

    main_phy_elem = query_object.query_object_by_name(phy_elem_str, **{XML_DICT_KEY_4_PHY_ELEM_LIST: xml_phy_elem_list})
    if not main_phy_elem:
        return plantuml_text

    main_phy_elem.parent = None

    plantuml_text = plantuml_adapter.get_phy_elem_decomposition(main_phy_elem,
                                                                xml_phy_elem_list,
                                                                xml_attribute_list,
                                                                xml_phy_inter_list)
    Logger.set_info(__name__,
                    f"Decomposition Diagram for {phy_elem_str} generated")

    return plantuml_text
