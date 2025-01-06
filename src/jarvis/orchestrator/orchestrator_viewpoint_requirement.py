""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries
import re
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
import difflib

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_INFORMATION_LIST, XML_DICT_KEY_11_ATTRIBUTE_LIST, \
    XML_DICT_KEY_12_VIEW_LIST, XML_DICT_KEY_13_TYPE_LIST, XML_DICT_KEY_14_FUN_CONS_LIST, \
    XML_DICT_KEY_15_FUN_PROD_LIST, XML_DICT_KEY_16_ACT_CONS_LIST, XML_DICT_KEY_17_ACT_PROD_LIST
from . import orchestrator_object
from tools import Logger
from jarvis.handler import handler_question
from jarvis import util

# Constants
REQUIREMENT_CONFIDENCE_RATIO = 0.95
NOUN_SINGULAR_TAG = "NN"
NOUN_PLURAL_TAG = "NNS"
PROPER_NOUN_SINGULAR_TAG = "NNP"
DETERMINER_TAG = "DT"
ADJECTIVE_TAG = "JJ"
SUBORDINATE_TAG = "IN"
COORDINATE_TAG = "CC"
PRONOUN_PERSONAL_TAG = "PRP"
VERB_TAG = "VB"
VERB_PAST_TAG = "VBN"
TO_TAG = "TO"
SEMICOLON_TAG = ":"


