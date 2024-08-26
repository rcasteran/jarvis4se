"""@defgroup xml_adapter
Module for 3SE xml parsing and writing
"""
# Libraries


# Modules


# Constants
XML_DICT_KEY_0_DATA_LIST = 'xml_data_list'
XML_DICT_KEY_1_FUNCTION_LIST = 'xml_function_list'
XML_DICT_KEY_2_FUN_ELEM_LIST = 'xml_fun_elem_list'
XML_DICT_KEY_3_FUN_INTF_LIST = 'xml_fun_inter_list'
XML_DICT_KEY_4_PHY_ELEM_LIST = 'xml_phy_elem_list'
XML_DICT_KEY_5_PHY_INTF_LIST = 'xml_phy_inter_list'
XML_DICT_KEY_6_STATE_LIST = 'xml_state_list'
XML_DICT_KEY_7_TRANSITION_LIST = 'xml_transition_list'
XML_DICT_KEY_8_REQUIREMENT_LIST = 'xml_requirement_list'
XML_DICT_KEY_9_ATTRIBUTE_LIST = 'xml_attribute_list'
XML_DICT_KEY_10_VIEW_LIST = 'xml_view_list'
XML_DICT_KEY_11_TYPE_LIST = 'xml_type_list'
XML_DICT_KEY_12_FUN_CONS_LIST = 'xml_consumer_function_list'
XML_DICT_KEY_13_FUN_PROD_LIST = 'xml_producer_function_list'


# Functions
def normalize_xml_string(p_str):
    # Using XML character encoding rather than escape string
    return str(p_str).replace("&", "#38;").replace("'", "#39;").replace("<", "#60;").replace(">", "#62;")


def denormalize_xml_string(p_str):
    return str(p_str).replace("#38;", "&").replace("#39;", "'").replace("#60;", "<").replace("#62;", ">")
