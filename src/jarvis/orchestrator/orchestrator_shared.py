""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from . import orchestrator_object
from jarvis.handler import handler_question
from jarvis import util
from tools import Logger


def check_add_child(parent_child_name_str_list, **kwargs):
    """
    Check if each string in parent_child_name_str_list are corresponding to an actual object,
    create new [parent, child] objects lists for object's type : State/Function/FunctionalElement.
    Send lists to add_child() to write them within xml and then returns update_list from it.

        Parameters:
            parent_child_name_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : 4 xml lists(see matched_composition() within command_parser.py)
            + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """

    parent_child_lists = [[] for _ in range(len(datamodel.TypeWithChildList))]

    cleaned_parent_child_list_str = util.cut_tuple_list(parent_child_name_str_list)
    # elem = [parent_object, child_object]
    for elem in cleaned_parent_child_list_str:
        parent_object = orchestrator_object.retrieve_object_by_name(elem[0], **kwargs)
        child_object = orchestrator_object.retrieve_object_by_name(elem[1], **kwargs)
        if parent_object is not None and child_object is not None:
            check_pair = None
            for idx, obj_type in enumerate(datamodel.TypeWithChildList):
                if isinstance(parent_object, obj_type) and isinstance(child_object, obj_type):
                    check_pair = idx
                    break
            if isinstance(check_pair, int):
                if child_object.parent is None:
                    parent_object.add_child(child_object)
                    child_object.set_parent(parent_object)
                    parent_child_lists[check_pair].append([parent_object, child_object])
                elif child_object.parent.id != parent_object.id:
                    Logger.set_warning(__name__, f"{elem[1]} has already a parent: {child_object.parent.name}")
            else:
                # Single display (not related to logging)
                print(f"Please choose a valid pair of element(Function/State/FunctionalElement"
                      f"/PhysicalElement) for {parent_object.name} and {child_object.name}")
        elif parent_object is None:
            Logger.set_error(__name__, f"{elem[0]} does not exist")
        else:
            Logger.set_error(__name__, f"{elem[1]} does not exist")

    update = add_child(parent_child_lists, **kwargs)

    return update


