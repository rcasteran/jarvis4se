"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re

# Modules
import datamodel
from . import orchestrator_shared
from jarvis import question_answer, util
from tools import Logger


def add_view(view_name_str, **kwargs):
    """
        Check if each string in view_name_str is not already corresponding to an actual
        object's name, create new View() object, instantiate it, write it within XML and
        then returns update_list.

            Parameters:
                view_name_str ([str]) : Lists of string from jarvis cell
                xml_view_list ([Function]) : view list from xml parsing
                output_xml (XmlWriter3SE object) : XML's file object

            Returns:
                1 if update, else 0
        """
    xml_view_list = kwargs['xml_view_list']
    output_xml = kwargs['output_xml']
    view_list = []
    update = 0

    # Create a list with all view names already in the xml
    xml_view_name_list = question_answer.get_objects_names(xml_view_list)

    # Loop on the list and create set for functions
    if view_name_str not in xml_view_name_list:
        # Instantiate view class
        view = datamodel.View(name=view_name_str, uid=util.get_unique_id())
        # Add view to new set() and existing set() from xml
        xml_view_list.add(view)
        view_list.append(view)

    activate_view(view_name_str, xml_view_list)

    if view_list:
        output_xml.write_view(view_list)
        for view in view_list:
            Logger.set_info(__name__,
                            view.name + " is a view")
        update = 1

    return update


def activate_view(view_name, xml_view_list):
    """Activates View from view's name str"""
    for view in xml_view_list:
        if view_name == view.name:
            view.set_activation(True)
        else:
            view.set_activation(False)


def check_get_consider(consider_str_list, **kwargs):
    """
    Check and get all "consider xxx" strings. If corresponds to an actual object not yet added to
    the current view => add it to View object and as allocatedItem within xml
    Args:
        consider_str_list ([strings]): list of strings (separated by comma is possible)
        xml_function_list ([Function]) : Function list from xml parsing
        xml_fun_elem_list ([Fun Elem]) : Functional Element list from xml parsing
        xml_data_list ([Data]) : Data list from xml parsing
        xml_view_list ([View]) : View list from xml parsing
        output_xml (XmlWriter3SE object) : XML's file object

    Returns:
        update ([0/1]) : 1 if update, else 0
    """
    xml_function_list = kwargs['xml_function_list']
    xml_fun_elem_list = kwargs['xml_fun_elem_list']
    xml_data_list = kwargs['xml_data_list']
    xml_view_list = kwargs['xml_view_list']
    output_xml = kwargs['output_xml']

    allocated_item_list = []
    # Create lists with all object names/aliases already in the xml
    xml_fun_elem_name_list = question_answer.get_objects_names(xml_fun_elem_list)
    xml_function_name_list = question_answer.get_objects_names(xml_function_list)
    xml_data_name_list = question_answer.get_objects_names(xml_data_list)

    consider_str_list = util.cut_chain_from_string_list(consider_str_list)

    for consider_str in consider_str_list:
        if consider_str not in [*xml_fun_elem_name_list, *xml_function_name_list,
                                *xml_data_name_list]:
            Logger.set_warning(__name__,
                               f"Object {consider_str} does not exist, available object types are : "
                               f"Functional Element, Function and Data")
        else:
            result_function = any(item == consider_str for item in xml_function_name_list)
            result_fun_elem = any(item == consider_str for item in xml_fun_elem_name_list)
            result_data = any(item == consider_str for item in xml_data_name_list)

            if result_function:
                allocated_fun = orchestrator_shared.check_add_allocated_item(
                    consider_str, xml_function_list, xml_view_list)
                if allocated_fun:
                    allocated_item_list.append(allocated_fun)
            elif result_fun_elem:
                allocated_fun_elem = orchestrator_shared.check_add_allocated_item(
                    consider_str, xml_fun_elem_list, xml_view_list)
                if allocated_fun_elem:
                    allocated_item_list.append(allocated_fun_elem)
            elif result_data:
                allocated_data = orchestrator_shared.check_add_allocated_item(
                    consider_str, xml_data_list, xml_view_list)
                if allocated_data:
                    allocated_item_list.append(allocated_data)

    update = orchestrator_shared.add_allocation({5: allocated_item_list}, output_xml)

    return update


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


