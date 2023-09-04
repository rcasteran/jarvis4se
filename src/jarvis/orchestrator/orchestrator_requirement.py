"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re
import nltk
import difflib

# Modules
import datamodel
from tools import Logger
from jarvis import question_answer
from jarvis import util
from . import orchestrator_viewpoint

# Constants
REQUIREMENT_CONFIDENCE_RATIO = 0.78
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

            # Check if a requirement with the same description already exist
            xml_requirement_list = kwargs['xml_requirement_list']
            sequence_ratio_list = {}
            for xml_requirement in xml_requirement_list:
                sequence = difflib.SequenceMatcher(None, xml_requirement.description,
                                                   f"{p_str[0]} shall {p_str[1]}")
                if sequence.ratio() > REQUIREMENT_CONFIDENCE_RATIO:
                    sequence_ratio_list[xml_requirement.name] = sequence.ratio()

            if sequence_ratio_list:
                similar_requirement_name = max(sequence_ratio_list, key=sequence_ratio_list.get)
                Logger.set_info(__name__,
                                f"Requirement {similar_requirement_name} has the same "
                                f"description (confidence factor: {sequence_ratio_list[similar_requirement_name]})")
            else:
                answer = input(f"Please give a requirement summary: ")
                if len(answer.lower()) > 0:
                    existing_object = question_answer.check_get_object(answer.lower(), **kwargs)
                    if existing_object:
                        if isinstance(existing_object.type, datamodel.BaseType):
                            if str(existing_object.type) != "Requirement":
                                Logger.set_error(__name__,
                                                 f"{existing_object.type} with the name "
                                                 f"{answer.lower()} already exists")
                            else:
                                requirement_list.append([answer.lower(), f"{p_str[0]} shall {p_str[1]}",
                                                         existing_object, req_subject_object])
                        else:
                            if str(existing_object.type.name) != "Requirement":
                                Logger.set_error(__name__,
                                                 f"{existing_object.type.name} with the name "
                                                 f"{answer.lower()} already exists")
                            else:
                                requirement_list.append([answer.lower(), f"{p_str[0]} shall {p_str[1]}",
                                                         existing_object, req_subject_object])
                    else:
                        requirement_list.append([answer.lower(), f"{p_str[0]} shall {p_str[1]}", None,
                                                 req_subject_object])
                else:
                    Logger.set_error(__name__, "No summary entered for identified requirement")

    if requirement_list:
        update = orchestrator_viewpoint.add_requirement(requirement_list, **kwargs)
    else:
        update = 0

    return update


def check_add_allocation(p_str_list, **kwargs):
    allocation_list = []
    cleaned_allocation_str_list = util.cut_tuple_list(p_str_list)
    for elem in cleaned_allocation_str_list:
        alloc_obj = question_answer.check_get_object(elem[0],
                                                     **{'xml_function_list': kwargs['xml_function_list'],
                                                        'xml_state_list': kwargs['xml_state_list'],
                                                        'xml_data_list': kwargs['xml_data_list'],
                                                        'xml_transition_list': kwargs['xml_transition_list'],
                                                        'xml_fun_elem_list': kwargs['xml_fun_elem_list'],
                                                        'xml_fun_inter_list': kwargs['xml_fun_inter_list'],
                                                        'xml_phy_elem_list': kwargs['xml_phy_elem_list'],
                                                        'xml_phy_inter_list': kwargs['xml_phy_inter_list'],
                                                        })

        req_obj = question_answer.check_get_object(elem[1], **{'xml_requirement_list': kwargs['xml_requirement_list']})

        if not alloc_obj:
            Logger.set_error(__name__, f"Object {elem[0]} not found or cannot satisfy a requirement, "
                                       f"supported satisfactions are:\n"
                                       f"(Function satisfies Requirement) OR\n"
                                       f"(State satisfies Requirement) OR\n"
                                       f"(Data satisfies Requirement) OR\n"
                                       f"(Transition satisfies Requirement) OR\n"
                                       f"(Functional element satisfies Requirement) OR\n"
                                       f"(Functional interface satisfies Requirement) OR\n"
                                       f"(Physical element satisfies Requirement) OR\n"
                                       f"(Physical interface satisfies Requirement)")
        elif not req_obj:
            Logger.set_error(__name__, f"Requirement {elem[1]} not found")
        else:
            if not any(allocated_req_id == req_obj.id for allocated_req_id in alloc_obj.allocated_req_list):
                alloc_obj.add_allocated_requirement(req_obj)
                allocation_list.append([alloc_obj, req_obj])
            else:
                Logger.set_info(__name__,
                                f"{req_obj.__class__.__name__} {req_obj.name} already satisfied by "
                                f"{alloc_obj.__class__.__name__} {alloc_obj.name}")

    if allocation_list:
        output_xml = kwargs['output_xml']
        output_xml.write_object_allocation(allocation_list)

        for elem in allocation_list:
            Logger.set_info(__name__,
                            f"{elem[1].__class__.__name__} {elem[1].name} is satisfied by "
                            f"{elem[0].__class__.__name__} {elem[0].name}")

        update = 1
    else:
        update = 0

    return update