def add_child(parent_child_lists, **kwargs):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            parent_child_lists ([Parent, Child]) : [[Function],[State],[FunctionalElement],
            [PhysicalElement]]
            xml_fun_elem_list ([FunctionalElement]) : functional element list from xml parsing
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            update_list ([0/1]) : Add 1 to list if any update, otherwise 0 is added
    """
    update = 0
    if any(parent_child_lists):
        xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
        output_xml = kwargs['output_xml']
        for object_type in range(len(datamodel.TypeWithChildList)):
            if parent_child_lists[object_type]:
                output_xml.write_object_child(parent_child_lists[object_type])
                update = 1

                for obj in parent_child_lists[object_type]:
                    Logger.set_info(__name__,
                                    f"{obj[0].name} is composed of {obj[1].name}")
                    if object_type in (datamodel.TypeWithChildListFunctionIndex, datamodel.TypeWithChildListStateIndex):
                        # Considering function and state allocation to a functional element
                        for fun_elem in xml_fun_elem_list:
                            if obj[0].id in fun_elem.allocated_function_list:
                                allocate_all_children_in_element([fun_elem, obj[1]], **kwargs)

                        if object_type == datamodel.TypeWithChildListFunctionIndex:
                            # Considering function allocation
                            xml_consumer_function_list = kwargs[XML_DICT_KEY_12_FUN_CONS_LIST]
                            xml_producer_function_list = kwargs[XML_DICT_KEY_13_FUN_PROD_LIST]

                            for (flow, function) in xml_consumer_function_list:
                                if obj[1].id == function.id and [flow, obj[0]] not in xml_consumer_function_list:
                                    if [flow, obj[0]] not in xml_producer_function_list:
                                        output_xml.write_data_consumer([[flow, obj[0]]])
                                        xml_consumer_function_list.append([flow, obj[0]])

                                        Logger.set_info(__name__, f"{obj[0].name} produces {flow.name}")
                                    else:
                                        # Case of a parent child is producing the data
                                        output_xml.delete_data_relationship([flow, obj[0]], "producer")
                                        xml_producer_function_list.remove([flow, obj[0]])

                                        Logger.set_info(__name__, f"{obj[0].name} does not produce {flow.name} anymore")

                            for (flow, function) in xml_producer_function_list:
                                if obj[1].id == function.id and [flow, obj[0]] not in xml_producer_function_list:
                                    if [flow, obj[0]] not in xml_consumer_function_list:
                                        output_xml.write_data_producer([[flow, obj[0]]])
                                        xml_producer_function_list.append([flow, obj[0]])

                                        Logger.set_info(__name__, f"{obj[0].name} consumes {flow.name}")
                                    else:
                                        # Case of a parent child is consuming the data
                                        output_xml.delete_data_relationship([flow, obj[0]], "consumer")
                                        xml_consumer_function_list.remove([flow, obj[0]])

                                        Logger.set_info(__name__, f"{obj[0].name} does not consume {flow} anymore")

    return update


def check_add_allocated_item(item, xml_item_list, xml_view_list):
    """
    Checks if a view is already activated, if yes check if item isn't already
    allocated and returns corresponding [View, Object].
    Args:
        item (string): Object's name/alias from user's input
        xml_item_list ([Object]): List of xml's item (same type as item)
        xml_view_list ([View]) : View list from xml parsing

    Returns:
        [View, Object]
    """
    if not any(s.activated for s in xml_view_list):
        return None

    activated_view = None
    for view in xml_view_list:
        if view.activated:
            activated_view = view
            break
    if activated_view:
        for i in xml_item_list:
            if item == i.name:
                if i.id not in activated_view.allocated_item_list:
                    activated_view.add_allocated_item(i.id)
                    return [activated_view, i]
            # To avoid errors for i.alias when i is Data (no such attriute)
            try:
                if item == i.alias:
                    if i.id not in activated_view.allocated_item_list:
                        activated_view.add_allocated_item(i.id)
                        return [activated_view, i]
            except AttributeError:
                pass


def check_and_delete_object(delete_str_list, **kwargs):
    """
    Check if each string in delete_str_list are corresponding to an actual object, create new
    objects list for objects to delete.
    Send lists to delete_objects() to delete them within xml and then returns update from it.

        Parameters:
            delete_str_list ([str]) : List of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    to_be_deleted_obj_lists = [[] for _ in range(10)]
    # Check if the wanted to delete object exists and can be deleted
    for elem in delete_str_list:
        object_name = elem.replace('"', "")

        object_to_del = orchestrator_object.retrieve_object_by_name(object_name, **kwargs)
        if object_to_del is None:
            Logger.set_error(__name__,
                             f"{object_name} does not exist")
            continue

        check, list_idx = check_relationship_before_delete(object_to_del, **kwargs)
        if check:
            to_be_deleted_obj_lists[list_idx].append(object_to_del)
        else:
            Logger.set_error(__name__,
                             f"{object_to_del.name} can not be deleted")

    update = delete_objects(to_be_deleted_obj_lists, kwargs['output_xml'])

    return update


def check_relationship_before_delete(object_to_del, **kwargs):
    """Switch to trigger differents methods depend object's type"""
    _, idx = get_basetype_and_idx(object_to_del)
    switch_check = {
        0: check_data,
        1: check_function,
        2: check_fun_elem,
        3: check_fun_inter,
        4: check_phy_elem,
        5: check_phy_inter,
        6: check_state,
        7: check_transition,
        8: check_attribute,
        9: check_chain,
    }
    check_obj = switch_check.get(idx, "Object can not be deleted")
    check = check_obj(object_to_del, **kwargs)
    return check, idx


def check_object_not_in_prod_cons(object_to_check, consumer_list, producer_list):
    """Check if object/data_name not in producer or consumer lists"""
    check = False
    if not any(object_to_check in o for o in consumer_list + producer_list):
        check = True
    return check


def check_object_no_parent_and_child(object_to_check):
    """Check if an object has not parent and not child"""
    check = False
    if not object_to_check.child_list and object_to_check.parent is None:
        check = True

    return check


