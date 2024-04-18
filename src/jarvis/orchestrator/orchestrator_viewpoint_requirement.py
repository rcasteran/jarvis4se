"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re
import nltk
import difflib

# Modules
import datamodel
from . import orchestrator_object
from tools import Logger
from jarvis.handler import handler_question
from jarvis.query import question_answer
from jarvis import util

# Constants
REQUIREMENT_CONFIDENCE_RATIO = 0.78
NOUN_SINGULAR_TAG = "NN"
NOUN_PLURAL_TAG = "NNS"
PROPER_NOUN_SINGULAR_TAG = "NNP"
DETERMINER_TAG = "DT"
ADJECTIVE_TAG = "JJ"
SUBORDINATE_TAG = "IN"
COORDINATE_TAG = "CC"
PRONOUN_PERSONAL_TAG = "PRP"


def check_add_requirement(p_str_list, **kwargs):
    """@ingroup jarvis
    @anchor check_add_requirement
    Check list of requirement declarations before adding them to jarvis data structure

    @param[in] p_str_list : list of requirements declaration
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    requirement_list = []

    for p_str in p_str_list:
        req_subject, req_object, req_conditional, req_temporal = detect_req_pattern(p_str[0], p_str[1])

        # Retrieve the subject in object list
        req_subject_object_list, is_error = retrieve_req_proper_noun_object(req_subject, p_is_subject=True, **kwargs)

        if not is_error:
            req_subject_object = None
            for obj in req_subject_object_list:
                if obj:
                    req_subject_object = obj

            if req_subject_object:
                Logger.set_info(__name__, f"Requirement identified about {req_subject_object.name}: "
                                          f"{p_str[0]} shall {p_str[1]}")
            else:
                Logger.set_info(__name__, f"Requirement identified: {p_str[0]} shall {p_str[1]}")
                Logger.set_warning(__name__,
                                   f'Subject "{req_subject}" of the requirement is unknown')

            # Check if a requirement with the same description already exist
            xml_requirement_list = kwargs['xml_requirement_list']
            sequence_ratio_list = {}
            for xml_requirement in xml_requirement_list:
                sequence_subject = difflib.SequenceMatcher(None,
                                                           detect_req_pattern(xml_requirement.description)[0],
                                                           detect_req_pattern(p_str[0], 'dummy')[0])
                sequence_object = difflib.SequenceMatcher(None,
                                                          detect_req_pattern(xml_requirement.description)[1],
                                                          detect_req_pattern('dummy', p_str[1])[1])

                if sequence_subject.ratio() == 1 and sequence_object.ratio() > REQUIREMENT_CONFIDENCE_RATIO:
                    sequence_ratio_list[xml_requirement.name] = sequence_object.ratio()
                # Else do nothing

            if sequence_ratio_list:
                similar_requirement_name = max(sequence_ratio_list, key=sequence_ratio_list.get)
                Logger.set_info(__name__,
                                f"Requirement {similar_requirement_name} has the same "
                                f"description (confidence factor: {sequence_ratio_list[similar_requirement_name]})")
            else:
                # Check requirement object content
                req_allocated_object_list, _ = retrieve_req_proper_noun_object(req_object, **kwargs)
                if req_subject_object:
                    for req_object_object in req_allocated_object_list.copy():
                        if req_object_object:
                            if not orchestrator_object.check_object_relationship(req_subject_object,
                                                                                 req_object_object,
                                                                                 req_object,
                                                                                 **kwargs):
                                # No relationship found in the datamodel between requirement subject and requirement
                                # object. Remove it from the list.
                                req_allocated_object_list.remove(req_object_object)
                            # Else do nothing
                        else:
                            req_allocated_object_list.remove(req_object_object)

                # Check requirement condition if any
                if len(req_conditional) > 0:
                    req_conditional_object_list, _ = retrieve_req_proper_noun_object(req_conditional, **kwargs)
                    if req_subject_object:
                        for req_conditional_object in req_conditional_object_list.copy():
                            if req_conditional_object:
                                if orchestrator_object.check_object_relationship(req_subject_object,
                                                                                 req_conditional_object,
                                                                                 req_conditional,
                                                                                 **kwargs):
                                    # Relationship found in the datamodel between requirement subject and requirement
                                    # object. Add it to the allocated object list.
                                    req_allocated_object_list.append(req_conditional_object)
                                # Else do nothing
                            # Else do nothing

                answer = handler_question.question_to_user(f"Please give a requirement summary: ")
                if len(answer) > 0:
                    existing_object = question_answer.check_get_object(answer, **kwargs)
                    if existing_object:
                        if isinstance(existing_object.type, datamodel.BaseType):
                            if str(existing_object.type) != "Requirement":
                                Logger.set_error(__name__,
                                                 f"{existing_object.type} with the name "
                                                 f"{answer} already exists")
                            else:
                                requirement_list.append([answer, f"{p_str[0]} shall {p_str[1]}",
                                                         existing_object, req_subject_object, req_allocated_object_list])
                        else:
                            if str(existing_object.type.name) != "Requirement":
                                Logger.set_error(__name__,
                                                 f"{existing_object.type.name} with the name "
                                                 f"{answer} already exists")
                            else:
                                requirement_list.append([answer, f"{p_str[0]} shall {p_str[1]}",
                                                         existing_object, req_subject_object, req_allocated_object_list])
                    else:
                        requirement_list.append([answer, f"{p_str[0]} shall {p_str[1]}", None,
                                                 req_subject_object, req_allocated_object_list])
                else:
                    Logger.set_error(__name__, "No summary entered for identified requirement")

    if requirement_list:
        update = add_requirement(requirement_list, **kwargs)
    else:
        update = 0

    return update


def detect_req_pattern(p_str_before_modal, p_str_after_modal=None):
    """@ingroup jarvis
    @anchor detect_req_pattern
    Detect requirement pattern in requirement declaration

    @param[in] p_str_before_modal : full requirement declaration (p_str_after_modal=None) or requirement declaration
    before the modal "shall" (p_str_after_modal!=None)
    @param[in] p_str_after_modal : requirement declaration after the modal "shall"
    @return requirement subject, requirement object, requirement condition, requirement temporality
    """
    if p_str_after_modal is None:
        pattern_shall = re.compile(r'([^. |\n][^.|\n]*) shall ([^.|\n]*)', re.IGNORECASE).split(p_str_before_modal)
        p_str_before_modal = pattern_shall[1]
        p_str_after_modal = pattern_shall[2]
    # Else do nothing

    # Detect if...then pattern before the requirement subject
    pattern_if = re.compile(r'if (.*?), then ([^.|\n]*)', re.IGNORECASE).split(p_str_before_modal)
    # Detect when pattern before the requirement subject
    pattern_when = re.compile(r'when (.*?), ([^.|\n]*)', re.IGNORECASE).split(p_str_before_modal)

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
    Logger.set_debug(__name__, f"Requirement is conditional: {req_conditional}")
    Logger.set_debug(__name__, f"Requirement is temporal: {req_temporal}")

    return req_subject, req_object, req_conditional, req_temporal


def add_requirement(p_requirement_list, **kwargs):
    """@ingroup jarvis
    @anchor add_requirement
    Add requirement list to jarvis data structure

    @param[in] p_requirement_list : list of requirements
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    xml_requirement_list = kwargs['xml_requirement_list']
    output_xml = kwargs['output_xml']

    new_requirement_list = []
    new_allocation_list = []

    update = 0
    # Create requirement names list already in xml
    xml_requirement_name_list = question_answer.get_objects_names(xml_requirement_list)
    # Filter attribute_list, keeping only the ones not already in the xml
    for requirement_item in p_requirement_list:
        if requirement_item[0] not in xml_requirement_name_list:
            new_requirement = datamodel.Requirement()
            new_requirement.set_name(str(requirement_item[0]))
            new_requirement.set_description(str(requirement_item[1]))
            # Generate and set unique identifier of length 10 integers
            new_requirement.set_id(util.get_unique_id())
            # alias is 'none' by default
            new_requirement_list.append(new_requirement)

            # Test if allocated object is identified in the requirement subject
            if requirement_item[3]:
                requirement_item[3].add_allocated_requirement(new_requirement)
                new_allocation_list.append([requirement_item[3], new_requirement])
            # Else do nothing

            # Test if allocated object is identified in the requirement object
            if requirement_item[4]:
                for item in requirement_item[4]:
                    if item:
                        item.add_allocated_requirement(new_requirement)
                        new_allocation_list.append([item, new_requirement])
        else:
            Logger.set_info(__name__, requirement_item[0] + " already exists")

    if new_requirement_list:
        output_xml.write_requirement(new_requirement_list)
        if new_allocation_list:
            output_xml.write_object_allocation(new_allocation_list)

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

        update = 1

    return update


