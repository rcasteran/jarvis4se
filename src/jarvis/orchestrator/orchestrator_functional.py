""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_ATTRIBUTE_LIST, XML_DICT_KEY_11_VIEW_LIST, \
    XML_DICT_KEY_12_TYPE_LIST, XML_DICT_KEY_13_FUN_CONS_LIST, XML_DICT_KEY_14_FUN_PROD_LIST
from . import orchestrator_object, orchestrator_object_allocation, orchestrator_viewpoint_requirement
from jarvis import util
from tools import Logger


def check_add_predecessor(data_predecessor_str_set, **kwargs):
    """
    Check if each string in data_predecessor_str_set is corresponding to an actual Data object,
    create new [Data, predecessor] objects lists for object's type : Data.
    Send lists to add_predecessor() to write them within xml and then returns update_list from it.

        Parameters:
            data_predecessor_str_set ([str]) : Lists of string from jarvis cell
            xml_data_list ([Data]) : Data list from xml parsing
            xml_view_list ([View]) : View list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    xml_data_list = kwargs[XML_DICT_KEY_0_DATA_LIST]
    output_xml = kwargs['output_xml']

    data_predecessor_list = []

    allocated_item_list = []
    # Filter input string
    data_predecessor_str_list = util.cut_tuple_list(data_predecessor_str_set)

    # Create data names list already in xml
    xml_data_name_list = orchestrator_object.check_object_name_in_list(xml_data_list)

    for elem in data_predecessor_str_list:
        is_elem_found = True
        if elem[0] not in xml_data_name_list:
            is_elem_found = False
            if elem[1] not in xml_data_name_list:
                Logger.set_error(__name__,
                                 f"{elem[0]} and {elem[1]} do not exist")
            else:
                Logger.set_error(__name__,
                                 f"{elem[0]} does not exist")

        if elem[0] in xml_data_name_list:
            if elem[1] not in xml_data_name_list:
                is_elem_found = False
                Logger.set_error(__name__,
                                 f"{elem[1]} does not exist")

        if is_elem_found:
            predecessor = None
            selected_data = None
            existing_predecessor_id_list = []

            for data in xml_data_list:
                if elem[0] == data.name:
                    selected_data = data
                    for existing_predecessor in data.predecessor_list:
                        existing_predecessor_id_list.append(existing_predecessor.id)

            for da in xml_data_list:
                if elem[1] == da.name and da.id not in existing_predecessor_id_list:
                    predecessor = da

            if predecessor is not None and selected_data is not None:
                data_predecessor_list.append([selected_data, predecessor])
                orchestrator_object_allocation.check_add_allocated_item_to_view(elem[0], **kwargs)
                orchestrator_object_allocation.check_add_allocated_item_to_view(elem[1], **kwargs)

    update = add_predecessor(data_predecessor_list, xml_data_list, output_xml)

    return update


def add_predecessor(predecessor_list, xml_data_list, output_xml):
    """
    Check if input lists is not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            predecessor_list ([Data, Data(predecessor)]) : Data object to set new predessor and
            predecessor Data
            xml_data_list ([Data]) : Data list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """

    if not predecessor_list:
        return 0

    output_xml.write_data_predecessor(predecessor_list)

    for data_predecessor in predecessor_list:
        for d in xml_data_list:
            if data_predecessor[0].id == d.id:
                d.add_predecessor(data_predecessor[1])

        Logger.set_info(__name__,
                        f"{data_predecessor[1].name} predecessor for "
                        f"{data_predecessor[0].name}")

    return 1


def check_add_consumer_function(consumer_str_list, **kwargs):
    """
    Check if each string in consumer_str_list are corresponding to an actual object, create new
    [data, consumer] objects list for object's type : Function.
    Send lists to add_consumer_function() to write them within xml and then returns update_list
    from it.

        Parameters:
            consumer_str_list ([str]) : Lists of string from jarvis cell
            xml_consumer_function_list ([Data, Function]) : Data and consumer's
            function list from xml
            xml_producer_function_list ([Data, Function]) : Data and producer's
            function list from xml
            xml_function_list ([Function]) : Function list from xml parsing
            xml_data_list ([Data]) : Data list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    xml_consumer_function_list = kwargs[XML_DICT_KEY_13_FUN_CONS_LIST]
    xml_producer_function_list = kwargs[XML_DICT_KEY_14_FUN_PROD_LIST]
    xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
    xml_data_list = kwargs[XML_DICT_KEY_0_DATA_LIST]
    output_xml = kwargs['output_xml']

    new_consumer_list = []
    # Create object names/aliases list and data's name
    xml_function_name_list = orchestrator_object.check_object_name_in_list(xml_function_list)
    xml_data_name_list = orchestrator_object.check_object_name_in_list(xml_data_list)
    # Loop to filter consumer and create a new list
    # elem = [data_name, consumer_function_name]
    for elem in consumer_str_list:
        data_name = elem[0].replace('"', "")
        consumer_function_name = elem[1].replace('"', "")

        is_elem_found = True
        if not any(item == consumer_function_name for item in xml_function_name_list) and \
                not any(item == data_name for item in xml_data_name_list):
            is_elem_found = False
            Logger.set_error(__name__,
                             f"{consumer_function_name} and {data_name} do not exist")
        elif not any(item == consumer_function_name for item in xml_function_name_list) or \
                not any(item == data_name for item in xml_data_name_list):
            is_elem_found = False
            if any(item == consumer_function_name for item in xml_function_name_list) and \
                    not any(item == data_name for item in xml_data_name_list):
                Logger.set_error(__name__,
                                 f"{data_name} does not exist")
            elif any(item == data_name for item in xml_data_name_list) and \
                    not any(item == consumer_function_name for item in xml_function_name_list):
                Logger.set_error(__name__,
                                 f"{consumer_function_name} does not exist")

        if is_elem_found:
            Logger.set_debug(__name__, f"[{data_name}, {consumer_function_name}] check")
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if consumer_function_name == function.name or consumer_function_name == function.alias:
                    for data in xml_data_list:
                        if data_name == data.name:
                            is_warned, _ = check_opposite(data, xml_producer_function_list, "consumer", False)
                            if [data, function] not in xml_consumer_function_list:
                                add_producer_consumer_flow_recursively(data,
                                                                       function,
                                                                       xml_consumer_function_list,
                                                                       xml_producer_function_list,
                                                                       new_consumer_list,
                                                                       output_xml,
                                                                       "consumer",
                                                                       is_warned)
                                break
                        # Else do nothing
                # Else do nothing
        # Else do nothing

    Logger.set_debug(__name__, f"{consumer_str_list}: {new_consumer_list}")
    update = add_consumer_function(new_consumer_list, **kwargs)

    return update