def check_object_not_allocated(object_to_check, allocated_to_object_list):
    """Check if object in allocated_list of allocated objects"""
    check = False
    if not allocated_to_object_list:
        check = True
        return check

    converted_list = list(allocated_to_object_list)
    if isinstance(object_to_check, datamodel.Function):
        if isinstance(converted_list[0], (datamodel.State, datamodel.FunctionalElement)):
            if not any(object_to_check.id in obj.allocated_function_list for obj
                       in converted_list):
                check = True
        if isinstance(converted_list[0], datamodel.View):
            if not any(object_to_check.id in obj.allocated_item_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.Data):
        if isinstance(converted_list[0], datamodel.View):
            if not any(object_to_check.id in obj.allocated_item_list for obj
                       in converted_list):
                check = True
        if isinstance(converted_list[0], datamodel.FunctionalInterface):
            if not any(object_to_check.id in obj.allocated_data_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.State):
        if isinstance(converted_list[0], datamodel.FunctionalElement):
            if not any(object_to_check.id in obj.allocated_state_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.FunctionalElement):
        if isinstance(converted_list[0], datamodel.PhysicalElement):
            if not any(object_to_check.id in obj.allocated_fun_elem_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.FunctionalInterface):
        if isinstance(converted_list[0], datamodel.FunctionalElement):
            if not any(object_to_check.id in obj.exposed_interface_list for obj
                       in converted_list):
                check = True
        if isinstance(converted_list[0], datamodel.PhysicalInterface):
            if not any(object_to_check.id in obj.allocated_fun_inter_list for obj
                       in converted_list):
                check = True
    if isinstance(object_to_check, datamodel.PhysicalInterface):
        if isinstance(converted_list[0], datamodel.PhysicalElement):
            if not any(object_to_check.id in obj.exposed_interface_list for obj
                       in converted_list):
                check = True
    return check


def check_object_no_attribute(object_to_check, attribute_list):
    """Check that object has not attribute set"""
    check = False
    described_item_list = [obj.described_item_list for obj in attribute_list]
    if not any(object_to_check.id in obj for obj in described_item_list):
        check = True
    return check


def check_function(object_to_del, **kwargs):
    """Checks for Function's object"""
    check = False
    check_list = [False] * 6
    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_6_STATE_LIST])
    check_list[2] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
    if not check_list[1] or not check_list[2]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    check_list[3] = check_object_not_in_prod_cons(object_to_del,
                                                  kwargs[XML_DICT_KEY_12_FUN_CONS_LIST],
                                                  kwargs[XML_DICT_KEY_13_FUN_PROD_LIST])
    if not check_list[3]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has production/consumption relationship(s)")

    check_list[4] = check_object_no_attribute(object_to_del, kwargs[XML_DICT_KEY_9_ATTRIBUTE_LIST])
    if not check_list[4]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has attribute(s) set")

    check_list[5] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_10_VIEW_LIST])
    if not check_list[5]:
        Logger.set_info(__name__, f"{object_to_del.name} has chain relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_1_FUNCTION_LIST].remove(object_to_del)
    return check


def check_data(object_to_del, **kwargs):
    """Checks for Data's object"""
    check = False
    check_list = [False] * 3
    check_list[0] = check_object_not_in_prod_cons(object_to_del.name,
                                                  kwargs[XML_DICT_KEY_12_FUN_CONS_LIST],
                                                  kwargs[XML_DICT_KEY_13_FUN_PROD_LIST])
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has production/consumption relationship(s)")

    check_list[1] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_10_VIEW_LIST])
    if not check_list[1]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has chain relationship(s)")

    check_list[2] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_3_FUN_INTF_LIST])
    if not check_list[2]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_0_DATA_LIST].remove(object_to_del)
    return check


def check_state(object_to_del, **kwargs):
    """Checks for State's object"""
    check = False
    check_list = [False] * 4

    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = not object_to_del.allocated_function_list
    check_list[2] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
    if not check_list[1] or not check_list[2]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    check_list[3] = not any(object_to_del.id in (trans.source, trans.destination)
                            for trans in kwargs[XML_DICT_KEY_7_TRANSITION_LIST])
    if not check_list[3]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has transition relationship(s)")
    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_6_STATE_LIST].remove(object_to_del)
    return check