def check_add_requirement(p_str_list, **kwargs):
    """@ingroup orchestrator
    @anchor check_add_requirement
    Check list of requirement declarations before adding them to jarvis data structure

    @param[in] p_str_list : list of requirement declarations
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    requirement_list = []

    for p_str in p_str_list:
        desc_before_modal = p_str[0].replace('"', "")
        desc_after_modal = p_str[1].replace('"', "")

        if not desc_before_modal.startswith(f'The {datamodel.ObjectTextPropertyLabel} of '):
            req_subject, req_object, req_conditional, req_temporal = detect_req_pattern(desc_before_modal,
                                                                                        desc_after_modal)

            # Retrieve the subject in object list
            req_subject_object_list, is_error = retrieve_req_proper_noun_object_list(req_subject,
                                                                                     **kwargs)

            if not is_error:
                if len(req_subject_object_list) > 0:
                    # Take the last one in case of requirement about attribute ( XXX of YYY shall)
                    if isinstance(req_subject_object_list[-1], datamodel.TypeWithAllocatedReqList):
                        req_subject_object = req_subject_object_list[-1]
                        Logger.set_info(__name__, f"Requirement identified about {req_subject_object.name}: "
                                                  f"{desc_before_modal} shall {desc_after_modal}")
                    else:
                        req_subject_object = None
                        Logger.set_info(__name__,
                                        f"Requirement identified: {desc_before_modal} shall {desc_after_modal}")
                        Logger.set_warning(__name__,
                                           f'Subject "{req_subject}" of the requirement is unknown')
                else:
                    req_subject_object = None
                    Logger.set_info(__name__, f"Requirement identified: {desc_before_modal} shall {desc_after_modal}")
                    Logger.set_warning(__name__,
                                       f'Subject "{req_subject}" of the requirement is unknown')

                # Check if a requirement with the same text already exist
                sequence_ratio_list = evaluate_text_similarities(req_subject,
                                                                 req_object,
                                                                 req_conditional,
                                                                 req_temporal,
                                                                 **kwargs)

                req_allocated_object_list = check_requirement_relationship(req_subject_object_list,
                                                                           req_object,
                                                                           req_conditional,
                                                                           req_temporal,
                                                                           **kwargs)
                if sequence_ratio_list:
                    similar_requirement_name = max(sequence_ratio_list, key=sequence_ratio_list.get)
                    Logger.set_info(__name__,
                                    f"Requirement {similar_requirement_name} has the same "
                                    f"text (confidence factor: {sequence_ratio_list[similar_requirement_name]})")
                else:
                    answer, _ = handler_question.question_to_user(f"Please give a requirement name: ")
                    if len(answer) > 0 and answer != "q":
                        existing_object = orchestrator_object.retrieve_object_by_name(answer, **kwargs)
                        if existing_object:
                            if isinstance(existing_object.type, datamodel.BaseType):
                                if str(existing_object.type) != "Requirement":
                                    Logger.set_error(__name__,
                                                     f"{existing_object.type} with the name "
                                                     f"{answer} already exists")
                                else:
                                    requirement_list.append([answer, f"{desc_before_modal} shall {desc_after_modal}",
                                                             req_subject_object_list,
                                                             req_allocated_object_list])
                            else:
                                if str(existing_object.type.name) != "Requirement":
                                    Logger.set_error(__name__,
                                                     f"{existing_object.type.name} with the name "
                                                     f"{answer} already exists")
                                else:
                                    requirement_list.append([answer, f"{desc_before_modal} shall {desc_after_modal}",
                                                             req_subject_object_list,
                                                             req_allocated_object_list])
                        else:
                            requirement_list.append([answer, f"{desc_before_modal} shall {desc_after_modal}",
                                                     req_subject_object_list, req_allocated_object_list])
                    else:
                        Logger.set_error(__name__, "No name entered for identified requirement")
            # Else do nothing
        # Else do nothing

    if requirement_list:
        update = add_requirement(requirement_list, **kwargs)
    else:
        update = 0

    return update


def check_add_text(p_text_str_list, **kwargs):
    xml_requirement_list = kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
    text_list = []

    # Create a list with all transition names/aliases already in the xml
    xml_requirement_name_list = orchestrator_object.check_object_name_in_list(xml_requirement_list)
    for elem in p_text_str_list:
        requirement_str = elem[0].replace('"', "")
        text_str = elem[1].replace('"', "")

        if 'shall' in text_str:
            if any(requirement_str in s for s in xml_requirement_name_list):
                for requirement in xml_requirement_list:
                    if requirement_str == requirement.name or requirement_str == requirement.alias:
                        req_subject, req_object, req_conditional, req_temporal = \
                            detect_req_pattern(text_str.lstrip(' '))

                        # Retrieve the subject in object list
                        req_subject_object_list, is_error = retrieve_req_proper_noun_object_list(req_subject,
                                                                                                 **kwargs)

                        if not is_error:
                            if len(req_subject_object_list) > 0:
                                # Take the last one in case of requirement about attribute ( XXX of YYY shall)
                                if isinstance(req_subject_object_list[-1], datamodel.TypeWithAllocatedReqList):
                                    req_subject_object = req_subject_object_list[-1]
                                    Logger.set_info(__name__, f"Requirement {requirement.name} is about "
                                                              f"{req_subject_object.name}")
                                else:
                                    req_subject_object = None
                                    Logger.set_warning(__name__,
                                                       f'Subject "{req_subject}" of the requirement {requirement.name} '
                                                       f'is unknown')
                            else:
                                req_subject_object = None
                                Logger.set_warning(__name__,
                                                   f'Subject "{req_subject}" of the requirement {requirement.name} '
                                                   f'is unknown')

                            # Check if a requirement with the same text already exist
                            sequence_ratio_list = evaluate_text_similarities(req_subject,
                                                                             req_object,
                                                                             req_conditional,
                                                                             req_temporal,
                                                                             **kwargs)

                            req_allocated_object_list = check_requirement_relationship(req_subject_object_list,
                                                                                       req_object,
                                                                                       req_conditional,
                                                                                       req_temporal,
                                                                                       **kwargs)

                            if sequence_ratio_list:
                                similar_requirement_name = max(sequence_ratio_list, key=sequence_ratio_list.get)
                                Logger.set_info(__name__,
                                                f"Requirement {similar_requirement_name} has the same "
                                                f"text (confidence factor: "
                                                f"{sequence_ratio_list[similar_requirement_name]})")
                            else:
                                text_list.append([requirement, text_str.lstrip(' '),
                                                  req_subject_object,
                                                  req_allocated_object_list])
                            # Else do nothing
                        # Else do nothing
                    # Else do nothing
            else:
                Logger.set_error(__name__,
                                 f"The requirement {requirement_str} does not exist")
        else:
            Logger.set_error(__name__,
                             f"text bad formatted: {text_str}")

    if text_list:
        update = add_requirement_text(text_list, **kwargs)
    else:
        update = 0

    return update


def evaluate_text_similarities(p_req_subject, p_req_object, p_req_conditional, p_req_temporal, **kwargs):
    xml_requirement_list = kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
    sequence_ratio_list = {}

    for xml_requirement in xml_requirement_list:
        if xml_requirement.text:
            xml_requirement_subject, xml_requirement_object, xml_requirement_conditional, \
                xml_requirement_temporal = detect_req_pattern(xml_requirement.text)

            sequence_subject = difflib.SequenceMatcher(None,
                                                       xml_requirement_subject,
                                                       p_req_subject)
            sequence_object = difflib.SequenceMatcher(None,
                                                      xml_requirement_object,
                                                      p_req_object)
            sequence_conditional = difflib.SequenceMatcher(None,
                                                           xml_requirement_conditional,
                                                           p_req_conditional)
            sequence_temporal = difflib.SequenceMatcher(None,
                                                        xml_requirement_temporal,
                                                        p_req_temporal)

            if sequence_subject.ratio() == 1 \
                    and sequence_object.ratio() > REQUIREMENT_CONFIDENCE_RATIO \
                    and sequence_conditional.ratio() > REQUIREMENT_CONFIDENCE_RATIO \
                    and sequence_temporal.ratio() > REQUIREMENT_CONFIDENCE_RATIO:
                sequence_ratio_list[xml_requirement.name] = max(sequence_object.ratio(),
                                                                sequence_conditional.ratio(),
                                                                sequence_temporal.ratio())
            # Else do nothing
        # Else do nothing

    return sequence_ratio_list


def detect_req_pattern(p_str_before_modal, p_str_after_modal=None):
    """@ingroup orchestrator
    @anchor detect_req_pattern
    Detect requirement pattern in requirement declaration

    @param[in] p_str_before_modal : full requirement declaration (p_str_after_modal=None) or requirement declaration
    before the modal "shall" (p_str_after_modal!=None)
    @param[in] p_str_after_modal : requirement declaration after the modal "shall"
    @return requirement subject, requirement object, requirement condition, requirement temporality
    """
    if p_str_after_modal is None:
        pattern_shall = re.compile(r"([^. |\n][^.|\n]*) shall (([^.]|\n)*)", re.IGNORECASE).split(p_str_before_modal)
        p_str_before_modal = pattern_shall[1]
        p_str_after_modal = pattern_shall[2]
    # Else do nothing

    # Detect if...then pattern before the requirement subject
    pattern_if = re.compile(r'if (.*?), then (([^.]|\n)*)', re.IGNORECASE).split(p_str_before_modal)
    # Detect when pattern before the requirement subject
    pattern_when = re.compile(r'when (.*?), (([^.]|\n)*)', re.IGNORECASE).split(p_str_before_modal)

    req_object = p_str_after_modal

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
        req_subject = p_str_before_modal

    Logger.set_debug(__name__, f"Requirement subject: {req_subject}")
    Logger.set_debug(__name__, f"Requirement object: {req_object}")
    Logger.set_debug(__name__, f"Requirement conditional: {req_conditional}")
    Logger.set_debug(__name__, f"Requirement temporal: {req_temporal}")

    return req_subject.strip(), req_object.strip(), req_conditional.strip(), req_temporal.strip()


def check_requirement_relationship(p_req_subject_object_list, p_req_object, p_req_conditional, p_req_temporal,
                                   **kwargs):
    """@ingroup orchestrator
    @anchor check_requirement_relationship
    Check requirement relationship between the object related to the requirement subject and the potential objects
    related to requirement object, conditional or temporal parts

    @param[in] p_req_subject_object_list : list of object related to the requirement subject
    @param[in] p_req_object : requirement object string
    @param[in] req_conditional : requirement conditional string
    @param[in] req_temporal : requirement temporal string
    @return list of objects in relation with the object related to the requirement subject
    """
    # Check requirement object content
    implicit_object_list = []
    req_object_list, _ = retrieve_req_proper_noun_object_list(p_req_object, **kwargs)
    if p_req_subject_object_list:
        for req_object_object in req_object_list.copy():
            for req_subject_object in p_req_subject_object_list:
                if not orchestrator_object.check_object_relationship(req_subject_object,
                                                                     req_object_object,
                                                                     p_req_object,
                                                                     **kwargs):
                    # No relationship found in the datamodel between requirement subject and requirement
                    # object. Remove it from the list.
                    if req_object_object in req_object_list:
                        req_object_list.remove(req_object_object)
                    # ELse do nothing
                else:
                    implicit_object = orchestrator_object.retrieve_implicit_object_relationship(req_subject_object,
                                                                                                req_object_object,
                                                                                                p_req_object,
                                                                                                req_object_list,
                                                                                                'transition',
                                                                                                **kwargs)
                    if implicit_object:
                        if implicit_object not in implicit_object_list:
                            implicit_object_list.append(implicit_object)
                        # Else do nothing
                    # Else do nothing

        for implicit_object in implicit_object_list:
            req_object_list.append(implicit_object)
    # Else do nothing

    # Check requirement conditional part if any
    if len(p_req_conditional) > 0:
        req_conditional_object_list, _ = retrieve_req_proper_noun_object_list(p_req_conditional, **kwargs)
        if p_req_subject_object_list:
            for req_conditional_object in req_conditional_object_list:
                for req_subject_object in p_req_subject_object_list:
                    if orchestrator_object.check_object_relationship(req_subject_object,
                                                                     req_conditional_object,
                                                                     p_req_conditional,
                                                                     **kwargs):
                        # Relationship found in the datamodel between requirement subject and requirement
                        # object. Add it to the allocated object list.
                        req_object_list.append(req_conditional_object)
                    # Else do nothing
        # Else do nothing
    # Else do nothing

    # Check requirement temporal part if any
    if len(p_req_temporal) > 0:
        req_temporal_object_list, _ = retrieve_req_proper_noun_object_list(p_req_temporal, **kwargs)
        if p_req_subject_object_list:
            for req_temporal_object in req_temporal_object_list:
                for req_subject_object in p_req_subject_object_list:
                    if orchestrator_object.check_object_relationship(req_subject_object,
                                                                     req_temporal_object,
                                                                     p_req_temporal,
                                                                     **kwargs):
                        # Relationship found in the datamodel between requirement subject and requirement
                        # object. Add it to the allocated object list.
                        req_object_list.append(req_temporal_object)
                    # Else do nothing
        # Else do nothing
    # Else do nothing

    return req_object_list


def add_requirement(p_requirement_list, **kwargs):
    """@ingroup orchestrator
    @anchor add_requirement
    Add requirement list to jarvis data structure

    @param[in] p_requirement_list : list of requirements
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    xml_requirement_list = kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
    output_xml = kwargs['output_xml']

    new_requirement_list = []
    new_allocation_list = []

    update = 0
    # Create requirement names list already in xml
    xml_requirement_name_list = orchestrator_object.check_object_name_in_list(xml_requirement_list)
    # Filter attribute_list, keeping only the ones not already in the xml
    for requirement_item in p_requirement_list:
        if requirement_item[0] not in xml_requirement_name_list:
            new_requirement = datamodel.Requirement()
            new_requirement.set_name(str(requirement_item[0]))
            new_requirement.set_text(str(requirement_item[1]))
            # Generate and set unique identifier of length 10 integers
            new_requirement.set_id(util.get_unique_id())
            # alias is 'none' by default
            new_requirement_list.append(new_requirement)

            # Test if any allocated object is identified in the requirement subject
            if requirement_item[2]:
                for item in requirement_item[2]:
                    item.add_allocated_requirement(new_requirement.id)
                    new_allocation_list.append([item, new_requirement])
            # Else do nothing

            # Test if any allocated object is identified in the requirement object or conditional part or temporal part
            if requirement_item[3]:
                for item in requirement_item[3]:
                    if item:
                        item.add_allocated_requirement(new_requirement.id)
                        new_allocation_list.append([item, new_requirement])
        else:
            Logger.set_info(__name__, requirement_item[0] + " already exists")

    if new_requirement_list:
        output_xml.write_requirement(new_requirement_list)
        if new_allocation_list:
            output_xml.write_object_allocation(new_allocation_list)
        # Else do nothing

        for requirement in new_requirement_list:
            xml_requirement_list.add(requirement)
            Logger.set_info(__name__,
                            requirement.name + " is a requirement")

        for elem in new_allocation_list:
            Logger.set_info(__name__,
                            f"{elem[1].__class__.__name__} {elem[1].name} is satisfied by "
                            f"{elem[0].__class__.__name__} {elem[0].name}")

            # Check for potential req parent in allocated obj parent
            if hasattr(elem[0], 'parent'):
                if elem[0].parent:
                    if hasattr(elem[0].parent, 'allocated_req_list'):
                        update_requirement_link(elem[0].parent, elem[1], **kwargs)
                    # Else do nothing
                # Else do nothing
            # Else do nothing

        update = 1
    # Else do nothing

    return update


