"""@defgroup jarvis
Jarvis module
"""

# Libraries
import re

# Modules
from tools import Logger


def cut_string_list(string_tuple_list):
    """@ingroup jarvis
    @anchor cut_string_list
    From a list of input strings containing {(element_A, [element_B, element_C])} or {([element_B, element_C],
    element_A)}, returns a list of combined strings containing {(element_A, element_B), (element_A, element_C)}.

    Allows to handle such Jarvis command as "F1, F2, F3 compose F"

    @param[in] string_tuple_list ([(str, str), ...]) : list of input string
    @return list of combined strings
    """
    Logger.set_debug(__name__, f'Input: {string_tuple_list}')

    output_list = []
    for parent, child in string_tuple_list:
        if "," in child:
            child_str = child.replace(" ", "")
            child_list_str = re.split(r',(?![^[]*\])', child_str)
            for elem in child_list_str:
                output_list.append((parent, elem))
        elif "," in parent:
            parent_str = parent.replace(" ", "")
            parent_list_str = re.split(r',(?![^[]*\])', parent_str)
            for elem in parent_list_str:
                output_list.append((elem, child))
        else:
            output_list.append((parent, child))

    Logger.set_debug(__name__, f'Output: {output_list}')

    return output_list
