# Libraries

# Modules
from xml_adapter import XmlDictKeyListForObjects
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
