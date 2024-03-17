"""@defgroup jarvis
Jarvis module
"""
# Libraries

# Modules
import datamodel
from jarvis.query import question_answer
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
    xml_type_list = kwargs['xml_type_list']
    output_xml = kwargs['output_xml']

    new_type_list = []
    # Capitalize the reference type for datamodel matching
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
    formatted_type_str = type_str.upper().replace(" ", "_")
    if any(a == formatted_type_str for a in [i.name for i in datamodel.BaseType]):
        return datamodel.BaseType[formatted_type_str]

    if any(a == type_str for a in question_answer.get_objects_names(xml_type_list)):
        check = question_answer.check_get_object(type_str, **{'xml_type_list': xml_type_list})
        return check

    return check
