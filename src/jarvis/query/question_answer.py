# Libraries


# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from tools import Logger





def get_consumes_produces_info(wanted_object, relationship_list):
    """Get consumes/produces info"""
    object_relationship = set()
    for elem in relationship_list:
        if elem[1].id == wanted_object.id:
            object_relationship.add(elem[0])
        if elem[0] == wanted_object.name:
            object_relationship.add(elem[1].name)
    if object_relationship:
        return object_relationship


def get_child_name_list(parent_object, object_list):
    """Get child's name list"""
    child_list = set()
    for child in object_list:
        if child in parent_object.child_list:
            child_list.add((child.name, "Child"))
    return list(child_list)


def get_allocation_object(wanted_object, object_list):
    """Get current allocation for an object"""
    allocation_set = set()
    object_type = get_object_type(wanted_object)

    if object_type == 'function':
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.allocated_function_list):
                allocation_set.add(fun_elem)
    elif object_type == 'state':
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.allocated_state_list):
                allocation_set.add(fun_elem)
    elif object_type == 'data':
        for fun_inter in object_list:
            if any(s == wanted_object.id for s in fun_inter.allocated_data_list):
                allocation_set.add(fun_inter)
    elif object_type == 'Functional interface':
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.exposed_interface_list):
                allocation_set.add(fun_elem)
    elif object_type == 'Functional element':
        for function in object_list:
            if any(s == function.id for s in wanted_object.allocated_function_list):
                allocation_set.add(function)
    if allocation_set:
        return allocation_set

    return


def get_fun_elem_function_state_allocation(wanted_object, xml_function_list, xml_state_list):
    """Returns a list for allocations with:
    [(function.name, "Function allocation"), (state.name, "State allocation"), ...]
    """
    allocation_list = []
    for allocated_fun in wanted_object.allocated_function_list:
        for fun in xml_function_list:
            if fun.id == allocated_fun:
                allocation_list.append((fun.name, "Function allocation"))
    for allocated_state in wanted_object.allocated_state_list:
        for state in xml_state_list:
            if state.id == allocated_state:
                allocation_list.append((state.name, "State allocation"))

    return allocation_list