def check_transition(object_to_del, **kwargs):
    """Checks for State's object"""
    check = False
    check_list = [False] * 1

    check_list[0] = object_to_del.source is None and object_to_del.destination is None
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has source/destination relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_7_TRANSITION_LIST].remove(object_to_del)
    return check


def check_fun_elem(object_to_del, **kwargs):
    """Checks for Functional Element's object"""
    check = False
    check_list = [False] * 4

    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = (not object_to_del.allocated_function_list and
                     not object_to_del.allocated_state_list)
    check_list[2] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST])
    if not check_list[1] or not check_list[2]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    check_list[3] = not object_to_del.exposed_interface_list
    if not check_list[3]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has interface relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST].remove(object_to_del)

    return check


def check_chain(object_to_del, **kwargs):
    """Checks for View's object"""
    check = False
    check_list = [False] * 1

    check_list[0] = not object_to_del.allocated_item_list
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_10_VIEW_LIST].remove(object_to_del)

    return check


def check_attribute(object_to_del, **kwargs):
    """Checks for Attribute's object"""
    check = False
    check_list = [False] * 1

    check_list[0] = not object_to_del.described_item_list
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has attribute relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_9_ATTRIBUTE_LIST].remove(object_to_del)

    return check


def check_fun_inter(object_to_del, **kwargs):
    """Checks for Functional Interface's object"""
    check = False
    check_list = [False] * 3

    check_list[0] = not object_to_del.allocated_data_list
    check_list[1] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
    check_list[2] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_5_PHY_INTF_LIST])
    if not check_list[0] or not check_list[1] or not check_list[2]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_3_FUN_INTF_LIST].remove(object_to_del)

    return check


def check_phy_elem(object_to_del, **kwargs):
    """Checks for Physical Element's object"""
    check = False
    check_list = [False] * 3

    check_list[0] = check_object_no_parent_and_child(object_to_del)
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has composition relationship(s)")

    check_list[1] = not object_to_del.allocated_fun_elem_list
    if not check_list[1]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    check_list[2] = not object_to_del.exposed_interface_list
    if not check_list[2]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has interface relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST].remove(object_to_del)

    return check


def check_phy_inter(object_to_del, **kwargs):
    """Checks for Physical Interface's object"""
    check = False
    check_list = [False] * 2

    check_list[0] = not object_to_del.allocated_fun_inter_list
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has allocation relationship(s)")

    check_list[1] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST])
    if not check_list[1]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has interface relationship(s)")

    if all(check_list):
        check = True
        kwargs[XML_DICT_KEY_5_PHY_INTF_LIST].remove(object_to_del)

    return check


def delete_objects(object_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            object_lists : see order in get_basetype_and_idx()
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_lists):
        for i in range(10):
            if object_lists[i]:
                output_xml.delete_object(object_lists[i])
                for object_type in object_lists[i]:
                    Logger.set_info(__name__,
                                    f"{object_type.name} deleted")
        return 1
    return 0


