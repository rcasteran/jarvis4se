""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries
import difflib
import re

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
from . import orchestrator_object, orchestrator_object_allocation
from tools import Logger
from jarvis.handler import handler_question
from jarvis import util

# Constants
GOAL_CONFIDENCE_RATIO = 0.95


def check_add_goal(p_str_list, **kwargs):
    """@ingroup orchestrator
    @anchor check_add_goal
    Check list of goal declarations before adding them to jarvis data structure

    @param[in] p_str_list : list of goal declarations
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    goal_list = []

    for p_str in p_str_list:
        pattern_actor = p_str[0].replace('"', "")
        desc_subject = p_str[1].replace('"', "")
        desc_activity = "to " + p_str[2].replace('"', "")

        if not pattern_actor.startswith(f'The {datamodel.ObjectTextPropertyLabel} of '):
            pattern_actor = re.compile(r'As a (.*?),', re.IGNORECASE).split(pattern_actor)
            desc_actor = pattern_actor[1]

            # Retrieve the subject in object list
            goal_subject_object, _ = retrieve_goal_proper_noun_subject_object(desc_subject, **kwargs)

            if goal_subject_object:
                if isinstance(goal_subject_object, datamodel.TypeWithAllocatedReqList):
                    Logger.set_info(__name__, f"Goal identified about {goal_subject_object.name}: "
                                              f"As a {desc_actor}, I want {desc_subject} "
                                              f"{desc_activity}")
                else:
                    Logger.set_info(__name__,
                                    f"Goal identified: As a {desc_actor}, I want {desc_subject} "
                                    f"{desc_activity}")
                    Logger.set_warning(__name__,
                                       f'Subject "{desc_subject}" of the goal is unknown')
            else:
                Logger.set_info(__name__, f"Goal identified: As a {desc_actor}, I want {desc_subject} "
                                          f"{desc_activity}")
                Logger.set_warning(__name__,
                                   f'Subject "{desc_subject}" of the goal is unknown')

            # Check if a goal with the same text already exist
            sequence_ratio_list = evaluate_goal_text_similarities(desc_actor,
                                                                  desc_subject,
                                                                  desc_activity,
                                                                  **kwargs)

            goal_allocated_object_list = check_goal_relationship(goal_subject_object,
                                                                 desc_actor,
                                                                 desc_activity,
                                                                 **kwargs)

            if sequence_ratio_list:
                similar_goal_name = max(sequence_ratio_list, key=sequence_ratio_list.get)
                Logger.set_info(__name__,
                                f"Goal {similar_goal_name} has the same "
                                f"text (confidence factor: {sequence_ratio_list[similar_goal_name]})")
            else:
                answer, _ = handler_question.question_to_user(f"Please give a goal name: ")
                if len(answer) > 0 and answer != "q":
                    existing_object = orchestrator_object.retrieve_object_by_name(answer, **kwargs)
                    if existing_object:
                        if isinstance(existing_object.type, datamodel.BaseType):
                            if str(existing_object.type) != "Goal":
                                Logger.set_error(__name__,
                                                 f"{existing_object.type} with the name "
                                                 f"{answer} already exists")
                            else:
                                goal_list.append([answer, f"As a {desc_actor}, I want {desc_subject} "
                                                          f"{desc_activity}",
                                                  goal_subject_object,
                                                  goal_allocated_object_list])
                        else:
                            if str(existing_object.type.name) != "Goal":
                                Logger.set_error(__name__,
                                                 f"{existing_object.type.name} with the name "
                                                 f"{answer} already exists")
                            else:
                                goal_list.append([answer, f"As a {desc_actor}, I want {desc_subject} "
                                                          f"{desc_activity}",
                                                  goal_subject_object,
                                                  goal_allocated_object_list])
                    else:
                        goal_list.append([answer, f"As a {desc_actor}, I want {desc_subject} "
                                                  f"{desc_activity}",
                                          goal_subject_object,
                                          goal_allocated_object_list])
                else:
                    Logger.set_error(__name__, "No name entered for identified goal")
        # Else do nothing

    if goal_list:
        update = add_goal(goal_list, **kwargs)
    else:
        update = 0

    return update


def evaluate_goal_text_similarities(p_desc_actor, p_desc_subject, p_desc_activity, **kwargs):
    """@ingroup orchestrator
    @anchor evaluate_goal_text_similarities
    Evaluate similarities between two goal declarations

    @param[in] p_desc_actor : part of goal declaration about the actor
    @param[in] p_desc_subject : part of goal declaration about the subject
    @param[in] p_desc_activity : part of goal declaration about the activity
    @param[in] kwargs : Jarvis dictionaries
    @return list of similarities ratio per requirements
    """
    xml_goal_list = kwargs[XML_DICT_KEY_9_GOAL_LIST]
    sequence_ratio_list = {}

    for xml_goal in xml_goal_list:
        if xml_goal.text:
            xml_desc_actor, xml_desc_subject, xml_desc_activity = detect_goal_pattern(xml_goal.text)

            sequence_desc_before_modal = difflib.SequenceMatcher(None,
                                                                 xml_desc_actor,
                                                                 p_desc_actor)
            sequence_desc_after_modal_subject = difflib.SequenceMatcher(None,
                                                                        xml_desc_subject,
                                                                        p_desc_subject)
            sequence_desc_after_modal_activity = difflib.SequenceMatcher(None,
                                                                         xml_desc_activity,
                                                                         p_desc_activity)
            if sequence_desc_after_modal_subject.ratio() == 1 \
                    and sequence_desc_before_modal.ratio() > GOAL_CONFIDENCE_RATIO \
                    and sequence_desc_after_modal_activity.ratio() > GOAL_CONFIDENCE_RATIO:
                sequence_ratio_list[xml_goal.name] = max(sequence_desc_before_modal.ratio(),
                                                         sequence_desc_after_modal_activity.ratio())
            # Else do nothing
        # Else do nothing

    return sequence_ratio_list


def check_goal_relationship(p_goal_subject_object, p_desc_actor, p_desc_activity, **kwargs):
    """@ingroup orchestrator
    @anchor check_goal_relationship
    Check goal relationship between the object related to the goal subject and the potential objects
    related to the other goal parts

    @param[in] p_goal_subject_object_list : list of object related to the goal subject
    @param[in] p_desc_actor : part of the goal about the actor
    @param[in] p_desc_activity : part of the goal about the activity
    @return list of objects in relation with the object related to the goal subject
    """
    goal_object_list = []

    # Check goal actor content
    goal_actor_object, _ = retrieve_goal_proper_noun_actor_object(p_desc_actor, **kwargs)
    if p_goal_subject_object:
        if orchestrator_object.check_object_relationship(p_goal_subject_object,
                                                         goal_actor_object,
                                                         p_desc_actor,
                                                         **kwargs):
            # Relationship found in the datamodel between goal subject and goal
            # actor. Add it to the allocated object list.
            goal_object_list.append(goal_actor_object)
        # Else do nothing : cannot create automatically this relationship because it requires
        # physical interface
    # Else do nothing

    goal_activity_object, _ = retrieve_goal_proper_noun_activity_object(p_desc_activity, **kwargs)
    if p_goal_subject_object and goal_activity_object is not None:
        if not orchestrator_object.check_object_relationship(p_goal_subject_object,
                                                             goal_activity_object,
                                                             p_desc_activity,
                                                             **kwargs):
            # Relationship not found in the datamodel between goal subject and goal
            # activity. Create this relationship automatically because it is an allocation.
            orchestrator_object_allocation.check_add_allocation([[p_goal_subject_object.name,
                                                                 goal_activity_object.name]],
                                                                **kwargs)
        # Else do nothing

        goal_object_list.append(goal_activity_object)

    return goal_object_list


def detect_goal_pattern(p_str):
    """@ingroup orchestrator
    @anchor detect_goal_pattern
    Detect goal pattern in goal declaration

    @param[in] p_str: full goal declaration
    @return goal actor, goal subject, goal activity
    """
    pattern = re.compile(datamodel.GOAL_PATTERN, re.IGNORECASE).split(p_str)
    pattern_actor = re.compile(r'As a (.*?),', re.IGNORECASE).split(pattern[1])

    Logger.set_debug(__name__, f'Goal actor: {pattern_actor[1]}')
    Logger.set_debug(__name__, f'Goal subject: {pattern[2]}')
    Logger.set_debug(__name__, f'Goal activity: {"to " + pattern[3]}')

    return pattern_actor[1].strip(), pattern[2].strip(), "to " + pattern[3].strip()


def retrieve_goal_actor_object(p_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_goal_actor_object
    Retrieve object named as proper noun found in goal text

    @param[in] p_str : goal text
    @param[in] kwargs : jarvis data structure
    @return object
    """
    actor_str, _, _ = detect_goal_pattern(p_str)

    req_object, _ = retrieve_goal_proper_noun_actor_object(actor_str, **kwargs)

    return req_object


