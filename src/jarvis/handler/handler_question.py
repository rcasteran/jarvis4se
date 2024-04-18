"""@defgroup jarvis
Jarvis module
"""
# Libraries

# Modules
from jarvis.query import question_answer
from tools import Logger


def question_to_user(p_question_str):
    """@ingroup jarvis
    @anchor question_to_user
    Ask question to user and get its answer

    @param[in] p_question_str : question label
    @return user answer
    """
    answer = ''

    try:
        answer = input(p_question_str)
    except KeyboardInterrupt:
        answer = "q"
        Logger.set_info(__name__,
                        f"Answer interrupted")
    return answer


def question_object_info(p_object_str, **kwargs):
    """@ingroup jarvis
    @anchor question_object_info
    Get answer to the user question: "What is <object name> ?"

    @param[in] p_object_str : object name
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    object_str = p_object_str[0].strip()
    wanted_object = question_answer.check_get_object(object_str, **kwargs)

    if wanted_object:
        return str(wanted_object)
    else:
        Logger.set_info(__name__, f"I do not know the following object: {object_str}")


def question_object_allocation(p_object_str, **kwargs):
    """@ingroup jarvis
    @anchor question_object_allocation
    Get answer to the user question: "Is <object name> allocated ?"

    @param[in] p_object_str : object name
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    # TODO To be reworked and extended (currently limited to function and state allocation
    object_info = ""
    p_object_str = p_object_str[0].strip()
    xml_function_name_list = question_answer.get_objects_names(kwargs['xml_function_list'])
    xml_state_name_list = question_answer.get_objects_names(kwargs['xml_state_list'])
    whole_objects_name_list = [*xml_function_name_list, *xml_state_name_list]
    if not any(s == p_object_str for s in whole_objects_name_list):
        Logger.set_warning(__name__,
                           f"{p_object_str} is not a function nor a state")
    else:
        result_function = any(s == p_object_str for s in xml_function_name_list)
        resul_state = any(s == p_object_str for s in xml_state_name_list)
        result = [result_function, False, resul_state,  False, False]
        wanted_object = question_answer.match_object(p_object_str, result, **kwargs)
        if wanted_object:
            allocation_list = question_answer.get_allocation_object(wanted_object, kwargs['xml_fun_elem_list'])
            if allocation_list:
                object_info += f'"{wanted_object.name}" is allocated to ' \
                               + ", ".join([elem.name for elem in allocation_list])
                return object_info

    return