def add_consumer_function(new_consumer_list, **kwargs):
    """
    Check if input list is not empty, write in xml for each element and return update list if some
    updates has been made

        Parameters:
            new_consumer_list ([Data, Function]) : Data and consumer's function list

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """

    if not new_consumer_list:
        return 0

    xml_consumer_function_list = kwargs[XML_DICT_KEY_13_FUN_CONS_LIST]
    output_xml = kwargs['output_xml']
    output_xml.write_data_consumer(new_consumer_list)

    # Warn the user once added within xml
    for consumer in new_consumer_list:
        xml_consumer_function_list.append(consumer)
        orchestrator_object.check_object_instance_list_requirement(consumer, **kwargs)

        Logger.set_info(__name__,
                        f"{consumer[1].name} consumes {consumer[0].name}")

    return 1


def add_producer_consumer_flow_recursively(flow, function, current_list, opposite_list, new_list, output_xml,
                                           relationship_str, is_warned):
    """
    Recursive method to add producer / consumer function for a flow.
        Parameters:
            flow (Data) : Data
            function (Function) : Current function's parent
            current_list ([Data_name_str, function_name_str]) : 'Current' list (producer/consumer)
            opposite_list ([Data_name_str, function_name_str]) : Opposite list from current
            new_list ([Data_name_str, Function]) : Data's name and consumer/producer's function list
            output_xml (XmlWriter3SE object) : XML's file object
            relationship_str (str) : "consumer" or "producer"
            out (bool) : List for recursivity
        Returns:
            elem ([data, Function]) : Return parent

    """
    # Prevent function.parent to be added twice
    if [flow, function] not in new_list and [flow, function] not in current_list:
        new_list.append([flow, function])
        Logger.set_debug(__name__, f"[{flow.name}, {function.name}] added")

        # Check that parent opposite flow is present (if any)
        is_warned, opposite_function = check_opposite(flow, opposite_list, relationship_str, is_warned)
        if opposite_function:
            if opposite_function == function.parent:
                if any([flow, child_f] in opposite_list for child_f in opposite_function.child_list):
                    remove_producer_consumer_opposite(flow, opposite_function, opposite_list, output_xml,
                                                      relationship_str)
                else:
                    if relationship_str == 'consumer':
                        Logger.set_error(__name__, f'{opposite_function.name} is a producer of {flow.name} '
                                                   f'but one of its child is a {relationship_str}')
                    else:
                        Logger.set_error(__name__, f'{opposite_function.name} is a consumer of {flow.name} '
                                                   f'but one of its child is a {relationship_str}')
            elif opposite_function.parent is not None and opposite_function.parent != function and \
                    opposite_function.parent != function.parent:
                if [flow, opposite_function.parent] not in opposite_list:
                    add_producer_consumer_opposite(flow, opposite_function.parent, opposite_list, output_xml,
                                                   relationship_str)
                # Else do nothing
            # Else do nothing
        # Else do nothing

    if function.parent is not None:
        parent_child_list, parent_child_dict = orchestrator_object.retrieve_object_children_recursively(function.parent)

        if not any([flow, parent_child] in opposite_list for parent_child in parent_child_list):
            add_producer_consumer_flow_recursively(flow, function.parent, current_list, opposite_list, new_list,
                                                   output_xml,
                                                   relationship_str,
                                                   is_warned)
        elif [flow, function.parent] in opposite_list:
            # Check that no other function needs the flow before removing it
            ext_function_list = []
            for [current_flow, current_function] in current_list:
                if current_flow == flow:
                    Logger.set_debug(__name__, f"[{current_flow.name}, {current_function.name}] "
                                               f"added in external function list")
                    ext_function_list.append([current_flow, current_function])

            for parent_child in parent_child_list:
                if [flow, parent_child] in ext_function_list:
                    ext_function_list.remove([flow, parent_child])

            if len(ext_function_list) == 0:
                remove_producer_consumer_opposite(flow, function.parent, opposite_list, output_xml, relationship_str)
            else:
                Logger.set_debug(__name__, f"[{flow.name}, {function.parent.name}] still needed")