def retrieve_goal_proper_noun_actor_object(p_desc_actor, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_goal_proper_noun_actor_object
    Retrieve object named as proper nouns found in goal text

    @param[in] p_desc_actor : goal text
    @param[in] kwargs : jarvis data structure
    @return object
    """
    # Try to retrieve the object with the whole goal string
    req_object = orchestrator_object.retrieve_object_by_name(p_desc_actor, **kwargs)

    if req_object:
        is_error = False
    else:
        is_error = True

    return req_object, is_error


def retrieve_goal_subject_object(p_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_goal_actor_object
    Retrieve object named as proper noun found in goal text

    @param[in] p_str : goal text
    @param[in] kwargs : jarvis data structure
    @return object
    """
    _, subject_str, _ = detect_goal_pattern(p_str)

    req_object, _ = retrieve_goal_proper_noun_subject_object(subject_str, **kwargs)

    return req_object


def retrieve_goal_proper_noun_subject_object(p_desc_actor, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_goal_proper_noun_subject_object
    Retrieve object named as proper nouns found in goal text

    @param[in] p_desc_actor : goal text
    @param[in] kwargs : jarvis data structure
    @return object
    """
    # Try to retrieve the object with the whole goal string
    req_object = orchestrator_object.retrieve_object_by_name(p_desc_actor, **kwargs)

    if req_object:
        is_error = False
    else:
        is_error = True

    return req_object, is_error


def retrieve_goal_activity_object(p_str, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_goal_activity_object
    Retrieve object named as proper nouns found in goal text

    @param[in] p_str : goal text
    @param[in] kwargs : jarvis data structure
    @return object
    """
    _, _, activity_str = detect_goal_pattern(p_str)

    req_object, _ = retrieve_goal_proper_noun_activity_object(activity_str, **kwargs)

    return req_object


def retrieve_goal_proper_noun_activity_object(p_desc_activity, **kwargs):
    """@ingroup orchestrator
    @anchor retrieve_goal_proper_noun_activity_object_list
    Retrieve object named as proper nouns found in goal text

    @param[in] p_desc_activity : goal text
    @param[in] kwargs : jarvis data structure
    @return object
    """
    # Try to retrieve the object with the whole goal string
    req_object = orchestrator_object.retrieve_object_by_name(p_desc_activity, **kwargs)

    if req_object:
        is_error = False
    else:
        is_error = True

    return req_object, is_error


def add_goal(p_goal_list, **kwargs):
    """@ingroup orchestrator
    @anchor add_goal
    Add goal list to jarvis data structure

    @param[in] p_goal_list : list of goals
    @param[in] kwargs : jarvis data structure
    @return jarvis data structure updated (1) or not (0)
    """
    xml_goal_list = kwargs[XML_DICT_KEY_9_GOAL_LIST]
    output_xml = kwargs['output_xml']

    new_goal_list = []
    new_allocation_list = []

    update = 0
    # Create goal names list already in xml
    xml_goal_name_list = orchestrator_object.check_object_name_in_list(xml_goal_list)
    # Filter attribute_list, keeping only the ones not already in the xml
    for goal_item in p_goal_list:
        if goal_item[0] not in xml_goal_name_list:
            new_goal = datamodel.Goal()
            new_goal.set_name(str(goal_item[0]))
            new_goal.set_text(str(goal_item[1]))
            # Generate and set unique identifier of length 10 integers
            new_goal.set_id(util.get_unique_id())
            # alias is 'none' by default
            new_goal_list.append(new_goal)

            # Test if any allocated object is identified in the goal subject
            if goal_item[2]:
                goal_item[2].add_allocated_goal(new_goal.id)
                new_allocation_list.append([goal_item[2], new_goal])
            # Else do nothing

            # Test if any allocated object is identified in the goal actor or activity
            if goal_item[3]:
                for item in goal_item[3]:
                    if item:
                        item.add_allocated_goal(new_goal.id)
                        new_allocation_list.append([item, new_goal])
        else:
            Logger.set_info(__name__, goal_item[0] + " already exists")

    if new_goal_list:
        output_xml.write_goal(new_goal_list)
        if new_allocation_list:
            output_xml.write_object_allocation(new_allocation_list)
        # Else do nothing

        for goal in new_goal_list:
            xml_goal_list.add(goal)
            Logger.set_info(__name__,
                            goal.name + " is a goal")

        for elem in new_allocation_list:
            Logger.set_info(__name__,
                            f"{elem[1].__class__.__name__} {elem[1].name} is satisfied by "
                            f"{elem[0].__class__.__name__} {elem[0].name}")

        update = 1
    # Else do nothing

    return update


def check_add_goal_text(p_text_str_list, **kwargs):
    xml_goal_list = kwargs[XML_DICT_KEY_9_GOAL_LIST]
    text_list = []

    # Create a list with all goal names/aliases already in the xml
    xml_goal_name_list = orchestrator_object.check_object_name_in_list(xml_goal_list)
    for elem in p_text_str_list:
        goal_str = elem[0].replace('"', "")
        text_str = elem[1].replace('"', "")

        if any(goal_str in s for s in xml_goal_name_list):
            for goal in xml_goal_list:
                if goal_str == goal.name or goal_str == goal.alias:
                    goal_actor, goal_subject, goal_activity = detect_goal_pattern(text_str.lstrip(' '))

                    # Retrieve the subject in object list
                    goal_subject_object, is_error = retrieve_goal_proper_noun_subject_object(goal_subject,
                                                                                             **kwargs)

                    if not is_error:
                        if isinstance(goal_subject_object, datamodel.TypeWithAllocatedReqList):
                            Logger.set_info(__name__, f"Goal {goal.name} is about "
                                                      f"{goal_subject_object.name}")
                        else:
                            Logger.set_warning(__name__,
                                               f'Subject "{goal_subject}" of the goal {goal.name} '
                                               f'is unknown')
                    # Else do nothing

                    # Check if a goal with the same text already exist
                    sequence_ratio_list = evaluate_goal_text_similarities(goal_actor,
                                                                          goal_subject,
                                                                          goal_activity,
                                                                          **kwargs)

                    goal_allocated_object_list = check_goal_relationship(goal_subject_object,
                                                                         goal_actor,
                                                                         goal_activity,
                                                                         **kwargs)

                    if sequence_ratio_list:
                        similar_goal_name = max(sequence_ratio_list, key=sequence_ratio_list.get)
                        Logger.set_info(__name__,
                                        f"Goal {similar_goal_name} has the same "
                                        f"text (confidence factor: "
                                        f"{sequence_ratio_list[similar_goal_name]})")
                    else:
                        text_list.append([goal, text_str.lstrip(' '),
                                          goal_subject_object,
                                          goal_allocated_object_list])
                # Else do nothing
        else:
            Logger.set_error(__name__,
                             f"The goal {goal_str} does not exist")

    if text_list:
        update = add_goal_text(text_list, **kwargs)
    else:
        update = 0

    return update


def add_goal_text(p_text_list, **kwargs):
    output_xml = kwargs['output_xml']
    update = 0

    for text_item in p_text_list:
        new_allocation_list = []
        # Test if allocated object is identified in the goal subject
        if text_item[2]:
            text_item[2].add_allocated_goal(text_item[0].id)
            new_allocation_list.append([text_item[2], text_item[0]])
        # Else do nothing

        # Test if allocated object is identified in the goal actor or activity
        if text_item[3]:
            for item in text_item[3]:
                if item:
                    item.add_allocated_goal(text_item[0].id)
                    new_allocation_list.append([item, text_item[0]])
                # Else do nothing
        # Else do nothing

        output_xml.write_goal_text([[text_item[0], text_item[1]]])
        Logger.set_info(__name__,
                        f"{text_item[0].name} text is {text_item[1]}")

        if new_allocation_list:
            output_xml.write_object_allocation(new_allocation_list)

            for elem in new_allocation_list:
                Logger.set_info(__name__,
                                f"{elem[1].__class__.__name__} {elem[1].name} is satisfied by "
                                f"{elem[0].__class__.__name__} {elem[0].name}")
        # Else do nothing

        update = 1

    return update