def check_set_object_type(type_str_list, **kwargs):
    """
    Check if each string in type_str_list are corresponding to an actual object's name/alias, create
    [objects] ordered lists(as BaseType(Enum)) for:
    [[Data], [Function],[FunctionalElement], [FuncitonalInterface],[PhysicalElement],
    [PhysicalInterface], [State],[Transition],[Attribute],[View]]
    Send lists to set_object_type() to write them within xml and then returns update from it.

        Parameters:
            type_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    object_type_lists = [[] for _ in range(10)]
    # Check if the wanted object exists and the type can be set
    # elem = [object_name, type_name]
    for elem in type_str_list:
        object_name = elem[0].replace('"', "")
        type_name = elem[1].replace('"', "")

        object_to_set = orchestrator_object.retrieve_object_by_name(object_name, **kwargs)
        if object_to_set is None:
            Logger.set_error(__name__,
                             f"{object_name} does not exist")
            continue
        if object_to_set.type == type_name:
            continue
        check, base_type_idx = check_new_type(object_to_set, type_name, kwargs[XML_DICT_KEY_11_TYPE_LIST])
        if check:
            object_type_lists[base_type_idx].append(object_to_set)

    update = set_object_type(object_type_lists, kwargs['output_xml'])

    return update


def check_new_type(object_to_set, type_name, xml_type_list):
    """Check if type in specity object's type list and if changed"""
    check = False
    base_type_idx = None
    obj_base_type = get_basetype_and_idx(object_to_set)
    # print(specific_obj_type_list, list_idx)
    if obj_base_type and type_name != object_to_set.type:
        if type_name.capitalize().replace("_", " ") in [str(i) for i in datamodel.BaseType]:
            base_type_idx = obj_base_type.value
            check = True
            object_to_set.set_type(obj_base_type)
        elif any(t == type_name for t in orchestrator_object.check_object_name_in_list(xml_type_list)):
            obj_type = orchestrator_object.retrieve_object_by_name(type_name,
                                                                   **{XML_DICT_KEY_11_TYPE_LIST: xml_type_list})
            check = check_type_recursively(obj_type)
            if not check:
                Logger.set_info(__name__,
                                f"{obj_type.name} is not base type: "
                                f"{str(obj_base_type)}")
            else:
                base_type_idx = obj_base_type.value
                object_to_set.set_type(obj_type)
        else:
            Logger.set_error(__name__,
                             f"The type {type_name} does not exist, available types are "
                             f": {', '.join([str(i) for i in datamodel.BaseType])}.")

    return check, base_type_idx


def check_type_recursively(obj_type):
    """Checks type.base recursively if it within specific_obj_type_list"""
    check = False
    if isinstance(obj_type.base, (datamodel.BaseType, str)):
        check = True
        return check
    elif isinstance(obj_type.base, datamodel.Type):
        return check_type_recursively(obj_type.base)
    return check


def get_basetype_and_idx(object_to_set):
    """Return BaseType according to object's type"""
    # Tuple order is same as datamodel.BaseType(Enum)
    class_obj_tuple = (datamodel.Data, datamodel.Function, datamodel.FunctionalElement,
                       datamodel.FunctionalInterface, datamodel.PhysicalElement, datamodel.PhysicalInterface,
                       datamodel.State, datamodel.Transition, datamodel.Attribute, datamodel.View)

    for idx, i in enumerate(class_obj_tuple):
        if isinstance(object_to_set, i):
            return datamodel.BaseType(idx)

    return None


def set_object_type(object_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update list if some
    updates has been made

        Parameters:
            object_lists : see order in get_basetype_and_idx()
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_lists):
        for i in range(10):
            if object_lists[i]:
                output_xml.write_object_type(object_lists[i])
                for object_type in object_lists[i]:
                    if isinstance(object_type.type, datamodel.BaseType):
                        type_name = str(object_type.type)
                    else:
                        type_name = object_type.type.name
                    Logger.set_info(__name__,
                                    f"The type of {object_type.name} is {type_name}")
        return 1
    return 0


def check_set_object_alias(alias_str_list, **kwargs):
    """
    Check if each string in alias_str_list are corresponding to an actual object's name/alias,
    create [objects] ordered lists for:
    [[Function],[State],[Transition],[FunctionalElement],[Attribute],
    [FuncitonalInterface],[PhysicalElement],[PhysicalInterface]]
    Send lists to set_object_type() to write them within xml and then returns update from it.

        Parameters:
            alias_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    object_lists = [[] for _ in range(9)]
    # Check if the wanted to object exists and the alias can be set
    # elem = [object_name, alias_str]
    for elem in alias_str_list:
        object_name = elem[0].replace('"', "")
        alias_str = elem[1].replace('"', "")

        object_to_set = orchestrator_object.retrieve_object_by_name(object_name, **kwargs)
        if object_to_set is None:
            Logger.set_error(__name__,
                             f"{object_name} does not exist")
            continue

        idx = check_new_alias(object_to_set, alias_str)
        if isinstance(idx, int):
            object_lists[idx].append(object_to_set)

    update = set_object_alias(object_lists, kwargs['output_xml'])

    return update


def check_new_alias(object_to_set, alias_str):
    """Check that alias is new and object has en alias attribute, then returns corresponding
    object's type index"""
    check = None
    try:
        if object_to_set.alias == alias_str:
            return check
    except AttributeError:
        print(f"{object_to_set.name} object does not have alias attribute")
        return check
    if isinstance(object_to_set, datamodel.Type):
        object_to_set.set_alias(alias_str)
        return 0

    base_type = orchestrator_object.retrieve_base_type_recursively(object_to_set.type)
    if isinstance(base_type, datamodel.BaseType):
        # Data() and View() do not have aliases attributes
        if base_type.value not in (0, 9):
            object_to_set.set_alias(alias_str)
            return base_type.value

    return check


