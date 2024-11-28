""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_INFORMATION_LIST, XML_DICT_KEY_11_ATTRIBUTE_LIST, \
    XML_DICT_KEY_12_VIEW_LIST, XML_DICT_KEY_13_TYPE_LIST, XML_DICT_KEY_14_FUN_CONS_LIST, \
    XML_DICT_KEY_15_FUN_PROD_LIST, XML_DICT_KEY_16_ACT_CONS_LIST, XML_DICT_KEY_17_ACT_PROD_LIST
from . import orchestrator_object
from . import orchestrator_object_allocation
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
                                orchestrator_object_allocation.allocate_all_children_in_element(
                                    [fun_elem, obj[1]], **kwargs
                                )

                        if object_type == datamodel.TypeWithChildListFunctionIndex:
                            # Considering function allocation
                            xml_consumer_function_list = kwargs[XML_DICT_KEY_14_FUN_CONS_LIST]
                            xml_producer_function_list = kwargs[XML_DICT_KEY_15_FUN_PROD_LIST]

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
                                                  kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                                                  kwargs[XML_DICT_KEY_15_FUN_PROD_LIST])
    if not check_list[3]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has production/consumption relationship(s)")

    check_list[4] = check_object_no_attribute(object_to_del, kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST])
    if not check_list[4]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has attribute(s) set")

    check_list[5] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_12_VIEW_LIST])
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
                                                  kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                                                  kwargs[XML_DICT_KEY_15_FUN_PROD_LIST])
    if not check_list[0]:
        Logger.set_info(__name__,
                        f"{object_to_del.name} has production/consumption relationship(s)")

    check_list[1] = check_object_not_allocated(object_to_del, kwargs[XML_DICT_KEY_12_VIEW_LIST])
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
        kwargs[XML_DICT_KEY_12_VIEW_LIST].remove(object_to_del)

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
        kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST].remove(object_to_del)

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
        check, base_type_idx = check_new_type(object_to_set, type_name, kwargs[XML_DICT_KEY_13_TYPE_LIST])
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
                                                                   **{XML_DICT_KEY_13_TYPE_LIST: xml_type_list})
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