def get_latest_obj_interface(fun_intf, data, last_fun_elem_exposing_list, fun_elem_exposing_list, **kwargs):
    """For a data, find last producer and consumer if they are allocated to last fun_elem
    exposing the functional interface asked"""
    data_dict = {'Data': data.name,
                 'Last consumer Function(s)': [],
                 'Last consumer Functional element(s)': [],
                 'Last producer Function(s)': [],
                 'Last producer Functional element(s)': []}

    for prod in kwargs[XML_DICT_KEY_13_FUN_PROD_LIST]:
        if prod[0] == data and \
                check_latest(prod[1], kwargs[XML_DICT_KEY_1_FUNCTION_LIST]) == prod[1].name:
            for cons in kwargs[XML_DICT_KEY_12_FUN_CONS_LIST]:
                cons_last_fun_elem = None
                prod_last_fun_elem = None
                if cons[0] == prod[0] and \
                        check_latest(cons[1], kwargs[XML_DICT_KEY_1_FUNCTION_LIST]) == cons[1].name:
                    cons_fun_elem_list = get_allocation_object(cons[1], kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
                    if cons_fun_elem_list:
                        for fun_elem in cons_fun_elem_list:
                            if fun_elem.name in last_fun_elem_exposing_list:
                                cons_last_fun_elem = fun_elem
                            elif fun_elem.name in fun_elem_exposing_list:
                                cons_last_fun_elem = fun_elem
                                if not check_child_fun_elem_exposing_recursively(0,
                                                                                 fun_elem,
                                                                                 last_fun_elem_exposing_list):
                                    Logger.set_warning(__name__,
                                                       f'Functional element {fun_elem.name} has a child exposing the '
                                                       f'Functional interface {fun_intf.name}. Please consider to '
                                                       f'allocate the Function {cons[1].name} to it.')
                                # Else do nothing
                            # Else do nothing
                    # Else do nothing

                    prod_fun_elem_list = get_allocation_object(prod[1], kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
                    if prod_fun_elem_list:
                        for fun_elem in prod_fun_elem_list:
                            if fun_elem.name in last_fun_elem_exposing_list:
                                prod_last_fun_elem = fun_elem
                            elif fun_elem.name in fun_elem_exposing_list:
                                prod_last_fun_elem = fun_elem
                                if not check_child_fun_elem_exposing_recursively(0,
                                                                                 fun_elem,
                                                                                 last_fun_elem_exposing_list):
                                    Logger.set_warning(__name__,
                                                       f'Functional element {fun_elem.name} has a child exposing the '
                                                       f'Functional interface {fun_intf.name}. Please consider to '
                                                       f'allocate the Function {prod[1].name} to it.')
                                # Else do nothing
                            # Else do nothing
                    # Else do nothing

                if not cons_last_fun_elem == prod_last_fun_elem:
                    if not any(c == prod[1].name for c in data_dict['Last producer Function(s)']):
                        if prod_last_fun_elem and \
                                prod[1].id in prod_last_fun_elem.allocated_function_list:
                            data_dict['Last producer Function(s)'].append(prod[1].name)
                            data_dict['Last producer Functional element(s)'].append(
                                prod_last_fun_elem.name)
                    if not any(c == cons[1].name for c in data_dict['Last consumer Function(s)']):
                        if cons_last_fun_elem and \
                                cons[1].id in cons_last_fun_elem.allocated_function_list:
                            data_dict['Last consumer Function(s)'].append(cons[1].name)
                            data_dict['Last consumer Functional element(s)'].append(
                                cons_last_fun_elem.name)

    return data_dict


def check_latest(wanted_object, check_list):
    """Checks and returns latest object = last one decomposed"""
    if not wanted_object.child_list:
        return wanted_object.name
    else:
        check_child = [c for c in wanted_object.child_list]
        if not any(j in check_child for j in check_list):
            return wanted_object.name


def check_child_fun_elem_exposing_recursively(p_nb_last_fun_elem_exposing, p_fun_elem, p_last_fun_elem_exposing_list):
    if p_fun_elem.child_list:
        for child in p_fun_elem.child_list:
            if child.name in p_last_fun_elem_exposing_list:
                p_nb_last_fun_elem_exposing = p_nb_last_fun_elem_exposing + 1
            # Else do nothing
            check_child_fun_elem_exposing_recursively(p_nb_last_fun_elem_exposing, child, p_last_fun_elem_exposing_list)
    # Else do nothing

    return p_nb_last_fun_elem_exposing


def get_input_or_output_fun_and_fun_elem(wanted_object, direction='input', unmerged=False,
                                         **kwargs):
    """
    Gets inputs/outputs for object (Function or Functional Element):
    i.e. what is consumed/produces by wanted object or object allocated functions.
    Args:
        wanted_object: current object
        direction (str: default=input): i.e. input or output asked
        unmerged (bool: default=false): used by functional elements
        **kwargs: all xml lists/sets

    Returns:
        input or output list
    """
    in_or_out_list = []

    object_type = get_object_type(wanted_object)
    if object_type == "Functional element":
        allocated_function_list = set()
        for allocated_function in wanted_object.allocated_function_list:
            for xml_function in kwargs[XML_DICT_KEY_1_FUNCTION_LIST]:
                if allocated_function == xml_function.id:
                    allocated_function_list.add(xml_function)

        for function in allocated_function_list:
            function_in_or_out_list = get_input_or_output_fun_and_fun_elem(function, direction, True, **kwargs)
            for function_in_or_out in function_in_or_out_list:
                if function_in_or_out and function_in_or_out[1] not in [f.name for f in allocated_function_list]:
                    in_or_out_list.append(function_in_or_out)
    elif object_type == "function":
        if direction == 'output':
            in_or_out_list = get_in_out_function(wanted_object,
                                                 kwargs[XML_DICT_KEY_13_FUN_PROD_LIST],
                                                 kwargs[XML_DICT_KEY_12_FUN_CONS_LIST])
        else:
            in_or_out_list = get_in_out_function(wanted_object,
                                                 kwargs[XML_DICT_KEY_12_FUN_CONS_LIST],
                                                 kwargs[XML_DICT_KEY_13_FUN_PROD_LIST])

    if in_or_out_list and not unmerged:
        in_or_out_list = merge_list_per_cons_prod(in_or_out_list)
    # Else do nothing

    return in_or_out_list


def merge_list_per_cons_prod(input_list):
    """
    Sorts data_name in alphabetical order according to their name and merges list by producer or consumer
    Args:
        input_list ([data_name, function_name]): List of consumer/producer with data_name per Function

    Returns:
        Sorted + merged list
    """
    input_list = sorted(input_list)
    output_list = []
    empty_dict = {}
    for data_name, obj_name in input_list:
        if data_name not in empty_dict:
            output_list.append([data_name, obj_name])
            empty_dict[data_name] = len(empty_dict)
        else:
            if obj_name:
                if obj_name not in output_list[empty_dict[data_name]][1]:
                    output_list[empty_dict[data_name]][1] += '\\n' + obj_name

    return output_list


def get_in_out_function(wanted_object, wanted_relationship, opposite_wanted_relationship):
    """
    Return the list of Input/Output for Function's objects.
    Args:
        wanted_object (Function): Object's wanted
        wanted_relationship ([Xml_list]): For Output (producer's list) and Input (consumer's list)
        opposite_wanted_relationship ([Xml_list]): slef-explained
    Returns:
        output_list ([Data, prod/cons])
    """
    output_list = []
    flow_list = get_consumes_produces_info(wanted_object, wanted_relationship)
    if not flow_list:
        return output_list
    for data in flow_list:
        if not any(data in s for s in opposite_wanted_relationship):
            output_list.append([data.name, None])
        else:
            for elem in opposite_wanted_relationship:
                check = True
                if elem[0] == data:
                    for child in elem[1].child_list:
                        if [elem[0], child] in opposite_wanted_relationship:
                            check = False
                    if check:
                        output_list.append([elem[0].name, elem[1].name])

    return output_list


def get_objects_from_id_list(id_list, object_list):
    """From a list of id (from same type) returns list of corresponding objects"""
    output_list = set()
    if not id_list:
        return output_list

    for wanted_object in object_list:
        if wanted_object.id in id_list:
            output_list.add(wanted_object)

    return output_list





def check_parentality(object_a, object_b):
    """Check recursively if object 'a' is not parent of object 'b'"""
    if object_b.parent:
        if object_a == object_b.parent:
            return True
        else:
            return check_parentality(object_a, object_b.parent)
    else:
        return False


def get_children(element, function_list=None, parent_dict=None, count=None, level=None):
    """Get children recursively, adds them to function_list and create parend_dict"""
    if function_list is None:
        function_list = set()
    if parent_dict is None:
        parent_dict = {}
    if not count:
        count = 0

    function_list.add(element)
    if element.child_list:
        count += 1
        if level:
            if (count - 1) == level:
                element.child_list.clear()
                return function_list, parent_dict
        for child in element.child_list:
            parent_dict[child.id] = element.id
            get_children(child, function_list, parent_dict, count, level)

    return function_list, parent_dict


def check_not_family(object_a, object_b):
    """Returns True if object_a and object_b are not in the same family"""
    if not check_parentality(object_a, object_b) and not check_parentality(object_b, object_a):
        return True
    else:
        return False


def get_object_type(object_to_check):
    """From an object, returns its type as string"""
    obj_type_list = [(datamodel.State, 'state'), (datamodel.Function, 'function'),
                     (datamodel.Data, 'data'), (datamodel.FunctionalElement, 'Functional element'),
                     (datamodel.View, 'View'), (datamodel.Transition, 'Transition'),
                     (datamodel.Attribute, 'Attribute'),
                     (datamodel.FunctionalInterface, 'Functional interface'),
                     (datamodel.PhysicalElement, 'Physical element'),
                     (datamodel.PhysicalInterface, 'Physical interface')]
    object_type = ''
    for elem in obj_type_list:
        if isinstance(object_to_check, elem[0]):
            object_type = elem[1]
            return object_type
    return object_type


def get_transition_between_states(p_object_src, p_object_dest, **kwargs):
    transition_object = None

    for transition in kwargs[XML_DICT_KEY_7_TRANSITION_LIST]:
        if p_object_src.id == transition.source and p_object_dest.id == transition.destination:
            transition_object = transition
            break
        # Else do nothing

    return transition_object


def get_fun_intf_data(wanted_object, _, **kwargs):
    """Case for 'list data Functional Interface' """
    data_dict = {}
    data_list = []
    fun_elem_exposing = get_allocation_object(wanted_object, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
    if wanted_object.derived:
        derived_fun_elem_exposing = get_allocation_object(wanted_object.derived,
                                                          kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
        if derived_fun_elem_exposing and fun_elem_exposing:
            fun_elem_exposing = fun_elem_exposing.union(derived_fun_elem_exposing)

    if not fun_elem_exposing:
        Logger.set_warning(__name__, f"Not any functional element exposing {wanted_object.name}")
    else:
        last_fun_elem_name_exposing_list = [check_latest(j, fun_elem_exposing)
                                            for j in fun_elem_exposing
                                            if check_latest(j, fun_elem_exposing)]

        fun_elem_name_exposing_list = [i.name for i in fun_elem_exposing]

        for allocated_id in wanted_object.allocated_data_list:
            for data in kwargs[XML_DICT_KEY_0_DATA_LIST]:
                if allocated_id == data.id:
                    data_list.append(get_latest_obj_interface(wanted_object,
                                                              data,
                                                              last_fun_elem_name_exposing_list,
                                                              fun_elem_name_exposing_list,
                                                              **kwargs))

        if wanted_object.derived:
            for allocated_id in wanted_object.derived.allocated_data_list:
                for data in kwargs[XML_DICT_KEY_0_DATA_LIST]:
                    if allocated_id == data.id:
                        data_list.append(
                            get_latest_obj_interface(wanted_object,
                                                     data,
                                                     last_fun_elem_name_exposing_list,
                                                     fun_elem_name_exposing_list,
                                                     **kwargs))

        if data_list:
            data_dict = {'title': f"Data list for {wanted_object.name}:",
                         'data': data_list}

    return data_dict
