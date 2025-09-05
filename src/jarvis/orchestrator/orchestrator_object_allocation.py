""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
from . import orchestrator_object, orchestrator_viewpoint_requirement
from jarvis.handler import handler_question
from jarvis import util
from tools import Logger

# Constants
OBJ_ALLOCATION_TO_DATA_IDX = 0
OBJ_ALLOCATION_TO_FUNCTION_IDX = 1
OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX = 2
OBJ_ALLOCATION_TO_FUN_ELEM_IDX = 3
OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX = 4
OBJ_ALLOCATION_TO_STATE_IDX = 5
OBJ_ALLOCATION_TO_TRANSITION_IDX = 6
OBJ_ALLOCATION_TO_FUN_INTF_IDX = 7
OBJ_ALLOCATION_TO_PHY_ELEM_IDX = 8
OBJ_ALLOCATION_TO_PHY_INTF_IDX = 9
OBJ_ALLOCATION_TO_VIEW_IDX = 10


def check_add_allocation(allocation_str_list, **kwargs):
    """
    Check if each string in allocation_str_list are corresponding to an actual object's name/alias,
    create lists for:
    [[FunctionalElement, Function/State], [FunctionalInterface, Data],[State, Function],
    [PhysicalElement, FunctionalElement], [PhysicalInterface, FunctionalInterface]]
    Send lists to add_allocation() to write them within xml and then returns update from it.

        Parameters:
            allocation_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    new_allocation_dict = {
        OBJ_ALLOCATION_TO_DATA_IDX: [], # [Data, Requirement]
        OBJ_ALLOCATION_TO_FUNCTION_IDX: [],  # [Function, Activity/Requirement]
        OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX: [],  # [FunctionalElement, Function/State/Requirement]
        OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX: [],  # [State, Function/Requirement]
        OBJ_ALLOCATION_TO_TRANSITION_IDX: [], # [Transition, Requirement]
        OBJ_ALLOCATION_TO_FUN_INTF_IDX: [],  # [FunctionalInterface, Data/Requirement]
        OBJ_ALLOCATION_TO_PHY_ELEM_IDX: [],  # [PhysicalElement, FunctionalElement/Requirement]
        OBJ_ALLOCATION_TO_PHY_INTF_IDX: [],  # [PhysicalInterface, FunctionalInterface/Requirement]
        OBJ_ALLOCATION_TO_VIEW_IDX: []  # [Function/Functional Element/Data, View]
    }

    cleaned_allocation_str_list = util.cut_tuple_list(allocation_str_list)

    for elem in cleaned_allocation_str_list:
        alloc_obj = orchestrator_object.retrieve_object_by_name(
            elem[0],
            **{XML_DICT_KEY_1_FUNCTION_LIST: kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
               XML_DICT_KEY_6_STATE_LIST: kwargs[XML_DICT_KEY_6_STATE_LIST],
               XML_DICT_KEY_0_DATA_LIST: kwargs[XML_DICT_KEY_0_DATA_LIST],
               XML_DICT_KEY_7_TRANSITION_LIST: kwargs[XML_DICT_KEY_7_TRANSITION_LIST],
               XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
               XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
               XML_DICT_KEY_4_PHY_ELEM_LIST: kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST],
               XML_DICT_KEY_5_PHY_INTF_LIST: kwargs[XML_DICT_KEY_5_PHY_INTF_LIST]
               })
        obj_to_alloc = orchestrator_object.retrieve_object_by_name(
            elem[1],
            **{XML_DICT_KEY_1_FUNCTION_LIST: kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
               XML_DICT_KEY_10_ACTIVITY_LIST: kwargs[XML_DICT_KEY_10_ACTIVITY_LIST],
               XML_DICT_KEY_6_STATE_LIST: kwargs[XML_DICT_KEY_6_STATE_LIST],
               XML_DICT_KEY_0_DATA_LIST: kwargs[XML_DICT_KEY_0_DATA_LIST],
               XML_DICT_KEY_11_INFORMATION_LIST: kwargs[XML_DICT_KEY_11_INFORMATION_LIST],
               XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
               XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
               XML_DICT_KEY_8_REQUIREMENT_LIST: kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
               })

        if alloc_obj is None or obj_to_alloc is None:
            if alloc_obj is None and obj_to_alloc is None:
                Logger.set_error(__name__,
                                 f"Objects {elem[0]} and {elem[1]} are unknown")
            elif alloc_obj is None:
                Logger.set_error(__name__,
                                 f"Object {elem[0]} is unknown")
            else:
                Logger.set_error(__name__,
                                 f"Object {elem[1]} is unknown")
        else:
            is_improper_allocation = False
            is_req_already_allocated = False

            # case OBJ_ALLOCATION_TO_DATA_IDX
            if isinstance(alloc_obj, datamodel.Data):
                if isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_DATA_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                elif isinstance(obj_to_alloc, datamodel.Information):
                    pair = check_allocation_information(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_DATA_IDX].append(pair)
                    # Else do nothing
                else:
                    is_improper_allocation = True
            # case OBJ_ALLOCATION_TO_FUNCTION_IDX
            elif isinstance(alloc_obj, datamodel.Function):
                if isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_FUNCTION_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                elif isinstance(obj_to_alloc, datamodel.Activity):
                    pair = check_allocation_to_function(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_FUNCTION_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                else:
                    is_improper_allocation = True
            # case OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX
            elif isinstance(alloc_obj, datamodel.FunctionalElement):
                if isinstance(obj_to_alloc, (datamodel.Function, datamodel.State)):
                    pair = check_allocation_to_fun_elem(alloc_obj, obj_to_alloc, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
                                                        **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX].append(pair)
                elif isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                else:
                    is_improper_allocation = True
            # case OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX
            elif isinstance(alloc_obj, datamodel.State):
                if isinstance(obj_to_alloc, datamodel.Function):
                    pair = check_allocation_to_state(alloc_obj, obj_to_alloc, kwargs[XML_DICT_KEY_6_STATE_LIST],
                                                     **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX].append(pair)
                elif isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                else:
                    is_improper_allocation = True
            # case OBJ_ALLOCATION_TO_TRANSITION_IDX
            elif isinstance(alloc_obj, datamodel.Transition):
                if isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_TRANSITION_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                else:
                    is_improper_allocation = True
            # case OBJ_ALLOCATION_TO_FUN_INTF_IDX
            elif isinstance(alloc_obj, datamodel.FunctionalInterface):
                if isinstance(obj_to_alloc, datamodel.Data):
                    pair = check_allocation_to_fun_inter(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_FUN_INTF_IDX].append(pair)
                elif isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_FUN_INTF_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                else:
                    is_improper_allocation = True
            # case OBJ_ALLOCATION_TO_PHY_ELEM_IDX
            elif isinstance(alloc_obj, datamodel.PhysicalElement):
                if isinstance(obj_to_alloc, (datamodel.Activity, datamodel.FunctionalElement)):
                    pair = check_allocation_to_phy_elem(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_PHY_ELEM_IDX].append(pair)
                elif isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_PHY_ELEM_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                else:
                    is_improper_allocation = True
            # case OBJ_ALLOCATION_TO_PHY_INTF_IDX
            elif isinstance(alloc_obj, datamodel.PhysicalInterface):
                if isinstance(obj_to_alloc, datamodel.FunctionalInterface):
                    # TODO Functional interface allocation to physical interface
                    print("Functional interface allocation case")
                elif isinstance(obj_to_alloc, datamodel.Requirement):
                    pair = check_allocation_requirement(alloc_obj, obj_to_alloc, **kwargs)
                    if pair:
                        new_allocation_dict[OBJ_ALLOCATION_TO_PHY_INTF_IDX].append(pair)
                    else:
                        is_req_already_allocated = True
                else:
                    is_improper_allocation = True
            else:
                is_improper_allocation = True

            if is_req_already_allocated:
                Logger.set_info(__name__,
                                f"{obj_to_alloc.__class__.__name__} {obj_to_alloc.name} already satisfied by "
                                f"{alloc_obj.__class__.__name__} {alloc_obj.name}")
            # Else do nothing

            if is_improper_allocation:
                Logger.set_error(__name__,
                                 f"{obj_to_alloc.__class__.__name__} {obj_to_alloc.name} cannot be allocated to "
                                 f"{alloc_obj.__class__.__name__} {alloc_obj.name}")
            # Else do nothing

    update = add_allocation(new_allocation_dict, **kwargs)

    return update


def check_allocation_to_function(alloc_obj, obj_to_alloc, **kwargs):
    pair = None

    if isinstance(obj_to_alloc, datamodel.Activity):
        if not any(allocated_activity_id == obj_to_alloc.id
                   for allocated_activity_id in alloc_obj.allocated_activity_list):
            alloc_obj.add_allocated_activity(obj_to_alloc.id)
            pair = [alloc_obj, obj_to_alloc]
        # Else do nothing
    # Else do nothing

    return pair


def check_add_allocated_item_to_view(p_item_name_str, p_item_producer_str, p_item_consumer_str, **kwargs):
    """
    Checks if a view is already activated, if yes check if item isn't already
    allocated and returns corresponding [View, Object].
    Args:
        p_item_name_str (string): Object's name/alias from user's input
    Returns:
        [View, Object]
    """
    xml_view_list = kwargs[XML_DICT_KEY_13_VIEW_LIST]

    # [data, function, fun_elem] case
    xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
    xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
    xml_data_list = kwargs[XML_DICT_KEY_0_DATA_LIST]

    # [information, activity, phy_elem] case
    xml_information_list = kwargs[XML_DICT_KEY_11_INFORMATION_LIST]
    xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]
    xml_phy_elem_list = kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST]

    new_allocation_dict = {
        OBJ_ALLOCATION_TO_VIEW_IDX: []  # [Function/Functional Element/Data/Activity/Physical Element/Information, View]
    }

    if any(s.activated for s in xml_view_list):
        activated_view = None

        for view in xml_view_list:
            if view.activated:
                activated_view = view
                break

        if activated_view:
            is_allocated = False

            for xml_data in xml_data_list:
                if p_item_name_str == xml_data.name:
                    if xml_data.id not in activated_view.allocated_item_list:
                        activated_view.add_allocated_item(xml_data.id)
                        new_allocation_dict[OBJ_ALLOCATION_TO_VIEW_IDX].append(
                            [activated_view,
                             xml_data,
                             orchestrator_object.retrieve_object_by_name(p_item_consumer_str,
                                                                         **kwargs),
                             orchestrator_object.retrieve_object_by_name(p_item_producer_str,
                                                                         **kwargs)])
                    # Else do nothing
                    is_allocated = True
                    break
                # Else do nothing

            if not is_allocated:
                for xml_function in xml_function_list:
                    if p_item_name_str == xml_function.name or p_item_name_str == xml_function.alias:
                        if xml_function.id not in activated_view.allocated_item_list:
                            activated_view.add_allocated_item(xml_function.id)
                            new_allocation_dict[OBJ_ALLOCATION_TO_VIEW_IDX].append(
                                [activated_view,
                                 xml_function,
                                 orchestrator_object.retrieve_object_by_name(p_item_consumer_str,
                                                                             **kwargs),
                                 orchestrator_object.retrieve_object_by_name(p_item_producer_str,
                                                                             **kwargs)])
                        # Else do nothing
                        is_allocated = True
                        break
                    # Else do nothing

                if not is_allocated:
                    for xml_fun_elem in xml_fun_elem_list:
                        if p_item_name_str == xml_fun_elem.name or p_item_name_str == xml_fun_elem.alias:
                            if xml_fun_elem.id not in activated_view.allocated_item_list:
                                activated_view.add_allocated_item(xml_fun_elem.id)
                                new_allocation_dict[OBJ_ALLOCATION_TO_VIEW_IDX].append(
                                    [activated_view,
                                     xml_fun_elem,
                                     orchestrator_object.retrieve_object_by_name(p_item_consumer_str,
                                                                                 **kwargs),
                                     orchestrator_object.retrieve_object_by_name(p_item_producer_str,
                                                                                 **kwargs)])
                            # Else do nothing
                            is_allocated = True
                            break
                        # Else do nothing

                    if not is_allocated:
                        for xml_information in xml_information_list:
                            if p_item_name_str == xml_information.name:
                                if xml_information.id not in activated_view.allocated_item_list:
                                    xml_activity_consumer = orchestrator_object.retrieve_object_by_name(
                                        p_item_consumer_str,
                                        **kwargs)
                                    xml_activity_producer = orchestrator_object.retrieve_object_by_name(
                                        p_item_producer_str,
                                        **kwargs)

                                    if len(p_item_consumer_str) > 0 and xml_activity_consumer is None:
                                        Logger.set_warning(__name__,
                                                           f'Activity "{p_item_consumer_str}" is unknown. '
                                                           f'Unable to filter the considered information '
                                                           f'"{xml_information.name}"')
                                    elif len(p_item_producer_str) > 0 and xml_activity_producer is None:
                                        Logger.set_warning(__name__,
                                                           f'Activity "{p_item_producer_str}" is unknown. '
                                                           f'Unable to filter the considered information '
                                                           f'"{xml_information.name}"')
                                    # Else do nothing

                                    activated_view.add_allocated_item(xml_information.id)
                                    new_allocation_dict[OBJ_ALLOCATION_TO_VIEW_IDX].append(
                                        [activated_view,
                                         xml_information,
                                         xml_activity_consumer,
                                         xml_activity_producer])
                                # Else do nothing
                                is_allocated = True
                                break
                            # Else do nothing

                        if not is_allocated:
                            for xml_activity in xml_activity_list:
                                if p_item_name_str == xml_activity.name or p_item_name_str == xml_activity.alias:
                                    if xml_activity.id not in activated_view.allocated_item_list:
                                        activated_view.add_allocated_item(xml_activity.id)
                                        new_allocation_dict[OBJ_ALLOCATION_TO_VIEW_IDX].append(
                                            [activated_view,
                                             xml_activity,
                                             orchestrator_object.retrieve_object_by_name(p_item_consumer_str,
                                                                                         **kwargs),
                                             orchestrator_object.retrieve_object_by_name(p_item_producer_str,
                                                                                         **kwargs)])
                                    # Else do nothing
                                    is_allocated = True
                                    break
                                # Else do nothing

                            if not is_allocated:
                                for xml_phy_elem in xml_phy_elem_list:
                                    if p_item_name_str == xml_phy_elem.name or p_item_name_str == xml_phy_elem.alias:
                                        if xml_phy_elem.id not in activated_view.allocated_item_list:
                                            activated_view.add_allocated_item(xml_phy_elem.id)
                                            new_allocation_dict[OBJ_ALLOCATION_TO_VIEW_IDX].append(
                                                [activated_view,
                                                 xml_phy_elem,
                                                 orchestrator_object.retrieve_object_by_name(p_item_consumer_str,
                                                                                             **kwargs),
                                                 orchestrator_object.retrieve_object_by_name(p_item_producer_str,
                                                                                             **kwargs)])
                                        # Else do nothing
                                        break
                                    # Else do nothing
                            # Else do nothing
                        # Else do nothing
                    # Else do nothing
                # Else do nothing
            # Else do nothing
        # Else do nothing
    # Else do nothing

    update = add_allocation(new_allocation_dict, **kwargs)

    return update


def check_allocation_to_phy_elem(alloc_obj, obj_to_alloc, **kwargs):
    # TODO Functional element allocation to physical element
    pair = None

    if isinstance(obj_to_alloc, datamodel.Activity):
        if not any(allocated_activity_id == obj_to_alloc.id
                   for allocated_activity_id in alloc_obj.allocated_activity_list):
            alloc_obj.add_allocated_activity(obj_to_alloc.id)
            pair = [alloc_obj, obj_to_alloc]
        # Else do nothing
    elif  isinstance(obj_to_alloc, datamodel.FunctionalElement):
        if not any(allocated_fun_elem_id == obj_to_alloc.id
                   for allocated_fun_elem_id in alloc_obj.allocated_fun_elem_list):
            alloc_obj.add_allocated_activity(obj_to_alloc.id)
            pair = [alloc_obj, obj_to_alloc]
        # Else do nothing
    # Else do nothing

    return pair


def check_allocation_requirement(p_obj, p_req, **kwargs):
    pair = None

    if not any(allocated_req_id == p_req.id for allocated_req_id in p_obj.allocated_req_list):
        p_obj.add_allocated_requirement(p_req.id)
        pair = [p_obj, p_req]

        # Check for potential req parent in allocated obj parent
        if p_obj.parent:
            if hasattr(p_obj.parent, 'allocated_req_list'):
                orchestrator_viewpoint_requirement.update_requirement_link(p_obj.parent,
                                                                           p_req,
                                                                           **kwargs)
            # Else do nothing
        # Else do nothing
    # Else do nothing

    return pair


def check_allocation_to_fun_elem(fun_elem, obj_to_alloc, fun_elem_list, **kwargs):
    """Check allocation rules for fun_elem then returns objects if check"""
    count = None
    out = None
    check_allocation = orchestrator_object.retrieve_allocated_object_list(obj_to_alloc, fun_elem_list, **kwargs)
    if check_allocation is not None:
        count = len(check_allocation)
        for item in check_allocation:
            # Checks if they are in the same family
            if not orchestrator_object.check_object_is_not_family(item, fun_elem) and item != fun_elem:
                count -= 1

    if count in (None, 0):
        if isinstance(obj_to_alloc, datamodel.State):
            fun_elem.add_allocated_state(obj_to_alloc.id)
        else:
            fun_elem.add_allocated_function(obj_to_alloc.id)
        out = [fun_elem, obj_to_alloc]

    return out


def check_allocation_to_state(state, function, state_list, **kwargs):
    """Check allocation rules for state then returns objects if check"""
    out = None
    check_allocation = orchestrator_object.retrieve_allocated_object_list(function, state_list, **kwargs)
    if check_allocation is None:
        state.add_allocated_function(function.id)
        out = [state, function]
    else:
        if state not in check_allocation:
            state.add_allocated_function(function.id)
            out = [state, function]

    return out


def check_allocation_to_fun_inter(fun_inter, data, **kwargs):
    """Check allocation rules for fun_inter then returns objects if check"""
    out = None
    check_allocation_fun_inter = orchestrator_object.retrieve_allocated_object_list(
        data,
        kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
        **kwargs)
    if check_allocation_fun_inter is None:
        check_fe = check_fun_elem_data_consumption(
            data, fun_inter,
            kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            kwargs[XML_DICT_KEY_15_FUN_CONS_LIST],
            kwargs[XML_DICT_KEY_16_FUN_PROD_LIST])
        if all(i for i in check_fe):
            out = [fun_inter, data]
            fun_inter.add_allocated_data(data.id)
        elif True in check_fe:
            if check_fe[0] is True:
                Logger.set_error(__name__,
                                 f"Data {data.name} has only consumer(s) "
                                 f"allocated to a functional element exposing "
                                 f"{fun_inter.name}, {data.name} not "
                                 f"allocated to {fun_inter.name}")
            elif check_fe[1] is True:
                Logger.set_error(__name__,
                                 f"Data {data.name} has only producer(s) "
                                 f"allocated to a functional element exposing "
                                 f"{fun_inter.name}, {data.name} not "
                                 f"allocated to {fun_inter.name}")
        else:
            Logger.set_error(__name__,
                             f"Data {data.name} has no producer(s) nor "
                             f"consumer(s) allocated to functional elements "
                             f"exposing {fun_inter.name}, {data.name} not "
                             f"allocated to {fun_inter.name}")

    return out


def check_fun_elem_data_consumption(data, fun_inter, fun_elem_list, function_list,
                                    xml_consumer_function_list, xml_producer_function_list):
    """Check if for a fun_inter, the fun_elem exposing it has allocated functions producing and
    consuming that data"""
    fun_elem_exposes = set()
    for fun_elem in fun_elem_list:
        if any(a == fun_inter.id for a in fun_elem.exposed_interface_list):
            fun_elem_exposes.add(fun_elem)

    is_consumer = False
    is_producer = False
    for function in function_list:
        for fun_elem in fun_elem_exposes:
            if any(a == function.id for a in fun_elem.allocated_function_list):
                fun_data = [data, function]
                if any(a == fun_data for a in xml_consumer_function_list):
                    is_consumer = True
                if any(a == fun_data for a in xml_producer_function_list):
                    is_producer = True
                if is_consumer or is_producer:
                    for child in fun_elem.child_list:
                        if child in fun_elem_exposes and \
                                not any(a == function.id for a in child.allocated_function_list):
                            Logger.set_warning(__name__,
                                               f'Child {child.name} of Functional element {fun_elem.name} exposes also '
                                               f'the Functional interface {fun_inter.name}. Please consider to '
                                               f'allocate the Function {function.name} to it.')

    return [is_consumer, is_producer]


def check_allocation_information(p_obj, p_information, **kwargs):
    xml_consumer_function_list = kwargs[XML_DICT_KEY_15_FUN_CONS_LIST]
    xml_producer_function_list = kwargs[XML_DICT_KEY_16_FUN_PROD_LIST]
    xml_consumer_activity_list = kwargs[XML_DICT_KEY_17_ACT_CONS_LIST]
    xml_producer_activity_list = kwargs[XML_DICT_KEY_18_ACT_PROD_LIST]
    pair = None

    if not any(allocated_info_id == p_information.id for allocated_info_id in p_obj.allocated_info_list):
        for xml_consumer_function in xml_consumer_function_list:
            if xml_consumer_function[0] == p_obj:
                for allocated_activity_id in xml_consumer_function[1].allocated_activity_list:
                    for xml_consumer_activity in xml_consumer_activity_list:
                        if xml_consumer_activity[1].id == allocated_activity_id and xml_consumer_activity[0] == p_information:
                            pair = [p_obj, p_information]
                        # Else do nothing
            #Else do nothing

        if not pair:
            for xml_producer_function in xml_producer_function_list:
                if xml_producer_function[0] == p_obj:
                    for allocated_activity_id in xml_producer_function[1].allocated_activity_list:
                        for xml_producer_activity in xml_producer_activity_list:
                            if xml_producer_activity[1].id == allocated_activity_id and xml_producer_activity[0] == p_information:
                                pair = [p_obj, p_information]
                            # Else do nothing
                # Else do nothing
        # Else do nothing
    # Else do nothing

    return pair


def add_allocation(allocation_dict, **kwargs):
    """
    Check if allocation_lists is not empty, write in xml for each list and return 0/1
    if some update has been made.

        Parameters:
            allocation_dict : Containing all allocation to write within xml
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(allocation_dict.values()):
        for _, k in enumerate(allocation_dict):
            if allocation_dict[k]:
                output_xml = kwargs['output_xml']
                output_xml.write_object_allocation(allocation_dict[k])
                # Warn the user once added within xml
                for elem in allocation_dict[k]:
                    Logger.set_info(__name__,
                                    f"{elem[1].__class__.__name__} {elem[1].name} is allocated to "
                                    f"{elem[0].__class__.__name__} {elem[0].name}")

                    orchestrator_object.check_object_instance_list_requirement([elem[0], elem[1]], **kwargs)

                    if isinstance(elem[1].type, datamodel.BaseType):
                        object_type = elem[1].type
                    else:
                        _, object_type = orchestrator_object.retrieve_type(elem[1].type.name, True, **kwargs)

                    if k == OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX and object_type == datamodel.BaseType.FUNCTION:
                        # Allocation of function to state
                        # Need to remove previous allocation if any
                        xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
                        xml_phy_elem_list = kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST]
                        xml_state_list = kwargs[XML_DICT_KEY_6_STATE_LIST]
                        xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]

                        for xml_state in xml_state_list:
                            if xml_state.id != elem[0].id:
                                if elem[1].id in xml_state.allocated_function_list:
                                    is_fun_elem = False
                                    for xml_fun_elem in xml_fun_elem_list:
                                        if xml_state.id in xml_fun_elem.allocated_state_list:
                                            is_fun_elem = True
                                            if elem[0].id not in xml_fun_elem.allocated_state_list:
                                                xml_state.remove_allocated_function(elem[1].id)
                                                output_xml.delete_object_allocation([[xml_state, elem[1]]])
                                                Logger.set_info(__name__,
                                                                f"Function {elem[1].name} is not allocated to "
                                                                f"State {xml_state.name} anymore")
                                                xml_fun_elem.remove_allocated_function(elem[1].id)
                                                output_xml.delete_object_allocation([[xml_fun_elem, elem[1]]])
                                                Logger.set_info(__name__,
                                                                f"Function {elem[1].name} is not allocated to "
                                                                f"Functional element {xml_fun_elem.name} anymore")

                                            else:
                                                Logger.set_info(__name__,
                                                                f"Function {elem[1].name} is still allocated to "
                                                                f"State {xml_state.name}")
                                                Logger.set_info(__name__,
                                                                f"Function {elem[1].name} is still allocated to "
                                                                f"Functional element {xml_fun_elem.name}")
                                        # Else do nothing

                                    if not is_fun_elem:
                                        xml_state.remove_allocated_function(elem[1].id)
                                        output_xml.delete_object_allocation([[xml_state, elem[1]]])
                                        Logger.set_info(__name__,
                                                        f"Function {elem[1].name} is not allocated to "
                                                        f"State {xml_state.name} anymore")
                                # Else do nothing
                            # Else do nothing

                        # Finalize allocation
                        for xml_fun_elem in xml_fun_elem_list:
                            # Check if state is allocated to functional element to allocate function to
                            # functional element
                            if elem[0].id in xml_fun_elem.allocated_state_list and elem[1].id not in \
                                    xml_fun_elem.allocated_function_list:
                                xml_fun_elem.add_allocated_function(elem[1].id)
                                output_xml.write_object_allocation([[xml_fun_elem, elem[1]]])
                                Logger.set_info(__name__,
                                                f"{elem[1].__class__.__name__} {elem[1].name} is allocated to "
                                                f"{xml_fun_elem.__class__.__name__} {xml_fun_elem.name}")
                            # Check if state is not allocated to functional element to allocate state to
                            # functional element
                            elif elem[0].id not in xml_fun_elem.allocated_state_list and \
                                    elem[1].id in elem[0].allocated_function_list and \
                                    elem[1].id in xml_fun_elem.allocated_function_list:
                                xml_fun_elem.add_allocated_state(elem[0].id)
                                output_xml.write_object_allocation([[xml_fun_elem, elem[0]]])
                                Logger.set_info(__name__,
                                                f"{elem[0].__class__.__name__} {elem[0].name} is allocated to "
                                                f"{xml_fun_elem.__class__.__name__} {xml_fun_elem.name}")
                            # Else do nothing

                        if len(elem[1].allocated_activity_list) > 0:
                            # Need to check if state allocated to fun elem allocated to phy elem
                            # to allocate activity to phy elem
                            for xml_fun_elem in xml_fun_elem_list:
                                if elem[1].id in xml_fun_elem.allocated_function_list:
                                    for xml_phy_elem in xml_phy_elem_list:
                                        if xml_fun_elem.id in xml_phy_elem.allocated_fun_elem_list:
                                            for allocated_activity_id in elem[1].allocated_activity_list:
                                                for xml_activity in xml_activity_list:
                                                    if xml_activity.id == allocated_activity_id \
                                                            and xml_activity.id not in \
                                                            xml_phy_elem.allocated_activity_list:
                                                        xml_phy_elem.add_allocated_activity(xml_activity.id)
                                                        output_xml.write_object_allocation([[xml_phy_elem,
                                                                                             xml_activity]])
                                                        Logger.set_info(__name__,
                                                                        f"{xml_activity.__class__.__name__} "
                                                                        f"{xml_activity.name} is allocated to "
                                                                        f"{xml_phy_elem.__class__.__name__} "
                                                                        f"{xml_phy_elem.name}")
                                                    # Else do nothing
                                        # Else do nothing
                                # Else do nothing
                        #Else do nothing
                    elif k == OBJ_ALLOCATION_TO_FUNCTION_IDX and object_type == datamodel.BaseType.ACTIVITY:
                        # Allocation of activity to function
                        # Need to add activity to physical element if any
                        xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
                        xml_phy_elem_list = kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST]

                        for xml_fun_elem in xml_fun_elem_list:
                            if elem[0].id in xml_fun_elem.allocated_function_list:
                                for xml_phy_elem in xml_phy_elem_list:
                                    if xml_fun_elem.id in xml_phy_elem.allocated_fun_elem_list \
                                            and elem[1].id not in xml_phy_elem.allocated_activity_list:
                                        xml_phy_elem.add_allocated_activity(elem[1].id)
                                        output_xml.write_object_allocation([[xml_phy_elem, elem[1]]])
                                        Logger.set_info(__name__,
                                                        f"{elem[1].__class__.__name__} {elem[1].name} is allocated to "
                                                        f"{xml_phy_elem.__class__.__name__} {xml_phy_elem.name}")
                                    # Else do nothing
                            # Else do nothing
                    elif k == OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX and object_type == datamodel.BaseType.FUNCTION:
                        xml_phy_elem_list = kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST]
                        xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]

                        if len(elem[1].allocated_activity_list) > 0:
                            # Need to check if fun elem allocated to phy elem
                            # to allocate activity to phy elem
                            for xml_phy_elem in xml_phy_elem_list:
                                if elem[0].id in xml_phy_elem.allocated_fun_elem_list:
                                    for allocated_activity_id in elem[1].allocated_activity_list:
                                        for xml_activity in xml_activity_list:
                                            if xml_activity.id == allocated_activity_id \
                                                    and xml_activity.id not in xml_phy_elem.allocated_activity_list:
                                                xml_phy_elem.add_allocated_activity(xml_activity.id)
                                                output_xml.write_object_allocation([[xml_phy_elem,
                                                                                     xml_activity]])
                                                Logger.set_info(__name__,
                                                                f"{xml_activity.__class__.__name__} "
                                                                f"{xml_activity.name} is allocated to "
                                                                f"{xml_phy_elem.__class__.__name__} "
                                                                f"{xml_phy_elem.name}")
                                            # Else do nothing
                                # Else do nothing
                        # Else do nothing
                    elif k == OBJ_ALLOCATION_TO_PHY_ELEM_IDX and object_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
                        xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
                        xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]

                        for allocated_fun_id in elem[1].allocated_function_list:
                            for xml_fun in xml_function_list:
                                if xml_fun.id == allocated_fun_id:
                                    for allocated_activity_id in xml_fun.allocated_activity_list:
                                        for xml_activity in xml_activity_list:
                                            if xml_activity.id == allocated_activity_id \
                                                    and xml_activity.id not in elem[0].allocated_activity_list:
                                                elem[0].add_allocated_activity(xml_activity.id)
                                                output_xml.write_object_allocation([[elem[0],
                                                                                     xml_activity]])
                                                Logger.set_info(__name__,
                                                                f"{xml_activity.__class__.__name__} "
                                                                f"{xml_activity.name} is allocated to "
                                                                f"{elem[0].__class__.__name__} "
                                                                f"{elem[0].name}")
                                            # Else do nothing

                    # Else do nothing

                    if k in (OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX, OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX):
                        allocate_all_children_in_element(elem, **kwargs)
        return 1
    return 0