def add_requirement_text(p_text_list, **kwargs):
    output_xml = kwargs['output_xml']
    update = 0

    for text_item in p_text_list:
        new_allocation_list = []
        # Test if allocated object is identified in the requirement subject
        if text_item[2]:
            text_item[2].add_allocated_requirement(text_item[0].id)
            new_allocation_list.append([text_item[2], text_item[0]])
        # Else do nothing

        # Test if allocated object is identified in the requirement object or conditional part or temporal part
        if text_item[3]:
            for item in text_item[3]:
                if item:
                    item.add_allocated_requirement(text_item[0].id)
                    new_allocation_list.append([item, text_item[0]])
                # Else do nothing
        # Else do nothing

        output_xml.write_requirement_text([[text_item[0], text_item[1]]])
        Logger.set_info(__name__,
                        f"{text_item[0].name} text is {text_item[1]}")

        if new_allocation_list:
            output_xml.write_object_allocation(new_allocation_list)

            for elem in new_allocation_list:
                Logger.set_info(__name__,
                                f"{elem[1].__class__.__name__} {elem[1].name} is satisfied by "
                                f"{elem[0].__class__.__name__} {elem[0].name}")

                # Check for potential req parent in allocated obj parent
                if hasattr(elem[0], 'parent'):
                    if elem[0].parent:
                        if hasattr(elem[0].parent, 'allocated_req_list'):
                            update_requirement_link(elem[0].parent, elem[1], **kwargs)
                        # Else do nothing
                    # Else do nothing
                # Else do nothing

        update = 1

    return update