def check_add_allocation(p_str_list, **kwargs):
    """@ingroup jarvis
    @anchor check_add_allocation
    Check list of requirement allocation declaration and add them to jarvis data structure

    @param[in] p_str_list : list of requirement allocation declaration
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
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

                # Check for potential req parent in allocated obj parent
                if alloc_obj.parent:
                    if hasattr(alloc_obj.parent, 'allocated_req_list'):
                        update_requirement_link(alloc_obj.parent, req_obj, **kwargs)
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


def update_requirement_link(p_allocated_parent, p_requirement, **kwargs):
    """@ingroup jarvis
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
        for xml_req in kwargs['xml_requirement_list']:
            if xml_req.id == req.id:
                parent_req_object = retrieve_requirement_object(xml_req.description.split("shall")[1])
                req_object = retrieve_requirement_object(p_requirement.description.split("shall")[1])
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
    """@ingroup jarvis
    @anchor retrieve_requirement_object
    Retrieve requirement object from requirement description

    @param[in] p_requirement_object_str : requirement description
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
    """@ingroup jarvis
    @anchor check_add_derived
    Check list of requirement derivation link requests and add them to jarvis data structure

    @param[in] p_str_list : list of requirement derivation link requests
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    derived_list = []
    cleaned_derived_str_list = util.cut_tuple_list(p_str_list)
    for elem in cleaned_derived_str_list:
        derived_req_obj = question_answer.check_get_object(elem[0],
                                                           **{'xml_requirement_list': kwargs['xml_requirement_list']})

        parent_req_obj = question_answer.check_get_object(elem[1],
                                                          **{'xml_requirement_list': kwargs['xml_requirement_list']})

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