def set_object_alias(object_lists, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update if some
    updates has been made.
        Parameters:
            object_lists ([Object]) : object with new alias
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_lists):
        for i in range(9):
            if object_lists[i]:
                output_xml.write_object_alias(object_lists[i])
                for object_alias in object_lists[i]:
                    Logger.set_info(__name__,
                                    f"The alias for {object_alias.name} is {object_alias.alias}")

        return 1

    return 0


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
    new_allocation = {
        0: [],  # [FunctionalElement, Function/State]
        1: [],  # [State, Function]
        2: [],  # [FunctionalInterface, Data]
        3: [],  # [PhysicalElement, FunctionalElement]
        4: [],  # [PhysicalInterface, FunctionalInterface]
        # 5: [],  [View, Object] in other modules or [Fun_elem_Parent, Function/State] in
        # check_parent_allocation() it's just a key with no recursivety
    }
    cleaned_allocation_str_list = util.cut_tuple_list(allocation_str_list)
    for elem in cleaned_allocation_str_list:
        alloc_obj = orchestrator_object.retrieve_object_by_name(
            elem[0],
            **{XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
               XML_DICT_KEY_6_STATE_LIST: kwargs[XML_DICT_KEY_6_STATE_LIST],
               XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
               XML_DICT_KEY_4_PHY_ELEM_LIST: kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST],
               XML_DICT_KEY_5_PHY_INTF_LIST: kwargs[XML_DICT_KEY_5_PHY_INTF_LIST],
               })
        obj_to_alloc = orchestrator_object.retrieve_object_by_name(
            elem[1],
            **{XML_DICT_KEY_1_FUNCTION_LIST: kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
               XML_DICT_KEY_6_STATE_LIST: kwargs[XML_DICT_KEY_6_STATE_LIST],
               XML_DICT_KEY_0_DATA_LIST: kwargs[XML_DICT_KEY_0_DATA_LIST],
               XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
               XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
               })
        check_obj = check_allocation_objects_types(alloc_obj, obj_to_alloc, elem)
        if not check_obj:
            continue
        check_rule, alloc = check_allocation_rules(alloc_obj, obj_to_alloc, **kwargs)
        if check_rule and alloc:
            new_allocation[alloc[0]].append(alloc[1])

    update = add_allocation(new_allocation, **kwargs)

    return update


def check_allocation_objects_types(alloc_obj, obj_to_alloc, elem):
    """Check that alloc_obj within is FunctionalElement or FunctionalInterface or State or
    PhysicalElement or PhysicalInterface AND obj_to_alloc is Function/State or Data or
    FunctionalElement or FunctionalInterface"""
    check = True
    if alloc_obj is None and obj_to_alloc is None:
        print_wrong_obj_allocation(elem)
        check = False
    elif alloc_obj is None or obj_to_alloc is None:
        if alloc_obj is None:
            print_wrong_obj_allocation(elem[0])
            check = False
        elif obj_to_alloc is None:
            print_wrong_obj_allocation(elem[1])
            check = False

    return check


def print_wrong_obj_allocation(obj_str):
    """Print relative message to wrong pair allocations"""
    if isinstance(obj_str, tuple):
        name_str = f"Objects {obj_str[0]} and {obj_str[1]}"
    else:
        name_str = f"Object {obj_str}"

    Logger.set_error(__name__,
                     name_str + " not found or can not be allocated, "
                                "available allocations are: \n"
                                "(Functional Element allocates State/Function) OR \n"
                                "(State allocates Function) OR \n"
                                "(Functional Interface allocates Data) OR \n"
                                "(Physical Element allocates Functional Element) OR \n"
                                "(Physical Interface allocates Functional Interface)")


