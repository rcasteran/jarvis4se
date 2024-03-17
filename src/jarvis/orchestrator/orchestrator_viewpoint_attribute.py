"""@defgroup jarvis
Jarvis module
"""
# Libraries

# Modules
import datamodel
from jarvis.orchestrator import orchestrator_viewpoint_requirement
from jarvis.query import question_answer
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
    xml_attribute_list = kwargs['xml_attribute_list']
    output_xml = kwargs['output_xml']

    new_attribute_list = []
    # Create attribute names list already in xml
    xml_attribute_name_list = question_answer.get_objects_names(xml_attribute_list)
    # Filter attribute_list, keeping only the the ones not already in the xml
    for attribute_name in attribute_str_list:
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
    for elem in described_attribute_list:
        obj_to_set = question_answer.check_get_object(
            elem[1],
            **{'xml_function_list': kwargs['xml_function_list'],
               'xml_fun_elem_list': kwargs['xml_fun_elem_list'],
               'xml_fun_inter_list': kwargs['xml_fun_inter_list'],
               'xml_phy_elem_list': kwargs['xml_phy_elem_list'],
               'xml_phy_inter_list': kwargs['xml_phy_inter_list'],
               })
        attribute_wanted = question_answer.check_get_object(
            elem[0],
            **{'xml_attribute_list': kwargs['xml_attribute_list'],
               })
        if obj_to_set is None and attribute_wanted is None:
            print(f"{elem[0]:s} do not exist and {elem[1]:s} neither or {elem[1]:s} is not a:\n"
                  "- Function\n"
                  "- Functional element\n"
                  "- Functional interface\n"
                  "- Physical element\n"
                  "- Physical interface\n")
            continue
        if None in (obj_to_set, attribute_wanted):
            print("{} does not exist".format(
                [elem[i] for i in range(2)
                 if [attribute_wanted, obj_to_set][i] is None]
                .pop()
            ))
            continue
        is_specified = False
        for described_item in attribute_wanted.described_item_list:
            if described_item[0] == obj_to_set.id:
                is_specified = True
                if described_item[1] != str(elem[2]):
                    Logger.set_warning(__name__,
                                       f"Attribute {attribute_wanted.name} already specified for {obj_to_set.name} "
                                       f"with value {described_item[1]}")
                # Else do nothing, attribute already set to this value

        if not is_specified:
            new_described_attribute_list.append([attribute_wanted, (obj_to_set, str(elem[2]))])

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
    xml_requirement_list = kwargs['xml_requirement_list']
    output_xml = kwargs['output_xml']

    for xml_requirement in xml_requirement_list:
        req_subject_object = orchestrator_viewpoint_requirement.retrieve_req_subject_object(
            xml_requirement.description, **kwargs)

        req_object_object_list = orchestrator_viewpoint_requirement.retrieve_req_object_object_list(
            xml_requirement.description, **kwargs)

        if req_subject_object is not None and len(req_object_object_list) > 0:
            for req_object_object in req_object_object_list:
                if attribute[0].name == req_object_object.name and attribute[1][0].name == req_subject_object.name:
                    attribute[0].add_allocated_requirement(xml_requirement)
                    output_xml.write_object_allocation([[attribute[0], xml_requirement]])

                    Logger.set_info(__name__,
                                    f"Requirement {xml_requirement.name} is satisfied by "
                                    f"{attribute[0].name}")
                # Else do nothing
