"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re

# Modules
from tools import Logger


def check_add_requirement(p_str_list, **kwargs):
    for p_str in p_str_list:
        # Detect if...then pattern before the requirement subject
        pattern_if = re.compile(r'if (.*?), then ([^.|\n]*)', re.IGNORECASE).split(p_str[0])
        # Detect when pattern before the requirement subject
        pattern_when = re.compile(r'when (.*?), ([^.|\n]*)', re.IGNORECASE).split(p_str[0])

        req_object = p_str[1]

        req_subject = ''
        req_conditional = ''
        req_temporal = ''
        if len(pattern_if) > 1 and len(pattern_when) > 1:
            req_conditional = pattern_if[1]
            req_subject = pattern_if[2]
            req_temporal = pattern_when[1]
        elif len(pattern_if) > 1:
            req_conditional = pattern_if[1]
            req_subject = pattern_if[2]
        elif len(pattern_when) > 1:
            req_temporal = pattern_when[1]
            req_subject = pattern_when[2]
        else:
            req_subject = p_str[0]

        Logger.set_info(__name__, f"Requirement identified: {p_str[0]} shall {p_str[1]}")
        Logger.set_debug(__name__, f"Requirement subject: {req_subject}")
        Logger.set_debug(__name__, f"Requirement object: {req_object}")
        Logger.set_debug(__name__, f"Requirement is conditional: {req_conditional}")
        Logger.set_debug(__name__, f"Requirement is temporal: {req_temporal}")

    return 0
