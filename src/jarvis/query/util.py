# Libraries

# Modules
from xml_adapter import XmlDictKeyListForObjects


def match_object(object_str, result, p_xml_str_lists=None, **kwargs):
    """Returns wanted_object from object_str and result matched from name lists"""
    # Because match_object() called within match_allocated() TBC/TBT if match_allocated()
    # still needed
    if not p_xml_str_lists:
        p_xml_str_lists = XmlDictKeyListForObjects
    for i in range(len(p_xml_str_lists)):
        if result[i]:
            for obj in kwargs[p_xml_str_lists[i]]:
                if object_str == obj.name:
                    return obj
                try:
                    if object_str == obj.alias:
                        return obj
                except AttributeError:
                    # To avoid error when there is no alias for the object
                    pass
    return None
