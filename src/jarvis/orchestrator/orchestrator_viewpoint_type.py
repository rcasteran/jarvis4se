""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
from . import orchestrator_object
from jarvis import util
from tools import Logger


def check_add_type_extension(extends_str_list, **kwargs):
    """
    Check if each type_to_extend string in extends_str_list are corresponding to actual objects
    name/alias, create lists for all <type> objects that needs to be added.

        Parameters:
            extends_str_list ([str]) : Lists of string from jarvis cell
            xml_type_list ([Type]) : xml list of type
            output_xml : xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    update = 0
    xml_type_list = kwargs[XML_DICT_KEY_14_TYPE_LIST]
    output_xml = kwargs['output_xml']
    new_type_list = []

    # elem = [type_extension_name, type_to_extend_name]
    for elem in extends_str_list:
        type_extension_name = elem[0].replace('"', "")
        type_to_extend_name = elem[1].replace('"', "")

        if any(t == type_extension_name for t in orchestrator_object.check_object_name_in_list(xml_type_list)):
            Logger.set_info(__name__,
                            f'"{type_extension_name}" already exists')
            continue

        type_to_extend = check_get_type_to_extend(type_to_extend_name, xml_type_list)
        if not type_to_extend:
            Logger.set_error(__name__,
                             f'Unable to find referenced type "{type_to_extend_name}"')
            continue

        new_type = datamodel.Type()
        new_type.set_name(type_extension_name)
        # Generate and set unique identifier of length 10 integers
        new_type.set_id(util.get_unique_id())

        new_type.set_base(type_to_extend)

        new_type_list.append(new_type)
        xml_type_list.add(new_type)

    if new_type_list:
        output_xml.write_type_element(new_type_list)
        for obj_type in new_type_list:
            if isinstance(obj_type.base, datamodel.Type):
                base_type = obj_type.base.name
            else:
                base_type = obj_type.base

            Logger.set_info(__name__,
                            f"{obj_type.name} is a type extending {str(base_type)}")

        update = 1
    # Else do nothing

    return update


def check_get_type_to_extend(type_str, xml_type_list):
    """Checks if type_str is within BaseType or xml_type_list, then return Basetype or
    type object"""
    check = None
    formatted_type_str = type_str.upper().replace(" ", "_")
    if any(a == formatted_type_str for a in [i.name for i in datamodel.BaseType]):
        return datamodel.BaseType[formatted_type_str]

    if any(a == type_str for a in orchestrator_object.check_object_name_in_list(xml_type_list)):
        check = orchestrator_object.retrieve_object_by_name(type_str, **{XML_DICT_KEY_14_TYPE_LIST: xml_type_list})
        return check

    return check
