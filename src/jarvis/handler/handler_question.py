"""@defgroup jarvis
Jarvis module
"""
# Libraries

# Modules
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from jarvis.query import query_object, question_answer
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
    wanted_object = query_object.query_object_by_name(object_str, **kwargs)

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
    # TODO To be reworked
    p_object_str = p_object_str[0].strip()
    wanted_object = query_object.query_object_by_name(p_object_str, **kwargs)
    if wanted_object:
        allocation_list = question_answer.get_allocation_object(wanted_object, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
                                                                **kwargs)
        if allocation_list:
            object_info = f'"{wanted_object.name}" is allocated to ' \
                           + ", ".join([elem.name for elem in allocation_list])
        else:
            object_info = f'"{wanted_object.name}" is not allocated'
    else:
        object_info = f'"{p_object_str}" is unknown'

    return object_info