def check_add_object_attribute(described_attribute_list, **xml_dict_sets):
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
            **{'xml_function_list': xml_dict_sets['xml_function_list'],
               'xml_fun_elem_list': xml_dict_sets['xml_fun_elem_list'],
               'xml_fun_inter_list': xml_dict_sets['xml_fun_inter_list'],
               'xml_phy_elem_list': xml_dict_sets['xml_phy_elem_list'],
               'xml_phy_inter_list': xml_dict_sets['xml_phy_inter_list'],
               })
        attribute_wanted = question_answer.check_get_object(
            elem[0],
            **{'xml_attribute_list': xml_dict_sets['xml_attribute_list'],
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

    update = add_object_attribute(new_described_attribute_list, xml_dict_sets['output_xml'])

    return update


def add_object_attribute(new_obj_attribute_list, output_xml):
    """
    Check if input list is not empty, write in xml for each element and return update list if some
    updates has been made

        Parameters:
            new_obj_attribute_list ([Attribute, (Object, value)]) : New described attributes
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if not new_obj_attribute_list:
        return 0

    output_xml.write_attribute_described_item(new_obj_attribute_list)
    # Warn the user once added within xml
    for described_attribute in new_obj_attribute_list:
        described_attribute[0].add_described_item(described_attribute[1])
        Logger.set_info(__name__,
                        f"Attribute {described_attribute[0].name} for {described_attribute[1][0].name} "
                        f"with value {described_attribute[1][1]}")
    return 1


def check_set_extends(extends_str_list, **kwargs):
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
    xml_type_list = kwargs['xml_type_list']
    output_xml = kwargs['output_xml']

    new_type_list = []
    # Capitalyze the reference type for datamodel matching
    for elem in extends_str_list:
        if any(t == elem[0] for t in question_answer.get_objects_names(xml_type_list)):
            # print(f"{elem[0]} already exists")
            continue
        type_to_extend = check_get_type_to_extend(elem[1], xml_type_list)
        if not type_to_extend:
            Logger.set_error(__name__,
                             f"Unable to find referenced type '{elem[1]}'")
            continue
        new_type = datamodel.Type()
        new_type.set_name(elem[0])
        # Generate and set unique identifier of length 10 integers
        new_type.set_id(util.get_unique_id())

        new_type.set_base(type_to_extend)

        new_type_list.append(new_type)
        xml_type_list.add(new_type)

    if not new_type_list:
        return 0

    output_xml.write_type_element(new_type_list)
    for obj_type in new_type_list:
        if isinstance(obj_type.base, datamodel.Type):
            base_type = obj_type.base.name
        else:
            base_type = obj_type.base

        Logger.set_info(__name__,
                        f"{obj_type.name} is a type extending {str(base_type)}")

    return 1


def check_get_type_to_extend(type_str, xml_type_list):
    """Checks if type_str is within BaseType or xml_type_list, then return Basetype or
    type object"""
    check = None
    formated_type_str = type_str.upper().replace(" ", "_")
    if any(a == formated_type_str for a in [i.name for i in datamodel.BaseType]):
        return datamodel.BaseType[formated_type_str]

    if any(a == type_str for a in question_answer.get_objects_names(xml_type_list)):
        check = question_answer.check_get_object(type_str, **{'xml_type_list': xml_type_list})
        return check

    return check


def add_requirement(requirement_str_list, **kwargs):
    xml_requirement_list = kwargs['xml_requirement_list']
    output_xml = kwargs['output_xml']

    new_requirement_list = []
    # Create requirement names list already in xml
    xml_requirement_name_list = question_answer.get_objects_names(xml_requirement_list)
    # Filter attribute_list, keeping only the the ones not already in the xml
    for requirement_item in requirement_str_list:
        if requirement_item[0] not in xml_requirement_name_list:
            new_requirement = datamodel.Requirement()
            new_requirement.set_name(str(requirement_item[0]))
            new_requirement.set_description(str(requirement_item[1]))
            # Generate and set unique identifier of length 10 integers
            new_requirement.set_id(util.get_unique_id())
            # alias is 'none' by default
            new_requirement_list.append(new_requirement)
        else:
            Logger.set_info(__name__, requirement_item[0] + " already exists")

    if not new_requirement_list:
        return 0

    output_xml.write_requirement(new_requirement_list)
    for requirement in new_requirement_list:
        xml_requirement_list.add(requirement)
        Logger.set_info(__name__,
                        requirement.name + " is a requirement")
    return 1