def update_requirement_link(p_allocated_parent, p_requirement, **kwargs):
    """@ingroup orchestrator
    @anchor update_requirement_link
    Update the requirement link in jarvis data structure according to object parent it has been allocated to

    @param[in] p_allocated_parent : object parent the requirement has been allocated to
    @param[in] p_requirement : requirement under consideration
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    sequence_ratio_list = {}
    sequence_req_list = {}
    for req in p_allocated_parent.allocated_req_list:
        for xml_req in kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]:
            if xml_req.id == req.id:
                parent_req_object = retrieve_requirement_object(xml_req.text.split("shall")[1])
                req_object = retrieve_requirement_object(p_requirement.text.split("shall")[1])
                sequence = difflib.SequenceMatcher(None, parent_req_object, req_object)
                Logger.set_debug(__name__, f"{parent_req_object} from requirement {xml_req.id} compared with "
                                           f"{req_object} from requirement {p_requirement.id} - confidence factor: "
                                           f"{sequence.ratio()}")

                if sequence.ratio() > REQUIREMENT_CONFIDENCE_RATIO:
                    sequence_ratio_list[xml_req.name] = sequence.ratio()
                    sequence_req_list[xml_req.name] = xml_req

    if sequence_ratio_list:
        similar_requirement_name = max(sequence_ratio_list, key=sequence_ratio_list.get)
        Logger.set_info(__name__, f"Requirement {similar_requirement_name} deals with the same object "
                                  f"(confidence factor: {sequence_ratio_list[similar_requirement_name]})")

        sequence_req_list[similar_requirement_name].add_child(p_requirement)
        p_requirement.set_parent(sequence_req_list[similar_requirement_name])

        output_xml = kwargs['output_xml']
        output_xml.write_object_child([[sequence_req_list[similar_requirement_name], p_requirement]])

        Logger.set_info(__name__, f"{p_requirement.__class__.__name__} {p_requirement.name} derives from "
                                  f"{sequence_req_list[similar_requirement_name].__class__.__name__} "
                                  f"{similar_requirement_name}")


def retrieve_requirement_object(p_requirement_object_str):
    """@ingroup orchestrator
    @anchor retrieve_requirement_object
    Retrieve requirement object from requirement text

    @param[in] p_requirement_object_str : requirement text
    @return requirement object
    """
    req_object = ''
    token_list = nltk.word_tokenize(p_requirement_object_str)
    tag_list = nltk.pos_tag(token_list)

    for word, tag in tag_list[1:]:
        if tag == NOUN_SINGULAR_TAG or tag == NOUN_PLURAL_TAG:
            req_object += word + " "
        elif tag == COORDINATE_TAG or tag == SUBORDINATE_TAG:
            break

    return req_object.strip()


def check_add_derived(p_str_list, **kwargs):
    """@ingroup orchestrator
    @anchor check_add_derived
    Check list of requirement derivation link requests and add them to jarvis data structure

    @param[in] p_str_list : list of requirement derivation link requests
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    derived_list = []
    cleaned_derived_str_list = util.cut_tuple_list(p_str_list)
    for elem in cleaned_derived_str_list:
        derived_req_obj = orchestrator_object.retrieve_object_by_name(elem[0], **{
            XML_DICT_KEY_8_REQUIREMENT_LIST: kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
        })

        parent_req_obj = orchestrator_object.retrieve_object_by_name(elem[1], **{
            XML_DICT_KEY_8_REQUIREMENT_LIST: kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
        })

        if not derived_req_obj:
            Logger.set_error(__name__, f"Requirement {elem[0]} not found")
        elif not parent_req_obj:
            Logger.set_error(__name__, f"Requirement {elem[1]} not found")
        else:
            if not any(child_req.id == derived_req_obj.id for child_req in parent_req_obj.child_list):
                parent_req_obj.add_child(derived_req_obj)
                derived_req_obj.set_parent(parent_req_obj)
                derived_list.append([parent_req_obj, derived_req_obj])
            else:
                Logger.set_info(__name__,
                                f"{derived_req_obj.__class__.__name__} {derived_req_obj.name} already derives from "
                                f"{parent_req_obj.__class__.__name__} {parent_req_obj.name}")

    if derived_list:
        output_xml = kwargs['output_xml']
        output_xml.write_object_child(derived_list)

        for elem in derived_list:
            Logger.set_info(__name__,
                            f"{elem[1].__class__.__name__} {elem[1].name} derives from "
                            f"{elem[0].__class__.__name__} {elem[0].name}")

        update = 1
    else:
        update = 0

    return update