def allocate_all_children_in_element(elem, **kwargs):
    """Recursive allocation for children of State/Function"""
    output_xml = kwargs['output_xml']
    check_parent_allocation(elem, **kwargs)

    if isinstance(elem[1].type, datamodel.BaseType):
        object_type = elem[1].type
    else:
        _, object_type = orchestrator_object.retrieve_type(elem[1].type.name, True, **kwargs)

    if elem[1].child_list:
        for i in elem[1].child_list:
            parent_child = [elem[1], i]
            allocated_child_list = get_allocated_child(parent_child, [elem[0]])
            if allocated_child_list:
                for item in allocated_child_list:
                    if isinstance(elem[1], datamodel.State):
                        item[0].add_allocated_state(item[1].id)
                    else:
                        item[0].add_allocated_function(item[1].id)

                # We want recursivety so it trigger for (0, 1) keys in the dict
                if isinstance(elem[0], datamodel.FunctionalElement):
                    add_allocation({OBJ_ALLOCATION_TO_FUN_ELEM_RECURSIVELY_IDX: allocated_child_list}, **kwargs)
                else:
                    add_allocation({OBJ_ALLOCATION_TO_STATE_RECURSIVELY_IDX: allocated_child_list}, **kwargs)
    else:
        if object_type == datamodel.BaseType.STATE and elem[1].id not in elem[0].allocated_state_list:
            # Remove previous allocation if any
            xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
            for xml_fun_elem in xml_fun_elem_list:
                if elem[1].id in xml_fun_elem.allocated_state_list:
                    xml_fun_elem.remove_allocated_state(elem[1].id)
                    output_xml.delete_object_allocation([[xml_fun_elem, elem[1]]])
                    Logger.set_info(__name__,
                                    f"State {elem[1].name} is not allocated to Functional element "
                                    f"{xml_fun_elem.name} anymore")

            elem[0].add_allocated_state(elem[1].id)
            add_allocation({OBJ_ALLOCATION_TO_FUN_ELEM_IDX: [elem]}, **kwargs)
        elif object_type == datamodel.BaseType.FUNCTION and elem[1].id not in elem[0].allocated_function_list:
            # Remove previous allocation if any
            xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
            for xml_fun_elem in xml_fun_elem_list:
                if elem[1].id in xml_fun_elem.allocated_function_list:
                    xml_fun_elem.remove_allocated_function(elem[1].id)
                    output_xml.delete_object_allocation([[xml_fun_elem, elem[1]]])
                    Logger.set_info(__name__,
                                    f"Function {elem[1].name} is not allocated to Functional element "
                                    f"{xml_fun_elem.name} anymore")

            elem[0].add_allocated_function(elem[1].id)
            if isinstance(elem[0], datamodel.FunctionalElement):
                add_allocation({OBJ_ALLOCATION_TO_FUN_ELEM_IDX: [elem]}, **kwargs)
            else:
                add_allocation({OBJ_ALLOCATION_TO_STATE_IDX: [elem]}, **kwargs)


