# Libraries

# Modules
import datamodel
from xml_adapter import XmlDictKeyListForObjects
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from jarvis.orchestrator import orchestrator_object
from . import util


def query_object_name_in_list(p_object_list):
    """
    Method that returns a list with all object aliases/names from object's list

    """
    object_name_list = []
    # Create the xml [object_name (and object_alias)] list
    for obj in p_object_list:
        object_name_list.append(obj.name)
        try:
            if len(obj.alias) > 0:
                object_name_list.append(obj.alias)
        except AttributeError:
            # To avoid error when there is no alias attribute for the object
            pass

    return object_name_list


def query_object_name_in_dict(**kwargs):
    """Returns lists of objects with their names depending on kwargs"""
    whole_objects_name_list = [[] for _ in range(len(XmlDictKeyListForObjects))]
    for i in range(len(XmlDictKeyListForObjects)):
        if kwargs.get(XmlDictKeyListForObjects[i], False):
            whole_objects_name_list[i] = query_object_name_in_list(kwargs[XmlDictKeyListForObjects[i]])
        # Else do nothing

    return whole_objects_name_list


def query_object_by_name(p_obj_name_str, **kwargs):
    """
    Returns the desired object from object's string
    Args:
        p_obj_name_str ([object_string]): list of object's name from cell
        **kwargs: xml lists

    Returns:
        wanted_object : Function/State/Data/Fun_Elem/Transition/Fun_Inter
    """
    wanted_object = None
    whole_objects_name_list = query_object_name_in_dict(**kwargs)

    if any(p_obj_name_str in s for s in whole_objects_name_list):
        result = [False] * len(XmlDictKeyListForObjects)
        for i in range(len(XmlDictKeyListForObjects)):
            result[i] = any(a == p_obj_name_str for a in whole_objects_name_list[i])

        wanted_object = util.match_object(p_obj_name_str, result, p_xml_str_lists=XmlDictKeyListForObjects, **kwargs)
    # Else do nothing

    return wanted_object


def query_object_type(p_object, **kwargs):
    if isinstance(p_object.type, datamodel.BaseType):
        object_type = p_object.type
    else:
        _, object_type = orchestrator_object.retrieve_type(p_object.type.name, True, **kwargs)

    return object_type


def query_object_children_recursively(p_object, p_object_list=None, p_parent_child_dict=None, p_level_count=None,
                                      p_requested_level=None):
    if p_object_list is None:
        p_object_list = set()
    # Else do nothing

    if p_parent_child_dict is None:
        p_parent_child_dict = {}
    # Else do nothing

    if not p_level_count:
        p_level_count = 0
    # Else do nothing

    p_object_list.add(p_object)

    if p_object.child_list:
        p_level_count += 1
        if p_requested_level:
            if (p_level_count - 1) == p_requested_level:
                p_object.child_list.clear()
            else:
                for child in p_object.child_list:
                    p_parent_child_dict[child.id] = p_object.id
                    query_object_children_recursively(child, p_object_list, p_parent_child_dict, p_level_count,
                                                      p_requested_level)
        else:
            for child in p_object.child_list:
                p_parent_child_dict[child.id] = p_object.id
                query_object_children_recursively(child, p_object_list, p_parent_child_dict, p_level_count,
                                                  p_requested_level)
    # Else do nothing

    return p_object_list, p_parent_child_dict


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
