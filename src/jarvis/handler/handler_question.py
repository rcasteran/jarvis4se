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


# Constants
TEXT_ANSWER_DISPLAY = 'as text'
ANSWER_FORMAT_STRING = 'str'
ANSWER_FORMAT_DICT = 'dict'


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
    return answer, ANSWER_FORMAT_STRING


def question_object_info(p_object_str, **kwargs):
    """@ingroup jarvis
    @anchor question_object_info
    Get answer to the user question: "What is <object name> ?"

    @param[in] p_object_str : object name
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    info_obj = None
    info_obj_format = None
    object_name = p_object_str[0].strip()

    if TEXT_ANSWER_DISPLAY in object_name:
        is_answer_text = True
        object_name = object_name[0: object_name.index(TEXT_ANSWER_DISPLAY)].strip()
    else:
        is_answer_text = False

    wanted_object = query_object.query_object_by_name(object_name, **kwargs)

    if wanted_object:
        if is_answer_text:
            info_obj = str(wanted_object)

            wanted_object_attribute_list = query_object.query_object_attribute_properties_list(wanted_object, **kwargs)
            for wanted_object_attribute in wanted_object_attribute_list:
                if len(wanted_object_attribute[1]) > len(f'"{wanted_object.name}" {wanted_object_attribute[0]}'):
                    info_obj += ('\n' + f'"{wanted_object.name}" {wanted_object_attribute[0]} is:\n'
                                        f'{wanted_object_attribute[1]}')
                else:
                    info_obj += '\n' + f'"{wanted_object.name}" {wanted_object_attribute[0]} is ' \
                                       f'{wanted_object_attribute[1]}'

            info_obj_format = ANSWER_FORMAT_STRING
        else:
            wanted_object_attribute_dict = {}
            wanted_object_attribute_list = query_object.query_object_attribute_properties_list(wanted_object, **kwargs)
            for wanted_object_attribute in wanted_object_attribute_list:
                wanted_object_attribute_dict[wanted_object_attribute[0]] = wanted_object_attribute[1]

            info_obj = {'title': f"Object {wanted_object.name}:",
                        'data': {**wanted_object.info()[0], **wanted_object_attribute_dict},
                        'columns': [*wanted_object.info()[1], *wanted_object_attribute_dict.keys()],
                        'index': [0]}

            info_obj_format = ANSWER_FORMAT_DICT
    else:
        Logger.set_info(__name__, f"I do not know the following object: {object_name}")

    return info_obj, info_obj_format


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

    return object_info, ANSWER_FORMAT_STRING