def check_allocation_rules(alloc_obj, obj_to_alloc, **kwargs):
    """Check "good" combinations, trigger specific check and then return check and new tuple
    allocation"""
    check = False
    new_alloc = None
    if isinstance(alloc_obj, datamodel.FunctionalElement):
        if isinstance(obj_to_alloc, (datamodel.Function, datamodel.State)):
            check = True
            pair = check_fun_elem_allocation(alloc_obj, obj_to_alloc, kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST], **kwargs)
            if pair:
                new_alloc = [0, pair]
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.State):
        if isinstance(obj_to_alloc, datamodel.Function):
            check = True
            pair = check_state_allocation(alloc_obj, obj_to_alloc, kwargs[XML_DICT_KEY_6_STATE_LIST], **kwargs)
            if pair:
                new_alloc = [1, pair]
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.FunctionalInterface):
        if isinstance(obj_to_alloc, datamodel.Data):
            check = True
            pair = check_fun_inter_allocation(alloc_obj, obj_to_alloc, **kwargs)
            if pair:
                new_alloc = [2, pair]
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.PhysicalElement):
        if isinstance(obj_to_alloc, datamodel.FunctionalElement):
            check = True
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)
    elif isinstance(alloc_obj, datamodel.PhysicalInterface):
        if isinstance(obj_to_alloc, datamodel.FunctionalInterface):
            check = True
        else:
            print_wrong_obj_allocation(obj_to_alloc.name)

    return check, new_alloc


def check_fun_elem_allocation(fun_elem, obj_to_alloc, fun_elem_list, **kwargs):
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


def check_state_allocation(state, function, state_list, **kwargs):
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


def check_fun_inter_allocation(fun_inter, data, **kwargs):
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
            kwargs[XML_DICT_KEY_12_FUN_CONS_LIST],
            kwargs[XML_DICT_KEY_13_FUN_PROD_LIST])
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

                    if k == 1:
                        # Allocation of [State, Function]
                        # Need to remove previous allocation if any
                        xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]
                        xml_state_list = kwargs[XML_DICT_KEY_6_STATE_LIST]
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

                    if k in (0, 1):
                        allocate_all_children_in_element(elem, **kwargs)
        return 1
    return 0


def check_parent_allocation(elem, **kwargs):
    """Check if parent's Function/Sate are allocated to parent's Fucntional Element:
    if not print message to user asking if he wants to, if yes write it in xml then continue
    with parents"""
    if elem[0].parent is not None and elem[1].parent is not None:
        fun_elem_parent = elem[0].parent
        object_parent = elem[1].parent
        check = False
        if isinstance(elem[1], datamodel.State):
            if object_parent.id in fun_elem_parent.allocated_state_list:
                check = True
        elif isinstance(elem[1], datamodel.Function):
            if object_parent.id in fun_elem_parent.allocated_function_list:
                check = True
        if not check:
            answer, _ = handler_question.question_to_user(f"Do you also want to allocate parents "
                                                          f"(i.e. {object_parent.name} "
                                                          f"to {fun_elem_parent.name}) ? (Y/N)")
            if answer.lower() == "y":
                if isinstance(elem[1], datamodel.State):
                    fun_elem_parent.add_allocated_state(object_parent.id)
                else:
                    fun_elem_parent.add_allocated_function(object_parent.id)

                add_allocation({5: [[fun_elem_parent, object_parent]]}, **kwargs)
                check_parent_allocation([fun_elem_parent, object_parent], **kwargs)
            else:
                Logger.set_error(__name__,
                                 f"{object_parent.name} is not allocated despite at least one "
                                 f"of its child is")


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
                add_allocation({0: allocated_child_list}, **kwargs)
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
            add_allocation({5: [elem]}, **kwargs)
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
            add_allocation({5: [elem]}, **kwargs)


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


