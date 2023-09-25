# Libraries

# Modules
from jarvis.query import question_answer
from tools import Logger


def question_object_info(question_str, **kwargs):
    """Get the 'what' declaration """
    object_str = question_str[0].strip()
    wanted_object = question_answer.check_get_object(object_str, **kwargs)

    if wanted_object:
        object_info = get_object_info(wanted_object, **kwargs)
        if object_info:
            return object_info
    else:
        Logger.set_info(__name__, f"I do not know the following object: {object_str}")


def get_object_info(wanted_object, **kwargs):
    """From wanted_object and all lists, returns a dict with info"""
    object_info = {'Name': str(wanted_object.name),
                   'Object Class': str(type(wanted_object).__name__),
                   'Type': str(wanted_object.type), 'Id': str(wanted_object.id)}

    try:
        # Only Data() does not have these attributes and Transition() does not have parent
        if any(wanted_object.alias):
            object_info['Alias'] = str(wanted_object.alias)
        if wanted_object.parent is not None:
            object_info['Parent'] = str(wanted_object.parent.name)
    except AttributeError:
        # To avoid error when there is no such attribute for the object
        pass
    if object_info['Object Class'] == 'Function':
        get_function_info(wanted_object, object_info, **kwargs)
    elif object_info['Object Class'] == 'FunctionalElement':
        get_fun_elem_info(wanted_object, object_info, **kwargs)
    elif object_info['Object Class'] == 'State':
        if any(wanted_object.child_list):
            object_info['Child List'] = question_answer.get_child_name_list(wanted_object, kwargs['xml_state_list'])
    elif object_info['Object Class'] == 'Transition':
        get_transition_info(wanted_object, kwargs['xml_state_list'], object_info)
    elif object_info['Object Class'] == 'Data':
        get_data_info(wanted_object, object_info, **kwargs)

    if object_info:
        return object_info

    return


def get_function_info(wanted_object, object_info, **kwargs):
    """Get Function info"""
    if any(wanted_object.child_list):
        object_info['Child List'] = question_answer.get_child_name_list(wanted_object, kwargs['xml_function_list'])
    if wanted_object.input_role is not None:
        object_info['Input Role'] = str(wanted_object.input_role)
    if wanted_object.operand is not None:
        object_info['Operand'] = str(wanted_object.operand)

    object_info['Consumption List'] = \
        question_answer.get_consumes_produces_info(wanted_object, kwargs['xml_consumer_function_list'])
    object_info['Production List'] = \
        question_answer.get_consumes_produces_info(wanted_object, kwargs['xml_producer_function_list'])
    return object_info


def get_fun_elem_info(wanted_object, object_info, **kwargs):
    """Get functional element info, i.e. child_list, allocated Function/State"""
    if any(wanted_object.child_list):
        object_info['Child List'] = question_answer.get_child_name_list(wanted_object, kwargs['xml_fun_elem_list'])
    if any(wanted_object.allocated_state_list):
        object_info['Allocated State List'] = \
            get_allocated_object_name_list(wanted_object, kwargs['xml_state_list'])
    if any(wanted_object.allocated_function_list):
        object_info['Allocated Function List'] = \
            get_allocated_object_name_list(wanted_object, kwargs['xml_function_list'])
    return object_info


def get_transition_info(wanted_object, state_list, object_info):
    """Get transition's info"""
    for state in state_list:
        if state.id == wanted_object.source:
            object_info['Source'] = str(state.name)
        if state.id == wanted_object.destination:
            object_info['Destination'] = str(state.name)
    if wanted_object.condition_list:
        object_info['Condition List'] = wanted_object.condition_list
    return object_info


def get_data_info(wanted_object, object_info, **kwargs):
    """Get what consumes/produces for a specific Data object"""
    pred_list = set()
    object_info['Consumer List'] = \
        question_answer.get_consumes_produces_info(wanted_object, kwargs['xml_consumer_function_list'])
    object_info['Producer List'] = \
        question_answer.get_consumes_produces_info(wanted_object, kwargs['xml_producer_function_list'])
    if any(wanted_object.predecessor_list):
        for pred in wanted_object.predecessor_list:
            pred_list.add(pred.name)
    object_info['Predecessor List'] = pred_list
    return object_info


def get_allocated_object_name_list(wanted_object, object_list):
    """From Functional Element object and list (State/Function) get the allocated objects"""
    allocation_list = set()
    for allocated_object in object_list:
        if any(s == allocated_object.id for s in wanted_object.allocated_state_list):
            allocation_list.add(allocated_object.name)
        if any(s == allocated_object.id for s in wanted_object.allocated_function_list):
            allocation_list.add(allocated_object.name)
    return allocation_list


def question_object_allocation(object_str, **kwargs):
    """From object_str, get object then check if allocated and returns allocation's list"""
    object_info = ""
    object_str = object_str[0]
    xml_function_name_list = question_answer.get_objects_names(kwargs['xml_function_list'])
    xml_state_name_list = question_answer.get_objects_names(kwargs['xml_state_list'])
    whole_objects_name_list = [*xml_function_name_list, *xml_state_name_list]
    if not any(s == object_str for s in whole_objects_name_list):
        Logger.set_warning(__name__,
                           f"{object_str} is not a function nor a state")
    else:
        result_function = any(s == object_str for s in xml_function_name_list)
        resul_state = any(s == object_str for s in xml_state_name_list)
        result = [result_function, False, resul_state,  False, False]
        wanted_object = question_answer.match_object(object_str, result, **kwargs)
        if wanted_object:
            allocation_list = question_answer.get_allocation_object(wanted_object, kwargs['xml_fun_elem_list'])
            if allocation_list:
                object_info += f'"{wanted_object.name}" is allocated to ' \
                               + ", ".join([elem.name for elem in allocation_list])
                return object_info

    return
