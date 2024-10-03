""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from jarvis.orchestrator import orchestrator_viewpoint_requirement, orchestrator_object
from jarvis import util
from tools import Logger


def add_attribute(attribute_str_list, **kwargs):
    """
    Check if each string in xml_attribute_list is not already corresponding to an actual object's
    name/alias, create new Attribute() object, instantiate it, write it within XML and then returns
    update_list.

        Parameters:
            attribute_str_list ([str]) : Lists of string from jarvis cell
            xml_attribute_list ([Attribute]) : Attribute list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    xml_attribute_list = kwargs[XML_DICT_KEY_9_ATTRIBUTE_LIST]
    output_xml = kwargs['output_xml']

    new_attribute_list = []
    # Create attribute names list already in xml
    xml_attribute_name_list = orchestrator_object.check_object_name_in_list(xml_attribute_list)
    # Filter attribute_list, keeping only the ones not already in the xml
    for elem in attribute_str_list:
        attribute_name = elem.replace('"', "")
        if attribute_name not in xml_attribute_name_list:
            new_attribute = datamodel.Attribute()
            new_attribute.set_name(str(attribute_name))
            # Generate and set unique identifier of length 10 integers
            new_attribute.set_id(util.get_unique_id())
            # alias is 'none' by default
            new_attribute_list.append(new_attribute)

    if not new_attribute_list:
        return 0

    output_xml.write_attribute(new_attribute_list)
    for attribute in new_attribute_list:
        xml_attribute_list.add(attribute)
        Logger.set_info(__name__,
                        attribute.name + " is an attribute")
    return 1


def check_add_object_attribute(described_attribute_list, **kwargs):
    """
    Check if each string in described_attribute_list are corresponding to an actual object and
    attribute, create new [Attribute, (Object, value)] objects list.
    Send lists to add_object_attribute() to write them within xml and then returns update_list
    from it.

        Parameters:
            described_attribute_list ([str]) : Lists of string from jarvis cell
            xml_attribute_list ([Attribute]) : Attribute's list from xml

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    new_described_attribute_list = []

    # elem = [attribute_name, object_name, attribute_value]
    for elem in described_attribute_list:
        attribute_name = elem[0].replace('"', "")
        object_name = elem[1].replace('"', "")
        attribute_value = elem[2].replace('"', "")

        obj_to_set = orchestrator_object.retrieve_object_by_name(
            object_name,
            **{XML_DICT_KEY_1_FUNCTION_LIST: kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
               XML_DICT_KEY_0_DATA_LIST: kwargs[XML_DICT_KEY_0_DATA_LIST],
               XML_DICT_KEY_7_TRANSITION_LIST: kwargs[XML_DICT_KEY_7_TRANSITION_LIST],
               XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
               XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
               XML_DICT_KEY_4_PHY_ELEM_LIST: kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST],
               XML_DICT_KEY_5_PHY_INTF_LIST: kwargs[XML_DICT_KEY_5_PHY_INTF_LIST],
               })
        attribute_wanted = orchestrator_object.retrieve_object_by_name(
            attribute_name,
            **{XML_DICT_KEY_9_ATTRIBUTE_LIST: kwargs[XML_DICT_KEY_9_ATTRIBUTE_LIST],
               })
        if obj_to_set is None or attribute_wanted is None:
            Logger.set_warning(__name__,
                               f"{attribute_name} do not exist and {object_name} neither or {object_name} is not a:\n"
                               "- Function\n"
                               "- Data\n"
                               "- Transition\n"
                               "- Functional element\n"
                               "- Functional interface\n"
                               "- Physical element\n"
                               "- Physical interface\n")
        else:
            is_specified = False
            for described_item in attribute_wanted.described_item_list:
                if described_item[0] == obj_to_set.id:
                    is_specified = True
                    if described_item[1] != attribute_value:
                        Logger.set_warning(__name__,
                                           f"Attribute {attribute_wanted.name} already specified for {obj_to_set.name} "
                                           f"with value {described_item[1]}")
                    # Else do nothing, attribute already set to this value

            if not is_specified:
                new_described_attribute_list.append([attribute_wanted, (obj_to_set, attribute_value)])

    update = add_object_attribute(new_described_attribute_list, **kwargs)

    return update


def add_object_attribute(new_obj_attribute_list, **kwargs):
    """
    Check if input list is not empty, write in xml for each element and return update list if some
    updates has been made

        Parameters:
            new_obj_attribute_list ([Attribute, (Object, value)]) : New described attributes
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    update = 0

    if new_obj_attribute_list:
        output_xml = kwargs['output_xml']
        output_xml.write_attribute_described_item(new_obj_attribute_list)
        # Warn the user once added within xml
        for described_attribute in new_obj_attribute_list:
            described_attribute[0].add_described_item(described_attribute[1])
            Logger.set_info(__name__,
                            f"Attribute {described_attribute[0].name} for {described_attribute[1][0].name} "
                            f"with value {described_attribute[1][1]}")

            # Add requirement related to the attribute if any
            add_attribute_requirement(described_attribute, **kwargs)

            update = 1

    return update


def add_attribute_requirement(attribute, **kwargs):
    xml_requirement_list = kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
    output_xml = kwargs['output_xml']

    for xml_requirement in xml_requirement_list:
        req_subject_object = orchestrator_viewpoint_requirement.retrieve_req_subject_object(
            xml_requirement.text, **kwargs)

        req_object_object_list = orchestrator_viewpoint_requirement.retrieve_req_object_object_list(
            xml_requirement.text, **kwargs)

        if req_subject_object is not None and len(req_object_object_list) > 0:
            for req_object_object in req_object_object_list:
                if attribute[0].name == req_object_object.name and attribute[1][0].name == req_subject_object.name:
                    attribute[0].add_allocated_requirement(xml_requirement.id)
                    output_xml.write_object_allocation([[attribute[0], xml_requirement]])

                    Logger.set_info(__name__,
                                    f"{xml_requirement.__class__.__name__} {xml_requirement.name} is satisfied by "
                                    f"{attribute[0].__class__.__name__} {attribute[0].name}")
                # Else do nothing