def check_add_inheritance(inherit_str_list, **kwargs):
    """
    Check if each string in allocation_str_list are corresponding to an actual object's name/alias,
    set_derive, create lists of objets.
    Send lists to add_derived() to write them within xml and then returns update from it.

        Parameters:
            inherit_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    new_list = []
    for elem in inherit_str_list:
        object_inheriting_name = elem[0].replace('"', "")
        object_to_inherit_name = elem[1].replace('"', "")

        object_inheriting = orchestrator_object.retrieve_object_by_name(
            object_inheriting_name,
            **{XML_DICT_KEY_1_FUNCTION_LIST: kwargs[
                XML_DICT_KEY_1_FUNCTION_LIST],
               XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[
                   XML_DICT_KEY_2_FUN_ELEM_LIST],
               XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[
                   XML_DICT_KEY_3_FUN_INTF_LIST],
               XML_DICT_KEY_4_PHY_ELEM_LIST: kwargs[
                   XML_DICT_KEY_4_PHY_ELEM_LIST],
               XML_DICT_KEY_5_PHY_INTF_LIST: kwargs[
                   XML_DICT_KEY_5_PHY_INTF_LIST],
               })

        object_to_inherit = orchestrator_object.retrieve_object_by_name(
            object_to_inherit_name,
            **{XML_DICT_KEY_1_FUNCTION_LIST: kwargs[
                XML_DICT_KEY_1_FUNCTION_LIST],
               XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[
                   XML_DICT_KEY_2_FUN_ELEM_LIST],
               XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[
                   XML_DICT_KEY_3_FUN_INTF_LIST],
               XML_DICT_KEY_4_PHY_ELEM_LIST: kwargs[
                   XML_DICT_KEY_4_PHY_ELEM_LIST],
               XML_DICT_KEY_5_PHY_INTF_LIST: kwargs[
                   XML_DICT_KEY_5_PHY_INTF_LIST],
               })
        if not object_inheriting or not object_to_inherit:
            if not object_inheriting and not object_to_inherit:
                print_wrong_object_inheritance(object_inheriting_name, object_to_inherit_name)
            elif not object_inheriting:
                print_wrong_object_inheritance(object_inheriting_name)
            else:
                print_wrong_object_inheritance(object_to_inherit_name)
            continue
        if object_inheriting == object_to_inherit:
            Logger.set_warning(__name__,
                               f"Same object {object_inheriting.name}")
            continue
        if object_inheriting.derived == object_to_inherit:
            continue

        check_obj = check_inheritance(object_inheriting, object_to_inherit)
        if not check_obj:
            continue
        new_list.append(object_inheriting)

    if not new_list:
        return 0

    add_derived(new_list, kwargs['output_xml'])
    return 1


def print_wrong_object_inheritance(*obj):
    """Prints wrong object(s) message for inheritance from input string"""
    if len(obj) == 2:
        user_message = f"{obj[0]} and {obj[1]}"
    else:
        user_message = f"{obj[0]}"

    Logger.set_error(__name__,
                     f"{user_message} not found, available objects for inheritance are:\n"
                     "- Function\n"
                     "- Functional element\n"
                     "- Functional interface\n"
                     "- Physical element\n"
                     "- Physical element\n")


def check_inheritance(elem_0, elem_1):
    """Returns check if pair are compatible and object list have been updated"""
    inheritance_type_list = [datamodel.Function, datamodel.FunctionalElement,
                             datamodel.FunctionalInterface, datamodel.PhysicalElement,
                             datamodel.PhysicalInterface]

    type_found = None
    for idx, inheritance_type in enumerate(inheritance_type_list):
        if isinstance(elem_0, inheritance_type) and isinstance(elem_1, inheritance_type):
            type_found = idx
            break

    if type_found is None:
        Logger.set_error(__name__,
                         f"{elem_0.__class__.__name__} and {elem_1.__class__.__name__} "
                         f"are not of the same type")
        return False

    elem_0.set_derived(elem_1)
    return True


def add_derived(object_list, output_xml):
    """
    Check if input lists are not empty, write in xml for each list and return update if some
    updates has been made.
        Parameters:
            object_list ([Object]) : object with new derived
            output_xml (XmlWriter3SE object) : XML's file object

        Returns:
            1 if update, else 0
    """
    if any(object_list):
        output_xml.write_object_derived(object_list)
        for obj in object_list:
            Logger.set_info(__name__,
                            f"{obj.name} inherited from {obj.derived.name}")
        return 1
    return 0