def check_opposite(flow, opposite_list, relationship_str, is_warned):
    # Check that parent opposite flow is present (if any)
    opposite_flow_function = None
    for [opposite_flow, opposite_function] in opposite_list:
        if opposite_flow == flow:
            opposite_flow_function = opposite_function
            break
        # Else do nothing

    if not opposite_flow_function and not is_warned:
        is_warned = True
        if relationship_str == "consumer":
            Logger.set_warning(__name__, f"No producer found for {flow.name}")
        elif relationship_str == "producer":
            Logger.set_warning(__name__, f"No consumer found for {flow.name}")
        else:
            Logger.set_error(__name__, f"Unsupported data relationship type: {relationship_str}")
    # Else do nothing

    return is_warned, opposite_flow_function


def add_producer_consumer_opposite(flow, function, flow_function_list, output_xml, relationship_type):
    """
    Add specific consumer/producer relationship within xml's file.

        Parameters:
            flow (Data) : Data
            function (Function) : Current Function object
            flow_function_list : list of [flow, function]
            output_xml (XmlWriter3SE object) : XML's file object
            relationship_type (str) : Type of relationship (i.e. consumer or producer)
        Returns:
            None
    """
    flow_function_list.append([flow, function])

    if relationship_type == "producer":
        output_xml.write_data_relationship([flow, function],
                                           "consumer")
        Logger.set_info(__name__,
                        f"{function.name} consumes {flow.name} due to one of its children")
    elif relationship_type == "consumer":

        output_xml.write_data_relationship([flow, function],
                                           "producer")
        Logger.set_info(__name__,
                        f"{function.name} produces {flow.name} due to one of its children")

    if function.parent:
        add_producer_consumer_opposite(flow, function.parent, flow_function_list, output_xml, relationship_type)