def retrieve_req_proper_noun_object_list(p_req_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_req_proper_noun_object_list
    Retrieve list of objects named as proper nouns found in requirement text

    @param[in] p_req_str : requirement string
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    req_object_list = []

    # Try to retrieve the object with the whole requirement string
    req_object = orchestrator_object.retrieve_object_by_name(p_req_str, **kwargs)

    if req_object:
        req_object_list.append(req_object)
        is_error = False
    else:
        req_proper_noun_list, is_error = retrieve_req_proper_noun_list(p_req_str)

        if not is_error:
            for req_proper_noun in req_proper_noun_list:
                req_object = orchestrator_object.retrieve_object_by_name(req_proper_noun, **kwargs)
                if req_object:
                    if req_object not in req_object_list:
                        req_object_list.append(req_object)
                    # Else do nothing
                # Else do nothing
        # ELse do nothing

    return req_object_list, is_error


def retrieve_req_proper_noun_list(p_req_str, p_is_noun_split=True):
    """@ingroup orchestrator
    @anchor retrieve_req_proper_noun_list
    Retrieve list of proper nouns found in requirement text

    @param[in] p_req_str : requirement text
    @param[in] p_is_noun_split : indicates if proper noun needs to be split (TRUE) or not (FALSE)
    @param[in] kwargs : jarvis data structure
    @return list of proper nouns
    """
    req_proper_noun_list = []
    is_error = False

    is_previous_proper_noun_singular_tag = False
    is_previous_proper_noun = False
    is_proper_noun = False
    proper_noun_str = ''
    is_previous_function_name = False
    is_function_name = False
    function_name_str = ''
    token_list = nltk.word_tokenize(p_req_str)
    tag_list = nltk.pos_tag(token_list)
    index = 0
    for tag in tag_list:
        previous_tag_list = []
        if index > 0:
            for i in range(0, index):
                previous_tag_list.append(tag_list[i])
        # Else do nothing

        next_tag_list = []
        if index < len(tag_list) - 1:
            for i in range(index + 1, len(tag_list)):
                next_tag_list.append(tag_list[i])
        # Else do nothing

        Logger.set_debug(__name__, f'tag: {tag}')

        is_proper_noun, is_previous_proper_noun_singular_tag, is_function_name, is_error = (
            check_proper_noun_tag(tag, previous_tag_list, next_tag_list, is_proper_noun,
                                  is_previous_proper_noun_singular_tag, is_function_name))

        Logger.set_debug(__name__, f'previous_tag_list: {previous_tag_list}')
        Logger.set_debug(__name__, f'next_tag_list: {next_tag_list}')
        Logger.set_debug(__name__, f'is_proper_noun: {is_proper_noun}')
        Logger.set_debug(__name__, f'is_previous_proper_noun_singular_tag: {is_previous_proper_noun_singular_tag}')
        Logger.set_debug(__name__, f'is_function_name: {is_function_name}')
        Logger.set_debug(__name__, f'is_error: {is_error}')

        if is_error:
            break
        else:
            if is_proper_noun:
                is_previous_proper_noun = True
                proper_noun_str = proper_noun_str + ' ' + tag[0]
            # Else do nothing

            if is_function_name:
                is_previous_function_name = True
                function_name_str = function_name_str + ' ' + tag[0]
            # Else do nothing

            if not is_proper_noun and is_previous_proper_noun:
                proper_noun_str = proper_noun_str.strip().replace('( ', '(').replace(' )', ')') \
                    .replace('[ ', '[').replace(' ]', ']')
                Logger.set_debug(__name__, f'proper_noun_str: {proper_noun_str.strip()}')
                req_proper_noun_list.append(proper_noun_str)

                if p_is_noun_split:
                    proper_noun_list = proper_noun_str.split(' ')
                    for proper_noun in proper_noun_list:
                        req_proper_noun_list.append(proper_noun)
                # Else do nothing

                proper_noun_str = ''
                is_previous_proper_noun = False
            # Else do nothing

            if not is_function_name and is_previous_function_name:
                Logger.set_debug(__name__, f'function_name_str: {function_name_str.strip()}')
                req_proper_noun_list.append(function_name_str.strip())
                function_name_str = ''
                is_previous_function_name = False
            # Else do nothing

            index = index + 1
    # Else do nothing

    if is_proper_noun:
        proper_noun_str = proper_noun_str.strip().replace('( ', '(').replace(' )', ')')\
            .replace('[ ', '[').replace(' ]', ']')
        Logger.set_debug(__name__, f'proper_noun_str: {proper_noun_str.strip()}')
        req_proper_noun_list.append(proper_noun_str)

        if p_is_noun_split:
            proper_noun_list = proper_noun_str.split(' ')
            for proper_noun in proper_noun_list:
                req_proper_noun_list.append(proper_noun)
        # Else do nothing
    # Else do nothing

    if is_function_name:
        Logger.set_debug(__name__, f'function_name_str: {function_name_str.strip()}')
        req_proper_noun_list.append(function_name_str.strip())
    # Else do nothing

    return req_proper_noun_list, is_error


def check_proper_noun_tag(p_tag, p_previous_tag_list, p_next_tag_list, is_proper_noun,
                          is_previous_proper_noun_singular_tag, is_function_name, p_is_silent=False):
    is_error = False

    if p_tag[1] == PROPER_NOUN_SINGULAR_TAG or p_tag[1] == PRONOUN_PERSONAL_TAG:
        # sign '=' is tagged as PROPER_NOUN_SINGULAR_TAG
        if p_tag[0] != '=':
            is_proper_noun = True
            is_previous_proper_noun_singular_tag = True
        # Else do nothing
    elif p_tag[1] == NOUN_SINGULAR_TAG or p_tag[1] == NOUN_PLURAL_TAG:
        # sign '%' is tagged as NOUN_SINGULAR_TAG
        if p_tag[0] != '%':
            if not is_function_name:
                is_proper_noun = not is_previous_proper_noun_singular_tag
                is_previous_proper_noun_singular_tag = False
            # Else do nothing
        # Else do nothing
    elif p_tag[1] == ADJECTIVE_TAG:
        is_previous_proper_noun_singular_tag = False
        if p_next_tag_list:
            if p_next_tag_list[0][1] == NOUN_SINGULAR_TAG or p_next_tag_list[0][1] == NOUN_PLURAL_TAG:
                # sign '%' is tagged as NOUN_SINGULAR_TAG
                if p_tag[0] != '%':
                    if not is_function_name:
                        is_proper_noun = not is_previous_proper_noun_singular_tag
    elif p_tag[1] == DETERMINER_TAG:
        is_previous_proper_noun_singular_tag = False
        if p_tag[0] == 'a':
            if p_next_tag_list:
                if p_next_tag_list[0][1] != NOUN_SINGULAR_TAG:
                    # case of 'a' used as a noun
                    is_proper_noun = True
                # Else do nothing
            else:
                # case of 'a' used as a noun
                is_proper_noun = True
    elif p_tag[1] == TO_TAG and not is_function_name:
        if p_previous_tag_list:
            if p_previous_tag_list[-1][1] == NOUN_SINGULAR_TAG or p_previous_tag_list[-1][1] == NOUN_PLURAL_TAG:
                if len(p_previous_tag_list) > 1:
                    if p_previous_tag_list[-2][1] != VERB_TAG and p_previous_tag_list[-2][1] != VERB_PAST_TAG:
                        is_previous_proper_noun_singular_tag = False
                        is_function_name = True
                    # Else do nothing
                else:
                    is_previous_proper_noun_singular_tag = False
                    is_function_name = True
            else:
                is_function_name = False
        # Else do nothing
    elif p_tag[1] == VERB_TAG:
        if len(p_tag[0]) > 1:
            if p_previous_tag_list:
                if p_previous_tag_list[-1][1] == NOUN_SINGULAR_TAG or p_previous_tag_list[-1][1] == NOUN_PLURAL_TAG:
                    is_function_name = False
                elif p_previous_tag_list[-1][1] == TO_TAG and not is_function_name:
                    # Could be a proper noun
                    is_previous_proper_noun_singular_tag = False
                    is_proper_noun = True
                elif p_previous_tag_list[-1][1] != TO_TAG and not p_is_silent:
                    Logger.set_error(__name__,
                                     f'Requirement bad formatted: "{p_tag[0]}" is considered as a verb '
                                     f'(tagged as "{p_tag[1]}")')
                    is_error = True
                # Else do nothing
            # Else do nothing
        else:
            # Case of a single letter, so it is a proper noun instead of a verb
            is_previous_proper_noun_singular_tag = False
            is_proper_noun = True
    elif p_tag[1] == VERB_PAST_TAG:
        if len(p_tag[0]) > 1:
            if p_previous_tag_list:
                if p_previous_tag_list[-1][1] == NOUN_SINGULAR_TAG or p_previous_tag_list[-1][1] == NOUN_PLURAL_TAG \
                        or p_previous_tag_list[-1][1] == ADJECTIVE_TAG or p_previous_tag_list[-1][1] == DETERMINER_TAG:
                    # Could be a proper noun
                    is_previous_proper_noun_singular_tag = False
                    is_proper_noun = True
                # Else do nothing
            # Else do nothing
        else:
            # Case of a single letter, so it is a proper noun instead of a verb
            is_previous_proper_noun_singular_tag = False
            is_proper_noun = True
    elif p_tag[1] == SUBORDINATE_TAG or p_tag[1] == COORDINATE_TAG or p_tag[1] == SEMICOLON_TAG:
        is_previous_proper_noun_singular_tag = False
        is_proper_noun = False
        is_function_name = False
    # Else do nothing

    return is_proper_noun, is_previous_proper_noun_singular_tag, is_function_name, is_error


def retrieve_req_subject_object(p_req_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_req_subject_object
    Retrieve the object named as proper noun found for requirement subject

    @param[in] p_req_str : requirement text
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    req_subject_object = None

    req_subject, _, _, _ = detect_req_pattern(p_req_str)

    # Retrieve the subject in object list
    req_subject_object_list, _ = retrieve_req_proper_noun_object_list(req_subject, **kwargs)

    if len(req_subject_object_list) > 0:
        # Take the last one in case of requirement about attribute ( XXX of YYY shall)
        req_subject_object = req_subject_object_list[-1]
    # Else do nothing

    return req_subject_object


def retrieve_req_object_object_list(p_req_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_req_object_object_list
    Retrieve list of objects named as proper nouns found for requirement object

    @param[in] p_req_str : requirement text
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    _, req_object, _, _ = detect_req_pattern(p_req_str)

    req_object_object_list, _ = retrieve_req_proper_noun_object_list(req_object, **kwargs)

    return req_object_object_list


def retrieve_req_condition_object_list(p_req_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_req_condition_object_list
    Retrieve list of objects named as proper nouns found for requirement condition

    @param[in] p_req_str : requirement text
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    _, _, req_condition, _ = detect_req_pattern(p_req_str)

    req_object_object_list, _ = retrieve_req_proper_noun_object_list(req_condition, **kwargs)

    return req_object_object_list


def retrieve_req_temporal_object_list(p_req_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_req_temporal_object_list
    Retrieve list of objects named as proper nouns found for requirement temporal condition

    @param[in] p_req_str : requirement text
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    _, _, _, req_temporal = detect_req_pattern(p_req_str)

    req_object_object_list, _ = retrieve_req_proper_noun_object_list(req_temporal, **kwargs)

    return req_object_object_list


def analyze_requirement(**kwargs):
    """@ingroup orchestrator
    @anchor analyze_requirement
    Analyze requirements against jarvis data structure

    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    update = 0
    xml_requirement_list = kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
    output_xml = kwargs['output_xml']

    for xml_requirement in xml_requirement_list:
        # Check if the requirement subject is known
        req_subject_object = retrieve_req_subject_object(xml_requirement.text, **kwargs)

        req_subject_object_analyzed = None
        if req_subject_object is None:
            # Ask user to create the object in the jarvis data structure
            answer, _ = handler_question.question_to_user(f"Do you want to create an object for the subject of "
                                                          f"the requirement: {xml_requirement.text} "
                                                          f"(name: {xml_requirement.name}) ? (Y/N)")

            if answer.lower() == "y":
                # Check if data type is in the requirement subject
                req_subject, _, _, _ = detect_req_pattern(xml_requirement.text)
                req_proper_noun_list, is_error = retrieve_req_proper_noun_list(req_subject)

                if not is_error:
                    if len(req_proper_noun_list) > 0:
                        req_subject_type = None
                        req_subject_name = req_subject
                        for req_proper_noun in req_proper_noun_list:
                            specific_type, base_type = orchestrator_object.retrieve_type(req_proper_noun, True,
                                                                                         **kwargs)
                            if specific_type is not None:
                                req_subject_type = specific_type
                                req_subject_name = req_subject_name.replace(req_subject_type, "")
                                break
                            elif base_type is not None:
                                req_subject_type = base_type
                                req_subject_name = req_subject_name.replace(req_subject_type, "")
                                break
                            # Else do nothing

                        if req_subject_type is None:
                            # Take the last one in case of requirement about attribute ( XXX of YYY shall)
                            req_subject_name = req_proper_noun_list[-1]
                            req_subject_type, _ = handler_question.question_to_user(f'What is the type '
                                                                                    f'of "{req_subject_name}" ?')
                        # Else do nothing

                        update = orchestrator_object.check_add_specific_obj_by_type(
                            [[req_subject_name, req_subject_type]],
                            **kwargs)

                        req_subject_object_analyzed = orchestrator_object.retrieve_object_by_name(req_subject, **kwargs)
                    # Else do nothing
                # Else do nothing
            elif answer == "q":
                break
            else:
                Logger.set_warning(__name__,
                                   f"Subject of requirement: {xml_requirement.text} (name: {xml_requirement.name}) "
                                   f"is not defined in the system analysis")
        # Else do nothing

        # Check if user does not abort (answer == "q")
        if req_subject_object_analyzed is not None:
            if xml_requirement.id not in req_subject_object_analyzed.allocated_req_list:
                req_subject_object_analyzed.add_allocated_requirement(xml_requirement.id)
                output_xml.write_object_allocation([[req_subject_object_analyzed, xml_requirement]])

                Logger.set_info(__name__,
                                f"{xml_requirement.__class__.__name__} {xml_requirement.name} is satisfied by "
                                f"{req_subject_object_analyzed.__class__.__name__} {req_subject_object_analyzed.name}")

                # Check for potential req parent in allocated obj parent
                if hasattr(req_subject_object_analyzed, 'parent'):
                    if req_subject_object_analyzed.parent:
                        if hasattr(req_subject_object_analyzed.parent, 'allocated_req_list'):
                            update_requirement_link(req_subject_object_analyzed.parent, xml_requirement, **kwargs)

                update = 1
            # Else do nothing
        # Else do nothing

        # Check if objects are already identified in requirement object
        # Always ask user to create objects (even if there are some already identified)
        req_object_object_list = retrieve_req_object_object_list(xml_requirement.text, **kwargs)
        for req_object_object in req_object_object_list:
            Logger.set_info(__name__,
                            f'{xml_requirement.__class__.__name__} {xml_requirement.name} is satisfied by '
                            f'{req_object_object.__class__.__name__} {req_object_object.name}')

        req_object_list = []
        # Ask user to create the object in the jarvis data structure
        answer, _ = handler_question.question_to_user(f"Do you want to create object(s) for the object of "
                                                      f"the requirement: {xml_requirement.text} "
                                                      f"(name: {xml_requirement.name}) ? (Y/N)")

        if answer.lower() == "y":
            # Check if data type is in the requirement object
            _, req_object, _, _ = detect_req_pattern(xml_requirement.text)
            req_proper_noun_list, is_error = retrieve_req_proper_noun_list(req_object, False)

            if not is_error:
                if len(req_proper_noun_list) > 0:
                    type_name_list = []
                    for idx_req_proper_noun in range(0, len(req_proper_noun_list)):
                        req_proper_noun_split = req_proper_noun_list[idx_req_proper_noun].split(" ")
                        for idx_req_proper_noun_split in range(0, len(req_proper_noun_split)):
                            specific_type, base_type = orchestrator_object.retrieve_type(
                                req_proper_noun_split[idx_req_proper_noun_split],
                                True,
                                **kwargs)
                            # If we have a type, then next proper noun is the object name related to the type
                            if specific_type is not None:
                                if idx_req_proper_noun_split < len(req_proper_noun_split):
                                    type_name_list.append([specific_type,
                                                           req_proper_noun_split[idx_req_proper_noun_split + 1]])
                                    req_proper_noun_split.remove(
                                        req_proper_noun_split[idx_req_proper_noun_split + 1])
                                elif idx_req_proper_noun < len(req_proper_noun_list):
                                    type_name_list.append([specific_type,
                                                           req_proper_noun_list[idx_req_proper_noun + 1]])
                                    req_proper_noun_list.remove(req_proper_noun_list[idx_req_proper_noun + 1])
                                # Else do nothing
                            elif base_type is not None:
                                if idx_req_proper_noun_split < len(req_proper_noun_split):
                                    type_name_list.append([base_type,
                                                           req_proper_noun_split[idx_req_proper_noun_split + 1]])
                                    req_proper_noun_split.remove(
                                        req_proper_noun_split[idx_req_proper_noun_split + 1])
                                elif idx_req_proper_noun < len(req_proper_noun_list):
                                    type_name_list.append([base_type, req_proper_noun_list[idx_req_proper_noun + 1]])
                                    req_proper_noun_list.remove(req_proper_noun_list[idx_req_proper_noun + 1])
                                # Else do nothing
                            else:
                                wanted_object = orchestrator_object.retrieve_object_by_name(
                                    req_proper_noun_split[idx_req_proper_noun_split], **kwargs)
                                if not wanted_object:
                                    if idx_req_proper_noun_split == len(req_proper_noun_split)-1:
                                        type_name_list.append([None, req_proper_noun_list[idx_req_proper_noun]])
                                    # Else do nothing
                                else:
                                    # Continue with next proper noun
                                    break
                            # Else do nothing

                    for type_name in type_name_list:
                        if type_name[0] is None:
                            req_object_type, _ = handler_question.question_to_user(f'What is the type '
                                                                                   f'of "{type_name[1]}" ?')
                        else:
                            req_object_type = type_name[0]

                        if req_object_type == "q":
                            break
                        else:
                            update = orchestrator_object.check_add_specific_obj_by_type(
                                [[type_name[1], req_object_type]],
                                **kwargs)

                            req_object_list.append(orchestrator_object.retrieve_object_by_name(type_name[1], **kwargs))
                # Else do nothing
            # Else do nothing
        elif answer == "q":
            break
        else:
            Logger.set_warning(__name__,
                               f"Object of requirement: {xml_requirement.text} (name: {xml_requirement.name}) "
                               f"is not defined in the system analysis")

        # Check if user does not abort (answer == "q")
        if len(req_object_list) > 0:
            for req_object in req_object_list:
                if xml_requirement.id not in req_object.allocated_req_list:
                    req_object.add_allocated_requirement(xml_requirement.id)
                    output_xml.write_object_allocation([[req_object, xml_requirement]])

                    Logger.set_info(__name__,
                                    f"{xml_requirement.__class__.__name__} {xml_requirement.name} is satisfied by "
                                    f"{req_object.__class__.__name__} {req_object.name}")

                    # Check for potential req parent in allocated obj parent
                    if hasattr(req_object, 'parent'):
                        if req_object.parent:
                            if hasattr(req_object.parent, 'allocated_req_list'):
                                update_requirement_link(req_object.parent, xml_requirement, **kwargs)

                    update = 1
                # Else do nothing
        # Else do nothing
    return update