def check_parent_allocation(elem, **kwargs):
    """Check if parent's Function/State are allocated to parent's Functional Element:
    if not print message to user asking if he wants to, if yes write it in xml then continue
    with parents"""
    if elem[0].parent is not None and elem[1].parent is not None:
        fun_elem_parent_list = orchestrator_object.retrieve_object_parents_recursively(elem[0])
        object_parent_list = orchestrator_object.retrieve_object_parents_recursively(elem[1])

        check = False
        if isinstance(elem[1], datamodel.State):
            for object_parent in object_parent_list:
                for fun_elem_parent in fun_elem_parent_list:
                    if object_parent.id in fun_elem_parent.allocated_state_list:
                        check = True
                        break
                    # Else do nothing
        elif isinstance(elem[1], datamodel.Function):
            for object_parent in object_parent_list:
                for fun_elem_parent in fun_elem_parent_list:
                    if object_parent.id in fun_elem_parent.allocated_function_list:
                        check = True
                        break
                    # Else do nothing
        # Else do nothing

        if not check:
            answer, _ = handler_question.question_to_user(f"Do you also want to allocate parents "
                                                          f"(i.e. {elem[1].parent.name} "
                                                          f"to {elem[0].parent.name}) ? (Y/N)")
            if answer.lower() == "y":
                if isinstance(elem[1], datamodel.State):
                    elem[0].parent.add_allocated_state(elem[1].parent.id)
                    add_allocation({OBJ_ALLOCATION_TO_STATE_IDX: [[elem[0].parent, elem[1].parent]]}, **kwargs)
                    check_parent_allocation([elem[0].parent, elem[1].parent], **kwargs)
                elif isinstance(elem[1], datamodel.Function):
                    elem[0].parent.add_allocated_function(elem[1].parent.id)
                    add_allocation({OBJ_ALLOCATION_TO_FUNCTION_IDX: [[elem[0].parent, elem[1].parent]]}, **kwargs)
                    check_parent_allocation([elem[0].parent, elem[1].parent], **kwargs)
                # Else do nothing
            else:
                Logger.set_warning(__name__,
                                   f"{elem[1].parent.name} is not allocated despite at least one "
                                   f"of its child is")
        # Else do nothing


def get_allocated_child(elem, xml_fun_elem_list):
    """
    Check if the parent state/function is already allocated to a fun elem and create list to add
    its child also (if not already allocated)

        Parameters:
            elem ([State/Function]) : parent object, child object
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing

        Returns:
            output_list ([FunctionalElement, State/Function]) : Allocation Relationships that need
            to be added
    """
    output_list = []
    for fun_elem in xml_fun_elem_list:
        if isinstance(elem[0], datamodel.State):
            # To avoid "RuntimeError: Set changed size during iteration" copy()
            allocated_list = fun_elem.allocated_state_list.copy()
        else:
            allocated_list = fun_elem.allocated_function_list.copy()
        if allocated_list:
            for allocated_object in allocated_list:
                if allocated_object == elem[0].id:
                    if elem[1].id not in allocated_list:
                        if isinstance(elem[0], datamodel.State):
                            fun_elem.add_allocated_state(elem[1].id)
                        else:
                            fun_elem.add_allocated_function(elem[1].id)
                        output_list.append([fun_elem, elem[1]])

    return output_list
