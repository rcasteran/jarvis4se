"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re
import nltk

# Modules
import datamodel
from tools import Logger
from jarvis import question_answer
from . import orchestrator_viewpoint

# Constants
NOUN_SINGULAR_TAG = "NN"
NOUN_PLURAL_TAG = "NNS"
PROPER_NOUN_SINGULAR_TAG = "NNP"
DETERMINER_TAG = "DT"
ADJECTIVE_TAG = "JJ"


def check_add_requirement(p_str_list, **kwargs):
    requirement_list = []
    for p_str in p_str_list:
        # Detect if...then pattern before the requirement subject
        pattern_if = re.compile(r'if (.*?), then ([^.|\n]*)', re.IGNORECASE).split(p_str[0])
        # Detect when pattern before the requirement subject
        pattern_when = re.compile(r'when (.*?), ([^.|\n]*)', re.IGNORECASE).split(p_str[0])

        req_object = p_str[1]

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

        Logger.set_debug(__name__, f"Requirement subject: {req_subject}")
        Logger.set_debug(__name__, f"Requirement object: {req_object}")
        Logger.set_debug(__name__, f"Requirement is conditional: {req_conditional}")
        Logger.set_debug(__name__, f"Requirement is temporal: {req_temporal}")

        # Retrieve the subject in object list
        req_subject_object = None
        is_previous_proper_noun_singular_tag = False
        is_error = False
        token_list = nltk.word_tokenize(req_subject)
        tag_list = nltk.pos_tag(token_list)
        for tag in tag_list:
            if tag[1] == PROPER_NOUN_SINGULAR_TAG:
                req_subject_object = question_answer.check_get_object(tag[0], **kwargs)
                is_previous_proper_noun_singular_tag = True
            elif tag[1] == NOUN_SINGULAR_TAG or tag[1] == NOUN_PLURAL_TAG:
                if not is_previous_proper_noun_singular_tag:
                    req_subject_object = question_answer.check_get_object(tag[0], **kwargs)
                # Else dismiss the noun

                is_previous_proper_noun_singular_tag = False
            elif tag[1] == DETERMINER_TAG or tag[1] == ADJECTIVE_TAG:
                is_previous_proper_noun_singular_tag = False
            elif tag[1] != DETERMINER_TAG:
                Logger.set_error(__name__,
                                 f"Requirement bad formatted: {tag[0]} is not a determiner nor an adjective nor a noun")
                is_error = True
                break

        if not is_error:
            if req_subject_object:
                Logger.set_info(__name__, f"Requirement identified about {req_subject_object.name}: "
                                          f"{p_str[0]} shall {p_str[1]}")
            else:
                Logger.set_info(__name__, f"Requirement identified about: {p_str[0]} shall {p_str[1]}")

            answer = input(f"Please give a requirement summary: ")
            if len(answer.lower()) > 0:
                existing_object = question_answer.check_get_object(answer.lower(), **kwargs)
                if existing_object:
                    if isinstance(existing_object.type, datamodel.BaseType):
                        if str(existing_object.type) != "Requirement":
                            Logger.set_error(__name__,
                                             f"{existing_object.type} with the name {elem[0]} already exists")
                        else:
                            requirement_list.append([answer.lower(), f"{p_str[0]} shall {p_str[1]}", existing_object])

                    else:
                        if str(existing_object.type.name) != "Requirement":
                            Logger.set_error(__name__,
                                             f"{existing_object.type.name} with the name {elem[0]} already exists")
                        else:
                            requirement_list.append([answer.lower(), f"{p_str[0]} shall {p_str[1]}", existing_object])
                else:
                    requirement_list.append([answer.lower(), f"{p_str[0]} shall {p_str[1]}", None])
            else:
                Logger.set_error(__name__, "No summary entered for identified requirement")

    if requirement_list:
        update = orchestrator_viewpoint.add_requirement(requirement_list, **kwargs)
    else:
        update = 0

    return update