def remove_producer_consumer_opposite(flow, function, flow_function_list, output_xml, relationship_type):
    """
    Delete specific consumer/producer relationship within xml's file.

        Parameters:
            flow (Data) : Data
            function (Function) : Current Function object
            flow_function_list : list of [flow, function]
            output_xml (XmlWriter3SE object) : XML's file object
            relationship_type (str) : Type of relationship (i.e. consumer or producer)
        Returns:
            None
    """
    flow_function_list.remove([flow, function])

    if relationship_type == "producer":
        output_xml.delete_data_relationship([flow, function],
                                            "consumer")
        Logger.set_info(__name__,
                        f"{function.name} does not consume {flow.name} anymore")
    elif relationship_type == "consumer":

        output_xml.delete_data_relationship([flow, function],
                                            "producer")
        Logger.set_info(__name__,
                        f"{function.name} does not produce {flow.name} anymore")

    if function.parent and [flow, function.parent] in flow_function_list:
        remove_producer_consumer_opposite(flow, function.parent, flow_function_list, output_xml, relationship_type)


def check_add_producer_function(producer_str_list, **kwargs):
    """
    Check if each string in consumer_str_list are corresponding to an actual object, create new
    [data, producer] objects list for object's type : Function.
    Send list to add_producer_function() to write them within xml and then returns update.

        Parameters:
            producer_str_list ([str]) : List of string from jarvis cell
            xml_consumer_function_list ([Data_name_str, Function]) : Data's name and consumer's
            function list from xml
            xml_producer_function_list ([Data_name_str, Function]) : Data's name and producer's
            function list from xml
            xml_function_list ([Function]) : Function list from xml parsing
            xml_data_list ([Data]) : Data list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    xml_consumer_function_list = kwargs[XML_DICT_KEY_13_FUN_CONS_LIST]
    xml_producer_function_list = kwargs[XML_DICT_KEY_14_FUN_PROD_LIST]
    xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
    xml_data_list = kwargs[XML_DICT_KEY_0_DATA_LIST]
    output_xml = kwargs['output_xml']

    new_producer_list = []
    # Create object names/aliases list
    xml_function_name_list = orchestrator_object.check_object_name_in_list(xml_function_list)
    xml_data_name_list = orchestrator_object.check_object_name_in_list(xml_data_list)
    # Loop to filter producer and create a new list
    # elem = [data_name, producer_function_name]
    for elem in producer_str_list:
        data_name = elem[0].replace('"', "")
        producer_function_name = elem[1].replace('"', "")

        is_elem_found = True
        if not any(item == producer_function_name for item in xml_function_name_list) and \
                not any(item == data_name for item in xml_data_name_list):
            is_elem_found = False
            Logger.set_error(__name__,
                             f"{producer_function_name} and {data_name} do not exist")
        elif not any(item == producer_function_name for item in xml_function_name_list) or \
                not any(item == data_name for item in xml_data_name_list):
            is_elem_found = False
            if any(item == producer_function_name for item in xml_function_name_list) and \
                    not any(item == data_name for item in xml_data_name_list):
                Logger.set_error(__name__,
                                 f"{data_name} does not exist")
            elif any(item == data_name for item in xml_data_name_list) and \
                    not any(item == producer_function_name for item in xml_function_name_list):
                Logger.set_error(__name__,
                                 f"{producer_function_name} does not exist")

        if is_elem_found:
            Logger.set_debug(__name__, f"[{data_name}, {elem[1]}] check")
            # Loop to filter consumer and create a new list
            for function in xml_function_list:
                if producer_function_name == function.name or producer_function_name == function.alias:
                    for data in xml_data_list:
                        if data_name == data.name:
                            is_warned, _ = check_opposite(data, xml_consumer_function_list, "producer", False)
                            if [data, function] not in xml_producer_function_list:
                                add_producer_consumer_flow_recursively(data,
                                                                       function,
                                                                       xml_producer_function_list,
                                                                       xml_consumer_function_list,
                                                                       new_producer_list,
                                                                       output_xml,
                                                                       "producer",
                                                                       is_warned)
                                break
                        # Else do nothing
                # Else do nothing
        # Else do nothing

    Logger.set_debug(__name__, f"{producer_str_list}: {new_producer_list}")
    update = add_producer_function(new_producer_list, **kwargs)

    return update


def add_producer_function(new_producer_list, **kwargs):
    """
    Check if input list is not empty, write in xml for each element and return update list if some
    updates has been made

        Parameters:
            new_producer_list ([Data_name_str, Function]) : Data's name and producer's function list

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if not new_producer_list:
        return 0

    xml_producer_function_list = kwargs[XML_DICT_KEY_14_FUN_PROD_LIST]
    output_xml = kwargs['output_xml']
    output_xml.write_data_producer(new_producer_list)

    # Warn the user once added within xml
    for producer in new_producer_list:
        xml_producer_function_list.append(producer)
        orchestrator_object.check_object_instance_list_requirement(producer, **kwargs)

        Logger.set_info(__name__,
                        f"{producer[1].name} produces {producer[0].name}")
    return 1


