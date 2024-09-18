""" @defgroup query
Jarvis query module
"""
# Libraries


# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from jarvis.orchestrator import orchestrator_object


def query_object_name_in_list(p_object_list):
    return orchestrator_object.check_object_name_in_list(p_object_list)


def query_object_by_name(p_obj_name_str, **kwargs):
    return orchestrator_object.retrieve_object_by_name(p_obj_name_str, **kwargs)


def query_object_type(p_object, **kwargs):
    if isinstance(p_object.type, datamodel.BaseType):
        object_type = p_object.type
    else:
        _, object_type = orchestrator_object.retrieve_type(p_object.type.name, True, **kwargs)

    return object_type


def query_object_children_recursively(p_object, p_object_list=None, p_parent_child_dict=None, p_level_count=None,
                                      p_requested_level=None):
    return orchestrator_object.retrieve_object_children_recursively(p_object, p_object_list, p_parent_child_dict,
                                                                    p_level_count, p_requested_level)


def query_object_is_not_family(p_object_a, p_object_b):
    return orchestrator_object.check_object_is_not_family(p_object_a, p_object_b)


def query_object_attribute_properties_list(p_object, **kwargs):
    xml_attribute_list = kwargs[XML_DICT_KEY_9_ATTRIBUTE_LIST]
    attribute_properties_list = []

    for xml_attribute in xml_attribute_list:
        for xml_described_item in xml_attribute.described_item_list:
            if xml_described_item[0] == p_object.id:
                attribute_properties_list.append([xml_attribute.name, xml_described_item[1]])
            # Else do nothing

    return attribute_properties_list


def query_object_is_parent_recursively(p_object_parent, p_object_child):
    return orchestrator_object.check_object_is_parent_recursively(p_object_parent, p_object_child)


def query_object_type_requirement_list(p_object, **kwargs):
    return orchestrator_object.retrieve_object_type_requirement_list(p_object, **kwargs)
