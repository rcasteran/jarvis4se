"""@defgroup jarvis
Jarvis module
"""

# Libraries
import re
import uuid
import pandas as pd


# Modules
from tools import Logger


def cut_tuple_list(string_tuple_list):
    """@ingroup jarvis
    @anchor cut_tuple_list
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
            child_list_str = cut_string(child)
            for elem in child_list_str:
                output_list.append((parent, elem))
        elif "," in parent:
            parent_list_str = cut_string(parent)
            for elem in parent_list_str:
                output_list.append((elem, child))
        else:
            output_list.append((parent, child))

    Logger.set_debug(__name__, f'Output: {output_list}')

    return output_list


def reverse_tuple_list(string_tuple_list):
    """@ingroup jarvis
    @anchor reverse_tuple_list
    Reverse a list of input strings

    @param[in] string_tuple_list ([(str, str), ...]) : list of input string
    @return list of reversed input strings
    """
    sorted_list = []
    for string_tuple in string_tuple_list:
        reversed_string_tuple = ()
        for k in reversed(string_tuple):
            reversed_string_tuple = reversed_string_tuple + (k,)
        sorted_list.append(reversed_string_tuple)

    return sorted_list


def cut_chain_from_string_list(input_string_list):
    """@ingroup jarvis
    @anchor cut_chain_from_string_list
    Creates flatten list : from ["A", "B, C, D"] to ["A", "B", "C", "D"]

    @param[in] input_string_list : input string list
    @return list of strings
    """
    output_list = []
    for input_string in input_string_list:
        if "," in input_string:
            for split_string in cut_string(input_string):
                output_list.append(split_string)
        else:
            output_list.append(input_string)

    return output_list


def cut_string(input_string):
    """@ingroup jarvis
    @anchor cut_string
    From an string containing "element_A, element_B, element_C...", returns a list of strings containing
    [[element_A], [element_B], [element_C], ...]

    @param[in] input_string : input string
    @return list of strings
    """
    split_string = re.split(r',(?![^[]*\])', input_string)

    i = 0
    for elem in split_string.copy():
        split_string[i] = elem.strip()
        i = i+1

    return split_string


def get_unique_id():
    """@ingroup jarvis
    @anchor get_unique_id
    Generate unique identifier of length 10 integers

    @return uuid
    """
    identifier = uuid.uuid4()
    return str(identifier.int)[:10]


def get_pandas_table(data_dict):
    """Returns pandas data frame called from command_parser.matched_list()
    with data_dict as list of ..."""
    if 'columns' in data_dict.keys():
        data_frame = pd.DataFrame(data_dict['data'], columns=data_dict['columns'])
    else:
        data_frame = pd.DataFrame(data_dict['data'])
    data_frame = data_frame.T
    if 'Data' in data_dict['title'] or 'Transition' in data_dict['title']:
        if 'Data' in data_dict['title']:
            first = 1
            last = 5
        else:
            first = 3
            last = 4
        for idx in range(first, last):
            data_frame.iloc[idx] = data_frame.iloc[idx].str.join("\\n")
    data_frame = data_frame.style \
        .set_caption(data_dict['title']) \
        .set_properties(**{'white-space': 'nowrap'})

    return data_frame.to_html().replace("\\n", "<br>")
