# Libraries

# Modules
from jarvis.query import question_answer
from tools import Logger


def question_object_info(question_str, **kwargs):
    """Get the 'what' declaration """
    object_str = question_str[0].strip()
    wanted_object = question_answer.check_get_object(object_str, **kwargs)

    if wanted_object:
        object_info = question_answer.get_object_info(wanted_object, **kwargs)
        if object_info:
            return object_info


def question_object_allocation(object_str, **kwargs):
    """From object_str, get object then check if allocated and returns allocation's list"""
    object_info = ""
    object_str = object_str[0]
    xml_function_name_list = question_answer.get_objects_names(kwargs['xml_function_list'])
    xml_state_name_list = question_answer.get_objects_names(kwargs['xml_state_list'])
    whole_objects_name_list = [*xml_function_name_list, *xml_state_name_list]
    if not any(s == object_str for s in whole_objects_name_list):
        Logger.set_warning(__name__,
                           f"{object_str} is not a function nor a state")
    else:
        result_function = any(s == object_str for s in xml_function_name_list)
        resul_state = any(s == object_str for s in xml_state_name_list)
        result = [result_function, False, resul_state,  False, False]
        wanted_object = question_answer.match_object(object_str, result, **kwargs)
        if wanted_object:
            allocation_list = question_answer.get_allocation_object(wanted_object, kwargs['xml_fun_elem_list'])
            if allocation_list:
                object_info += f'"{wanted_object.name}" is allocated to ' \
                               + ", ".join([elem.name for elem in allocation_list])
                return object_info

    return