# TODO: Check condition_str on data and (add LogicalType, ArithmeticType in datamodel.py)
def check_add_transition_condition(trans_condition_str_list, **kwargs):
    """
    Check if each string in trans_condition_str_list is corresponding to an actual Transition
    object, create new [Transition, condition_str] objects lists for object's type : Transition.
    Send lists to add_transition_condition() to write them within xml and then returns update_list
    from it.

        Parameters:
            trans_condition_str_list ([str]) : Lists of string from jarvis cell
            xml_transition_list ([Transition]) : Transition list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    xml_transition_list = kwargs[XML_DICT_KEY_7_TRANSITION_LIST]
    condition_list = []

    # Create a list with all transition names/aliases already in the xml
    xml_transition_name_list = orchestrator_object.check_object_name_in_list(xml_transition_list)
    # elem = [transition_name, condition_str]
    for elem in trans_condition_str_list:
        transition_name = elem[0].replace('"', "")
        condition_str = elem[1].replace('"', "")

        is_elem_found = True
        if not any(transition_name in s for s in xml_transition_name_list):
            is_elem_found = False
            Logger.set_error(__name__,
                             f"The transition {transition_name} does not exist")

        if is_elem_found:
            for transition in xml_transition_list:
                if transition_name == transition.name or transition_name == transition.alias:
                    if not condition_str.lstrip(' ') in transition.condition_list:
                        condition_list.append([transition, condition_str.lstrip(' ')])
                    else:
                        Logger.set_info(__name__,
                                        f'Condition "{condition_str.lstrip(" ")}" already exists '
                                        f'for transition {transition_name}')

    check_condition_list_requirement(condition_list, **kwargs)
    update = add_transition_condition(condition_list, **kwargs)

    return update


def check_condition_list_requirement(p_condition_list, **kwargs):
    xml_requirement_list = kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
    output_xml = kwargs['output_xml']

    for condition in p_condition_list:
        for xml_requirement in xml_requirement_list:
            _, _, _, xml_requirement_temporal = \
                orchestrator_viewpoint_requirement.detect_req_pattern(xml_requirement.text)

            if len(xml_requirement_temporal) > 0:
                if xml_requirement_temporal in condition[1]:
                    if xml_requirement.id not in condition[0].allocated_req_list:
                        condition[0].add_allocated_requirement(xml_requirement.id)
                        output_xml.write_object_allocation([[condition[0], xml_requirement]])

                        Logger.set_info(__name__,
                                        f"{xml_requirement.__class__.__name__} {xml_requirement.name} is satisfied by "
                                        f"{condition[0].__class__.__name__} {condition[0].name}")
                    # Else do nothing
                # Else do nothing
            # Else do nothing


def add_transition_condition(condition_list, **kwargs):
    """
    Check if input list is not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            condition_list ([Transition, condition_str]) : Transition object and conditions as str
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    output_xml = kwargs['output_xml']
    update = 0

    if condition_list:
        output_xml.write_transition_condition(condition_list)

        for elem in condition_list:
            elem[0].add_condition(elem[1])
            Logger.set_info(__name__,
                            f"Condition for {elem[0].name} : {elem[1]}")

        update = 1

    return update