def retrieve_req_proper_noun_object(p_req_str, p_is_subject=False, **kwargs):
    """@ingroup jarvis
    @anchor retrieve_req_proper_noun_object
    Retrieve list of objects named as proper nouns found in requirement description

    @param[in] p_req_str : requirement description
    @param[in] p_is_subject : indicate if list of objects named as proper nouns concern the requirement subject
    only (TRUE) or not (FALSE)
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    req_string_object_list = []
    is_error = False

    is_previous_proper_noun_singular_tag = False
    token_list = nltk.word_tokenize(p_req_str)
    tag_list = nltk.pos_tag(token_list)
    for tag in tag_list:
        if tag[1] == PROPER_NOUN_SINGULAR_TAG or tag[1] == PRONOUN_PERSONAL_TAG:
            # sign '=' is tagged as PROPER_NOUN_SINGULAR_TAG
            if tag[0] != '=':
                req_string_object_list.append(question_answer.check_get_object(tag[0], **kwargs))
                is_previous_proper_noun_singular_tag = True
        elif tag[1] == NOUN_SINGULAR_TAG or tag[1] == NOUN_PLURAL_TAG:
            if not is_previous_proper_noun_singular_tag:
                req_string_object_list.append(question_answer.check_get_object(tag[0], **kwargs))
            # Else dismiss the noun

            is_previous_proper_noun_singular_tag = False
        elif tag[1] == DETERMINER_TAG or tag[1] == ADJECTIVE_TAG:
            is_previous_proper_noun_singular_tag = False
        elif tag[1] != DETERMINER_TAG and p_is_subject:
            Logger.set_error(__name__,
                             f"Requirement bad formatted: {tag[0]} is not a determiner nor an adjective nor a noun")
            is_error = True
            break

    return req_string_object_list, is_error


def retrieve_req_subject_object(p_req_str, **kwargs):
    """@ingroup jarvis
    @anchor retrieve_req_subject_object
    Retrieve list of objects named as proper nouns found for requirement subject

    @param[in] p_req_str : requirement description
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    req_subject_object = None

    req_subject, _, _, _ = detect_req_pattern(p_req_str)

    # Retrieve the subject in object list
    req_subject_object_list, _ = retrieve_req_proper_noun_object(req_subject, p_is_subject=True, **kwargs)

    for obj in req_subject_object_list:
        if obj:
            req_subject_object = obj

    return req_subject_object


def retrieve_req_object_object_list(p_req_str, **kwargs):
    """@ingroup jarvis
    @anchor retrieve_req_object_object_list
    Retrieve list of objects named as proper nouns found for requirement object

    @param[in] p_req_str : requirement description
    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    _, req_object, _, _ = detect_req_pattern(p_req_str)

    req_object_object_list, _ = retrieve_req_proper_noun_object(req_object, **kwargs)

    for req_object_object in req_object_object_list.copy():
        if req_object_object is None:
            req_object_object_list.remove(req_object_object)

    return req_object_object_list


def analyze_requirement(**kwargs):
    """@ingroup jarvis
    @anchor analyze_requirement
    Analyze requirements against jarvis data structure

    @param[in] kwargs : jarvis data structure
    @return list of objects
    """
    update = 0
    xml_requirement_list = kwargs['xml_requirement_list']
    output_xml = kwargs['output_xml']

    for xml_requirement in xml_requirement_list:
        # Check if the requirement subject is known
        req_subject_object = retrieve_req_subject_object(xml_requirement.description)

        if req_subject_object is None:
            # Ask user to create the object in the jarvis data structure
            answer = handler_question.question_to_user(f"Do you want to create an object for the subject of "
                                                       f"the requirement: {xml_requirement.description} "
                                                       f"(id: {xml_requirement.id}) ? (Y/N)")

            if answer == "y":
                print("TODO")
            elif answer == "q":
                break
            else:
                Logger.set_warning(__name__,
                                   f"Subject of requirement: {xml_requirement.description} (id: {xml_requirement.id}) "
                                   f"is not defined in the system analysis")

    return update