def check_add_src_dest(src_dest_str, **kwargs):
    """
    Check if each string in src_dest_str is corresponding to an actual Transition and State object,
    create new [Transition, State] objects lists.
    Send lists to add_src_dest() to write them within xml and then returns update_list from it.

        Parameters:
            src_dest_str ([str]) : Lists of string from jarvis cell
            xml_transition_list ([Transition]) : Transition list from xml parsing
            xml_state_list ([State]) : State list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    xml_transition_list = kwargs[XML_DICT_KEY_7_TRANSITION_LIST]
    xml_state_list = kwargs[XML_DICT_KEY_6_STATE_LIST]
    output_xml = kwargs['output_xml']

    new_src_list = []
    new_dest_list = []
    # Create lists with all object names/aliases already in the xml
    xml_transition_name_list = orchestrator_object.check_object_name_in_list(xml_transition_list)
    xml_state_name_list = orchestrator_object.check_object_name_in_list(xml_state_list)

    concatenated_lists = [*xml_transition_name_list, *xml_state_name_list]

    # elem = [source/destination, transition_name, state_name]
    for elem in src_dest_str:
        transition_name = elem[1].replace('"', "")
        state_name = elem[2].replace('"', "")

        is_elem_found = True
        if not all(t in concatenated_lists for t in [transition_name, state_name]):
            is_elem_found = False
            if any(transition_name in s for s in xml_transition_name_list) and not any(
                    state_name in j for j in xml_state_name_list):
                Logger.set_error(__name__,
                                 f"{state_name} state does not exist")
            elif any(state_name in s for s in xml_state_name_list) and not any(
                    transition_name in j for j in xml_transition_name_list):
                Logger.set_error(__name__,
                                 f"{transition_name} transition does not exist")
            else:
                Logger.set_error(__name__,
                                 f"{transition_name} transition and {state_name} state do not exist")

        if is_elem_found:
            if elem[0] == "source":
                for transition in xml_transition_list:
                    if transition_name == transition.name or transition_name == transition.alias:
                        for state in xml_state_list:
                            if state_name == state.name or state_name == state.alias:
                                if not isinstance(state.type, datamodel.BaseType):
                                    if datamodel.ExitStateLabel in state.type.name.lower():
                                        Logger.set_error(__name__,
                                                         f"{state_name} is typed as EXIT state, "
                                                         f"it cannot be put as source's transition (not added)")
                                    elif datamodel.EntryStateLabel in state.type.name.lower():
                                        if transition.source != state.id:
                                            new_src_list.append([transition, state])
                                        else:
                                            Logger.set_info(__name__,
                                                            f'{state_name} already the source of transition '
                                                            f'{transition_name}')
                                    else:
                                        Logger.set_error(__name__,
                                                         f"{state_name} is not typed as state, "
                                                         f"it cannot be put as source's transition (not added)")
                                else:
                                    if transition.source != state.id:
                                        new_src_list.append([transition, state])
                                    else:
                                        Logger.set_info(__name__,
                                                        f'{state_name} already the source of transition '
                                                        f'{transition_name}')

            elif elem[0] == "destination":
                for transition in xml_transition_list:
                    if transition_name == transition.name or transition_name == transition.alias:
                        for state in xml_state_list:
                            if state_name == state.name or state_name == state.alias:
                                if not isinstance(state.type, datamodel.BaseType):
                                    if datamodel.EntryStateLabel in state.type.name.lower():
                                        Logger.set_error(__name__,
                                                         f"{state_name} is typed as ENTRY state, it cannot be "
                                                         f"put as destination's transition (not added)")
                                    elif datamodel.ExitStateLabel in state.type.name.lower():
                                        if transition.destination != state.id:
                                            new_dest_list.append([transition, state])
                                        else:
                                            Logger.set_info(__name__,
                                                            f'{state_name} already the destination of transition '
                                                            f'{transition_name}')
                                    else:
                                        Logger.set_error(__name__,
                                                         f"{state_name} is not typed as state, "
                                                         f"it cannot be put as source's transition (not added)")
                                else:
                                    if transition.destination != state.id:
                                        new_dest_list.append([transition, state])
                                    else:
                                        Logger.set_info(__name__,
                                                        f'{state_name} already the destination of transition '
                                                        f'{transition_name}')
            # Else do nothing

    src_dest_lists = [new_src_list, new_dest_list]
    update = add_src_dest(src_dest_lists, output_xml)

    return update


def add_src_dest(src_dest_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            src_dest_lists ([Transition, State(Source)],[Transition, State(Destination)]) :
            Transition object and Source/Destination
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    if any(src_dest_lists):
        new_src_list = src_dest_lists[0]
        new_dest_list = src_dest_lists[1]
        if new_src_list:
            output_xml.write_transition_source(new_src_list)
            # Warn the user once written and added within xml
            for source in new_src_list:
                source[0].set_source(source[1].id)
                Logger.set_info(__name__,
                                f"{source[1].name} source for {source[0].name}")

        if new_dest_list:
            output_xml.write_transition_destination(new_dest_list)
            # Warn the user once written and added within xml
            for destination in new_dest_list:
                destination[0].set_destination(destination[1].id)
                Logger.set_info(__name__,
                                f"{destination[1].name} destination for {destination[0].name}")
        return 1

    return 0


def check_add_exposes(exposes_str_list, **kwargs):
    """
    Check and get all "Fun_elem exposes Fun_inter" strings, if Fun_inter is not exposed yet
    (or parentality relationship) => add it to Fun_elem object and as exposedInterface within xml.
    Args:
        exposes_str_list ([strings]): list of strings
        xml_fun_elem_list ([Fun Elem]) : Functional Element list from xml parsing
        xml_fun_inter_list ([FunctionalInterface]) : FunctionalInterface list from xml parsing
        xml_data_list ([Data]) : Data list from xml parsing
        output_xml (XmlWriter3SE object) : XML's file object

    Returns:
        [0/1] : if update has been made
    """
    # TODO : add physical interface support (see write_element_exposed_interface())
    xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
    xml_fun_inter_list = kwargs[XML_DICT_KEY_3_FUN_INTF_LIST]
    output_xml = kwargs['output_xml']

    output = False
    cleaned_exposes_str_list = util.cut_tuple_list(exposes_str_list)
    # elem = [fun_elem_name, fun_intf_name]
    for elem in cleaned_exposes_str_list:
        fun_elem_name = elem[0].replace('"', "")
        fun_intf_name = elem[1].replace('"', "")

        fun_elem = orchestrator_object.retrieve_object_by_name(fun_elem_name,
                                                               **{XML_DICT_KEY_2_FUN_ELEM_LIST: xml_fun_elem_list})
        fun_inter = orchestrator_object.retrieve_object_by_name(fun_intf_name,
                                                                **{XML_DICT_KEY_3_FUN_INTF_LIST: xml_fun_inter_list})

        check_print_wrong_pair_object((fun_elem_name, fun_elem, 'Functional Element'),
                                      (fun_intf_name, fun_inter, 'Functional Interface'),
                                      'exposes')
        if fun_elem and fun_inter:
            if fun_inter.id not in fun_elem.exposed_interface_list:
                output = True
                fun_elem.add_exposed_interface(fun_inter.id)
                output_xml.write_element_exposed_interface([[fun_elem, fun_inter]])
                Logger.set_info(__name__,
                                f"{fun_elem.name} exposes {fun_inter.name}")

    if output:
        return 1

    return 0


def check_print_wrong_pair_object(object_a, object_b, relationship_type):
    """
    Prints specific user messages for wrong object(s) pair (Object_a, Object_b) relationship

    Args:
        object_a: (input_string, object_or_none, object_type_string)
        e.g. (exposes_str[0], fun_elem, 'Functional Element')
        object_b: (exposes_str[1], fun_inter, 'Functional Interface')
        relationship_type: e.g. 'exposes'

    """
    if object_a[1] == object_b[1] is None:
        Logger.set_error(__name__,
                         f"{object_a[0]} and {object_b[0]} do not exist, choose valid names/aliases for: "
                         f"'{object_a[2]}' {relationship_type} "
                         f"'{object_b[2]}'")
    elif object_a[1] is None or object_b[1] is None:
        if object_a[1] is None and object_b[1]:
            Logger.set_error(__name__,
                             f"{object_a[0]} does not exist, choose a valid name/alias for: "
                             f"'{object_a[2]}' {relationship_type} "
                             f"{object_b[1].name}")
        elif object_b[1] is None and object_a[1]:
            Logger.set_error(__name__,
                             f"{object_b[0]} does not exist, choose a valid name/alias for: "
                             f"{object_a[1].name} {relationship_type} "
                             f"'{object_b[2]}'")
