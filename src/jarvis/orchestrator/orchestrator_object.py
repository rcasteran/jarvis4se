""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries
import re

# Modules
import datamodel
from xml_adapter import XmlDictKeyListForObjects
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
from jarvis import util
from . import orchestrator_viewpoint_requirement, orchestrator_viewpoint_goal
from tools import Logger


class ObjectInstanceList(list):
    nb_object_instance_base_type = 12

    def __init__(self, p_base_type_idx):
        super().__init__()
        self.base_type_idx = p_base_type_idx

    def write_instance(self, **kwargs):
        # Object write routine list must be in the same order as object_instance_list in ObjectInstance
        # Object write routine has a size of nb_object_instance_base_type
        object_write_routine_list = {
            0: kwargs['output_xml'].write_data,
            1: kwargs['output_xml'].write_function,
            2: kwargs['output_xml'].write_functional_element,
            3: kwargs['output_xml'].write_functional_interface,
            4: kwargs['output_xml'].write_physical_element,
            5: kwargs['output_xml'].write_physical_interface,
            6: kwargs['output_xml'].write_state,
            7: kwargs['output_xml'].write_transition,
            8: kwargs['output_xml'].write_requirement,
            9: kwargs['output_xml'].write_goal,
            10: kwargs['output_xml'].write_activity,
            11: kwargs['output_xml'].write_information,
        }
        call = object_write_routine_list.get(self.base_type_idx)
        call(self)


class ObjectInstance:
    object_instance_list = {
        0: datamodel.Data,
        1: datamodel.Function,
        2: datamodel.FunctionalElement,
        3: datamodel.FunctionalInterface,
        4: datamodel.PhysicalElement,
        5: datamodel.PhysicalInterface,
        6: datamodel.State,
        7: datamodel.Transition,
        8: datamodel.Requirement,
        9: datamodel.Goal,
        10: datamodel.Activity,
        11: datamodel.Information
    }

    def __init__(self, obj_str, base_type, specific_obj_type=None, **kwargs):
        self.specific_type = specific_obj_type
        self.base_type = base_type
        self.base_type_idx = datamodel.BaseType.get_enum(str(self.base_type)).value

        call = self.object_instance_list.get(self.base_type_idx)
        if self.specific_type is None:
            self.object_instance = call(p_name=obj_str, p_id=util.get_unique_id())
        else:
            self.object_instance = call(p_name=obj_str, p_id=util.get_unique_id(), p_type=self.specific_type)

        # Information, Data and View do not have aliases
        if not isinstance(self.object_instance, (datamodel.Information, datamodel.Data, datamodel.View)):
            alias_str = re.search(r"(.*)\s[-]\s", obj_str, re.MULTILINE)
            if alias_str:
                self.object_instance.set_alias(alias_str.group(1))

        # Add object to object dictionary
        # Object dictionary list must be in the same order as object_instance_list
        object_dictionary_list = {
            0: kwargs[XML_DICT_KEY_0_DATA_LIST].add,
            1: kwargs[XML_DICT_KEY_1_FUNCTION_LIST].add,
            2: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST].add,
            3: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST].add,
            4: kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST].add,
            5: kwargs[XML_DICT_KEY_5_PHY_INTF_LIST].add,
            6: kwargs[XML_DICT_KEY_6_STATE_LIST].add,
            7: kwargs[XML_DICT_KEY_7_TRANSITION_LIST].add,
            8: kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST].add,
            9: kwargs[XML_DICT_KEY_9_GOAL_LIST].add,
            10: kwargs[XML_DICT_KEY_10_ACTIVITY_LIST].add,
            11: kwargs[XML_DICT_KEY_11_INFORMATION_LIST].add
        }
        call = object_dictionary_list.get(self.base_type_idx)
        call(self.object_instance)

    def get_instance(self):
        return self.object_instance


def check_add_specific_obj_by_type(obj_type_str_list, **kwargs):
    """
    Check if each string in obj_type_str_list are corresponding to an actual object's name/alias,
    set_derive, create object_instance_per_base_type_list with list per obj. Send lists to add_obj_to_xml()
    write them within xml and then returns update from it.

        Parameters:
            obj_type_str_list ([str]) : Lists of string from jarvis cell
            kwargs (dict) : whole xml lists + xml's file object

        Returns:
            update ([0/1]) : 1 if update, else 0
    """
    object_instance_per_base_type_list = [ObjectInstanceList(idx) for idx in
                                          range(ObjectInstanceList.nb_object_instance_base_type)]

    # elem = [object_name, object_type]
    for elem in obj_type_str_list:
        object_name = elem[0].replace('"', "")
        object_type = elem[1].replace('"', "")

        if "?" not in elem[1]:
            specific_type, base_type = retrieve_type(object_type, **kwargs)
            existing_object = retrieve_object_by_name(object_name, **kwargs)

            if existing_object:
                if isinstance(existing_object.type, datamodel.BaseType):
                    Logger.set_info(__name__, f"{existing_object.type} with the name {object_name} already exists")
                else:
                    Logger.set_info(__name__, f"{existing_object.type.name} with the name {object_name} already exists")
            elif base_type is not None:
                new_object = ObjectInstance(object_name, base_type, specific_type, **kwargs)
                if isinstance(new_object.get_instance().type, datamodel.BaseType):
                    Logger.set_info(__name__,
                                    f"{new_object.get_instance().name} is a {str(new_object.get_instance().type)}")
                else:
                    Logger.set_info(__name__,
                                    f"{new_object.get_instance().name} is a {new_object.get_instance().type.name}")

                object_instance_per_base_type_list[new_object.base_type_idx].append(new_object.get_instance())
            # Else do nothing

    check = 0
    if any(object_instance_per_base_type_list):
        for object_base_type, object_instance_list in enumerate(object_instance_per_base_type_list):
            if object_instance_list:
                object_instance_list.write_instance(**kwargs)

                # Check if any requirement related to the objects
                check_object_instance_list_requirement(object_instance_list, **kwargs)

                # Check if any goal related to the objects
                check_object_instance_list_goal(object_instance_list, **kwargs)

                check = 1

    return check


def retrieve_type(p_type_str, p_is_silent=False, **kwargs):
    specific_type = None
    base_type = None

    if p_type_str.capitalize() in [str(i) for i in datamodel.BaseType]:
        base_type = next((i for i in [str(i) for i in datamodel.BaseType]
                          if i == p_type_str.capitalize()))
    else:
        specific_type = retrieve_object_by_name(p_type_str,
                                                **{XML_DICT_KEY_14_TYPE_LIST: kwargs[XML_DICT_KEY_14_TYPE_LIST]})
        if specific_type is None:
            if not p_is_silent:
                Logger.set_error(__name__,
                                 f"No valid type found for {p_type_str}")
            # Else do nothing
        else:
            base_type = retrieve_base_type_recursively(specific_type)

            if base_type is None and not p_is_silent:
                Logger.set_error(__name__, f"No valid base type found for {p_type_str}")
            # Else do nothing

    return specific_type, base_type


def retrieve_base_type_recursively(obj_type):
    """Checks type: if it's a BaseType or its base else recursively return """
    if isinstance(obj_type, datamodel.BaseType):
        base_type = obj_type
    elif obj_type.base in [str(i) for i in datamodel.BaseType]:
        base_type = obj_type.base
    else:
        base_type = retrieve_base_type_recursively(obj_type.base)

    return base_type


def retrieve_implicit_object_relationship(p_object_src, p_object_dest, p_context, p_object_in_context_list,
                                          p_transition_keyword, **kwargs):
    implicit_object = None

    if hasattr(p_object_src, 'type') and hasattr(p_object_dest, 'type'):
        if isinstance(p_object_src.type, datamodel.BaseType):
            object_src_type = p_object_src.type
        else:
            _, object_src_type = retrieve_type(p_object_src.type.name, True, **kwargs)

        if isinstance(p_object_dest.type, datamodel.BaseType):
            object_dest_type = p_object_dest.type
        else:
            _, object_dest_type = retrieve_type(p_object_dest.type.name, True, **kwargs)

        # check_object_relationship need to be executed before to ensure relationship between object_src and object_dest
        if object_src_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
            if object_dest_type == datamodel.BaseType.STATE:
                if p_transition_keyword in p_context:
                    for object_in_context in p_object_in_context_list:
                        if object_in_context:
                            if isinstance(object_in_context.type, datamodel.BaseType):
                                object_in_context_type = object_in_context.type
                            else:
                                _, object_in_context_type = retrieve_type(object_in_context.type.name, True, **kwargs)

                            if object_in_context.type == datamodel.BaseType.STATE and \
                                    object_in_context_type != p_object_dest:
                                implicit_object = retrieve_object_transition_between_states(p_object_dest,
                                                                                            object_in_context,
                                                                                            **kwargs)
                            # Else do nothing
                # Else do nothing
            # Else do nothing
        # Else do nothing
    # Else do nothing : no implicit relationship with a type

    return implicit_object


def retrieve_object_transition_between_states(p_object_src, p_object_dest, **kwargs):
    transition_object = None

    for transition in kwargs[XML_DICT_KEY_7_TRANSITION_LIST]:
        if p_object_src.id == transition.source and p_object_dest.id == transition.destination:
            transition_object = transition
            break
        # Else do nothing

    return transition_object


def retrieve_object_children_recursively(p_object, p_object_list=None, p_parent_child_dict=None, p_level_count=None,
                                         p_requested_level=None):
    if p_object_list is None:
        p_object_list = set()
    # Else do nothing

    if p_parent_child_dict is None:
        p_parent_child_dict = {}
    # Else do nothing

    if not p_level_count:
        p_level_count = 0
    # Else do nothing

    p_object_list.add(p_object)

    if p_object.child_list:
        p_level_count += 1
        if p_requested_level:
            if (p_level_count - 1) == p_requested_level:
                p_object.child_list.clear()
            else:
                for child in p_object.child_list:
                    p_parent_child_dict[child.id] = p_object.id
                    retrieve_object_children_recursively(child, p_object_list, p_parent_child_dict, p_level_count,
                                                         p_requested_level)
        else:
            for child in p_object.child_list:
                p_parent_child_dict[child.id] = p_object.id
                retrieve_object_children_recursively(child, p_object_list, p_parent_child_dict, p_level_count,
                                                     p_requested_level)
    # Else do nothing

    return p_object_list, p_parent_child_dict


def retrieve_object_parents_recursively(p_object, p_object_list=None):
    if p_object_list is None:
        p_object_list = set()
    # Else do nothing

    if p_object.parent:
        p_object_list.add(p_object.parent)
        retrieve_object_parents_recursively(p_object.parent, p_object_list)
    # Else do nothing

    return p_object_list


def retrieve_object_by_name(p_obj_name_str, **kwargs):
    """
    Returns the desired object from object's string
    Args:
        p_obj_name_str ([object_string]): list of object's name from cell
        **kwargs: xml lists

    Returns:
        wanted_object : Function/State/Data/Fun_Elem/Transition/Fun_Inter
    """
    wanted_object = None
    whole_objects_name_list = check_object_name_in_dict(**kwargs)

    if any(p_obj_name_str in s for s in whole_objects_name_list):
        result = [False] * len(XmlDictKeyListForObjects)
        for i in range(len(XmlDictKeyListForObjects)):
            result[i] = any(a == p_obj_name_str for a in whole_objects_name_list[i])

        wanted_object = match_object(p_obj_name_str, result, p_xml_str_lists=XmlDictKeyListForObjects, **kwargs)
    # Else do nothing

    return wanted_object


def match_object(object_str, result, p_xml_str_lists=None, **kwargs):
    """Returns wanted_object from object_str and result matched from name lists"""
    # Because match_object() called within match_allocated() TBC/TBT if match_allocated()
    # still needed
    if not p_xml_str_lists:
        p_xml_str_lists = XmlDictKeyListForObjects
    for i in range(len(p_xml_str_lists)):
        if result[i]:
            for obj in kwargs[p_xml_str_lists[i]]:
                if object_str == obj.name:
                    return obj
                try:
                    if object_str == obj.alias:
                        return obj
                except AttributeError:
                    # To avoid error when there is no alias for the object
                    pass
    return None


def retrieve_allocated_object_list(wanted_object, object_list, **kwargs):
    """Get current allocation for an object"""
    allocation_set = set()

    if isinstance(wanted_object.type, datamodel.BaseType):
        object_type = wanted_object.type
    else:
        _, object_type = retrieve_type(wanted_object.type.name, True, **kwargs)

    if object_type == datamodel.BaseType.FUNCTION:
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.allocated_function_list):
                allocation_set.add(fun_elem)
            # Else do nothing
    elif object_type == datamodel.BaseType.STATE:
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.allocated_state_list):
                allocation_set.add(fun_elem)
            # Else do nothing
    elif object_type == datamodel.BaseType.DATA:
        for fun_inter in object_list:
            if any(s == wanted_object.id for s in fun_inter.allocated_data_list):
                allocation_set.add(fun_inter)
            # Else do nothing
    elif object_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
        for fun_elem in object_list:
            if any(s == wanted_object.id for s in fun_elem.exposed_interface_list):
                allocation_set.add(fun_elem)
            # Else do nothing
    elif object_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
        for function in object_list:
            if any(s == function.id for s in wanted_object.allocated_function_list):
                allocation_set.add(function)
            # Else do nothing
    elif object_type == datamodel.BaseType.PHYSICAL_ELEMENT:
        for activity in object_list:
            if any(s == activity.id for s in wanted_object.allocated_activity_list):
                allocation_set.add(activity)
            # Else do nothing
    # Else do nothing

    if len(allocation_set) == 0:
        allocation_set = None
    # Else do nothing

    return allocation_set


def check_object_name_in_dict(**kwargs):
    """Returns lists of objects with their names depending on kwargs"""
    whole_objects_name_list = [[] for _ in range(len(XmlDictKeyListForObjects))]
    for i in range(len(XmlDictKeyListForObjects)):
        if kwargs.get(XmlDictKeyListForObjects[i], False):
            whole_objects_name_list[i] = check_object_name_in_list(kwargs[XmlDictKeyListForObjects[i]])
        # Else do nothing

    return whole_objects_name_list


def check_object_name_in_list(p_object_list):
    """
    Method that returns a list with all object aliases/names from object's list

    """
    object_name_list = []
    # Create the xml [object_name (and object_alias)] list
    for obj in p_object_list:
        object_name_list.append(obj.name)
        if hasattr(obj, 'alias'):
            if len(obj.alias) > 0:
                object_name_list.append(obj.alias)
            # Else do nothing
        # Else do nothing

    return object_name_list


def check_object_relationship(p_object_src, p_object_dest, p_context, **kwargs):
    if hasattr(p_object_src, 'type') and hasattr(p_object_dest, 'type'):
        is_relationship = False
        if isinstance(p_object_src.type, datamodel.BaseType):
            object_src_type = p_object_src.type
        else:
            _, object_src_type = retrieve_type(p_object_src.type.name, True, **kwargs)

        if isinstance(p_object_dest.type, datamodel.BaseType):
            object_dest_type = p_object_dest.type
        else:
            _, object_dest_type = retrieve_type(p_object_dest.type.name, True, **kwargs)

        Logger.set_debug(__name__,
                         f"Relationship detected in requirement/goal between {object_src_type} {p_object_src.name} and "
                         f"{object_dest_type} {p_object_dest.name}")
        if object_src_type == datamodel.BaseType.FUNCTION or object_src_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
            # Relationship with DATA, ATTRIBUTE, FUNCTIONAL_ELEMENT
            if object_dest_type == datamodel.BaseType.DATA:
                if object_src_type == datamodel.BaseType.FUNCTION:
                    xml_consumer_function_list = kwargs[XML_DICT_KEY_15_FUN_CONS_LIST]
                    xml_producer_function_list = kwargs[XML_DICT_KEY_16_FUN_PROD_LIST]

                    for xml_consumer_function in xml_consumer_function_list:
                        if xml_consumer_function[0] == p_object_dest and xml_consumer_function[1] == p_object_src:
                            Logger.set_info(__name__,
                                            f"{object_src_type} {p_object_src.name} consumes "
                                            f"{object_dest_type} {p_object_dest.name}")
                            is_relationship = True
                            break

                    if not is_relationship:
                        for xml_producer_function in xml_producer_function_list:
                            if xml_producer_function[0] == p_object_dest and xml_producer_function[1] == p_object_src:
                                Logger.set_info(__name__,
                                                f"{object_src_type} {p_object_src.name} produces "
                                                f"{object_dest_type} {p_object_dest.name}")
                                is_relationship = True
                                break
                    # Else do nothing

                    if not is_relationship:
                        Logger.set_warning(__name__,
                                           f"{object_src_type} {p_object_src.name} does not consume nor produce "
                                           f"{object_dest_type} {p_object_dest.name}")
                    # Else do nothing
                else:
                    print("Data for Functional interface")
            elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
                # Check if value of the attribute is in relationship context
                for described_object_id, value in p_object_dest.described_item_list:
                    if described_object_id == p_object_src.id:
                        is_relationship = True
                        if value in p_context:
                            Logger.set_info(__name__,
                                            f"{object_dest_type} {p_object_dest.name} of "
                                            f"{object_src_type} {p_object_src.name} has a value {value}")
                        else:
                            Logger.set_warning(__name__,
                                               f"Value of {object_dest_type} {p_object_dest.name} "
                                               f"for {object_src_type} {p_object_src.name} is not defined "
                                               f"by the relationship")
                        break
                    # Else do nothing

                if not is_relationship:
                    Logger.set_warning(__name__,
                                       f"Value of {object_dest_type} {p_object_dest.name} is not defined for "
                                       f"{object_src_type} {p_object_src.name}")
                # Else do nothing
            elif object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
                if object_src_type == datamodel.BaseType.FUNCTION:
                    if p_object_src.id in p_object_dest.allocated_function_list:
                        Logger.set_info(__name__,
                                        f"{object_dest_type} {p_object_dest.name} allocates "
                                        f"{object_src_type} {p_object_src.name}")
                        is_relationship = True
                    else:
                        Logger.set_warning(__name__,
                                           f"{object_src_type} {p_object_src.name} is not allocated to "
                                           f"{object_dest_type} {p_object_dest.name}")
                else:
                    # TODO relationship between fun_elem and fun_intf
                    print(f"Relationship detected between {object_src_type}: {p_object_src.name} and "
                          f"{object_dest_type}: {p_object_dest.name}")
                    print("Functional interface case")
            elif object_dest_type == datamodel.BaseType.FUNCTION:
                if object_src_type == datamodel.BaseType.FUNCTION:
                    # TODO investigate relationship based on inheritance
                    is_relationship = True
                # Else do nothing
            elif object_dest_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
                if object_src_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
                    # TODO investigate relationship based on inheritance
                    is_relationship = True
                # Else do nothing
            else:
                # TODO Warn about improper relationship between source type and destination type
                print("Not supported")
        elif object_src_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
            # Relationship with FUNCTION, FUNCTIONAL_INTERFACE, STATE, ATTRIBUTE, DATA
            if object_dest_type == datamodel.BaseType.FUNCTION:
                if p_object_dest.id in p_object_src.allocated_function_list:
                    Logger.set_info(__name__,
                                    f"{object_src_type} {p_object_src.name} allocates "
                                    f"{object_dest_type} {p_object_dest.name}")
                    is_relationship = True
                else:
                    Logger.set_warning(__name__,
                                       f"{object_dest_type} {p_object_dest.name} is not allocated to "
                                       f"{object_src_type} {p_object_src.name}")
            elif object_dest_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
                # TODO relationship between fun_elem and fun_intf
                print(f"Relationship detected between {object_src_type}: {p_object_src.name} and "
                      f"{object_dest_type}: {p_object_dest.name}")
                print("Functional interface case")
            elif object_dest_type == datamodel.BaseType.STATE:
                if p_object_dest.id in p_object_src.allocated_state_list:
                    Logger.set_info(__name__,
                                    f"{object_src_type} {p_object_src.name} allocates "
                                    f"{object_dest_type} {p_object_dest.name}")
                    is_relationship = True
                else:
                    Logger.set_warning(__name__,
                                       f"{object_dest_type} {p_object_dest.name} is not allocated to "
                                       f"{object_src_type} {p_object_src.name}")
            elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
                # Check if value of the attribute is in relationship context
                for described_object_id, value in p_object_dest.described_item_list:
                    if described_object_id == p_object_src.id:
                        is_relationship = True
                        if value in p_context:
                            Logger.set_info(__name__,
                                            f"{object_dest_type} {p_object_dest.name} of "
                                            f"{object_src_type} {p_object_src.name} has a value {value}")
                        else:
                            Logger.set_warning(__name__,
                                               f"Value of {object_dest_type} {p_object_dest.name} "
                                               f"for {object_src_type} {p_object_src.name} is not defined "
                                               f"by the relationship")
                        break
                    # Else do nothing

                if not is_relationship:
                    Logger.set_warning(__name__,
                                       f"Value of {object_dest_type} {p_object_dest.name} is not defined for "
                                       f"{object_src_type} {p_object_src.name}")
                # Else do nothing
            elif object_dest_type == datamodel.BaseType.DATA:
                for allocated_fun_id in p_object_src.allocated_function_list:
                    for xml_function in kwargs[XML_DICT_KEY_1_FUNCTION_LIST]:
                        if allocated_fun_id == xml_function.id:
                            if ([p_object_dest, xml_function] in kwargs[XML_DICT_KEY_15_FUN_CONS_LIST] or
                                    [p_object_dest, xml_function] in kwargs[XML_DICT_KEY_16_FUN_PROD_LIST]):
                                is_relationship = True
                                break
                            # Else do nothing
                        # Else do nothing

                if not is_relationship:
                    Logger.set_warning(__name__,
                                       f"{object_src_type} {p_object_src.name} has no allocated function "
                                       f"producing or consuming {object_dest_type} {p_object_dest.name}")
                # Else do nothing
            elif object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
                # TODO investigate relationship based on inheritance
                is_relationship = True
            else:
                # TODO Warn about improper relationship between source type and destination type
                print("Not supported")
        elif object_src_type == datamodel.BaseType.PHYSICAL_ELEMENT:
            # Relationship with FUNCTIONAL_ELEMENT, ATTRIBUTE
            if object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
                print("Functional element case")
            elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
                print("Attribute case")
            elif object_dest_type == datamodel.BaseType.PHYSICAL_ELEMENT:
                # TODO investigate relationship based on inheritance
                is_relationship = True
            else:
                # TODO Warn about improper relationship between source type and destination type
                print("Not supported")
        elif object_src_type == datamodel.BaseType.PHYSICAL_INTERFACE:
            # Relationship with FUNCTIONAL_INTERFACE, ATTRIBUTE
            if object_dest_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
                print("Functional interface case")
            elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
                print("Attribute case")
            elif object_dest_type == datamodel.BaseType.PHYSICAL_INTERFACE:
                # TODO investigate relationship based on inheritance
                is_relationship = True
            else:
                # TODO Warn about improper relationship between source type and destination type
                print("Not supported")
        elif object_src_type == datamodel.BaseType.STATE:
            # Relationship with FUNCTION, FUNCTIONAL_ELEMENT, ATTRIBUTE
            if object_dest_type == datamodel.BaseType.FUNCTION:
                print("Function case")
            elif object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
                print("Functional element case")
            elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
                print("Attribute case")
            elif object_dest_type == datamodel.BaseType.STATE:
                # TODO investigate relationship based on inheritance
                is_relationship = True
            else:
                # TODO Warn about improper relationship between source type and destination type
                print("Not supported")
        elif object_src_type == datamodel.BaseType.TRANSITION:
            # Relationship with STATE
            if object_dest_type == datamodel.BaseType.STATE:
                print("State case")
            else:
                # Warn about improper relationship between source type and destination type
                print("Not supported")
        elif object_src_type == datamodel.BaseType.ATTRIBUTE:
            if object_dest_type == datamodel.BaseType.FUNCTION or \
                    object_dest_type == datamodel.BaseType.FUNCTIONAL_INTERFACE or \
                    object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT or \
                    object_dest_type == datamodel.BaseType.PHYSICAL_INTERFACE or \
                    object_dest_type == datamodel.BaseType.PHYSICAL_ELEMENT or \
                    object_dest_type == datamodel.BaseType.STATE:
                # Check if value of the attribute is in relationship context
                for described_object_id, value in p_object_src.described_item_list:
                    if described_object_id == p_object_dest.id:
                        is_relationship = True
                        if value in p_context:
                            Logger.set_info(__name__,
                                            f"{object_src_type} {p_object_src.name} of "
                                            f"{object_dest_type} {p_object_dest.name} has a value {value}")
                        else:
                            Logger.set_warning(__name__,
                                               f"Value of {object_src_type} {p_object_src.name} "
                                               f"for {object_dest_type} {p_object_dest.name} is not defined "
                                               f"by the relationship")
                        break
                    # Else do nothing

                if not is_relationship:
                    Logger.set_warning(__name__,
                                       f"Value of {object_src_type} {p_object_src.name} is not defined for "
                                       f"{object_dest_type} {p_object_dest.name}")
                # Else do nothing
            elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
                is_relationship = True
            else:
                # TODO Warn about improper relationship between source type and destination type
                print("Not supported")
        else:
            # Warn about improper object source type
            print(f"Relationship not supported between {object_src_type}: {p_object_src.name} and "
                  f"{object_dest_type}: {p_object_dest.name}")
    elif hasattr(p_object_src, 'type') or hasattr(p_object_dest, 'type'):
        # At least one of the object is a type: the requirement/goal itself is creating the relationship
        is_relationship = True
    else:
        # The two object are types: they cannot be related
        is_relationship = False

    return is_relationship


def check_object_instance_list_requirement(object_instance_list, **kwargs):
    xml_requirement_list = kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]
    output_xml = kwargs['output_xml']

    for obj in object_instance_list:
        for xml_requirement in xml_requirement_list:
            if xml_requirement.text:
                req_subject_object = orchestrator_viewpoint_requirement.retrieve_req_subject_object(
                    xml_requirement.text, **kwargs)
                req_object_object_list = orchestrator_viewpoint_requirement.retrieve_req_object_object_list(
                    xml_requirement.text, **kwargs)
                req_condition_object_list = orchestrator_viewpoint_requirement.retrieve_req_condition_object_list(
                    xml_requirement.text, **kwargs)
                req_temporal_object_list = orchestrator_viewpoint_requirement.retrieve_req_temporal_object_list(
                    xml_requirement.text, **kwargs)

                if req_subject_object is not None:
                    if obj == req_subject_object:
                        if hasattr(obj, 'allocated_req_list'):
                            if xml_requirement.id not in obj.allocated_req_list:
                                obj.add_allocated_requirement(xml_requirement.id)
                                output_xml.write_object_allocation([[obj, xml_requirement]])

                                Logger.set_info(__name__,
                                                f"{xml_requirement.__class__.__name__} {xml_requirement.name} "
                                                f"is satisfied by "
                                                f"{obj.__class__.__name__} {obj.name}")
                            # Else do nothing
                        else:
                            Logger.set_error(__name__,
                                             f"{obj.__class__.__name__} {obj.name} cannot allocate requirements")
                    # Else do nothing
                # Else do nothing

                if len(req_object_object_list) > 0:
                    for req_object_object in req_object_object_list:
                        if obj == req_object_object:
                            if hasattr(obj, 'allocated_req_list'):
                                if xml_requirement.id not in obj.allocated_req_list:
                                    obj.add_allocated_requirement(xml_requirement.id)
                                    output_xml.write_object_allocation([[obj, xml_requirement]])

                                    Logger.set_info(__name__,
                                                    f"{xml_requirement.__class__.__name__} {xml_requirement.name} "
                                                    f"is satisfied by "
                                                    f"{obj.__class__.__name__} {obj.name}")
                                # Else do nothing
                            else:
                                Logger.set_error(__name__,
                                                 f"{obj.__class__.__name__} {obj.name} cannot allocate requirements")
                        # Else do nothing
                # Else do nothing

                if len(req_condition_object_list) > 0:
                    for req_condition_object in req_condition_object_list:
                        if obj == req_condition_object and obj != req_subject_object:
                            if hasattr(obj, 'allocated_req_list'):
                                if xml_requirement.id not in obj.allocated_req_list:
                                    obj.add_allocated_requirement(xml_requirement.id)
                                    output_xml.write_object_allocation([[obj, xml_requirement]])

                                    Logger.set_info(__name__,
                                                    f"{xml_requirement.__class__.__name__} {xml_requirement.name} "
                                                    f"is satisfied by "
                                                    f"{obj.__class__.__name__} {obj.name}")
                                # Else do nothing
                            else:
                                Logger.set_error(__name__,
                                                 f"{obj.__class__.__name__} {obj.name} cannot allocate requirements")
                        # Else do nothing
                # Else do nothing

                if len(req_temporal_object_list) > 0:
                    for req_temporal_object in req_temporal_object_list:
                        if obj == req_temporal_object and obj != req_subject_object:
                            if hasattr(obj, 'allocated_req_list'):
                                if xml_requirement.id not in obj.allocated_req_list:
                                    obj.add_allocated_requirement(xml_requirement.id)
                                    output_xml.write_object_allocation([[obj, xml_requirement]])

                                    Logger.set_info(__name__,
                                                    f"{xml_requirement.__class__.__name__} {xml_requirement.name} "
                                                    f"is satisfied by "
                                                    f"{obj.__class__.__name__} {obj.name}")
                                # Else do nothing
                            else:
                                Logger.set_error(__name__,
                                                 f"{obj.__class__.__name__} {obj.name} cannot allocate requirements")
                        # Else do nothing
                # Else do nothing
            # Else do nothing


def check_object_instance_list_goal(object_instance_list, **kwargs):
    xml_goal_list = kwargs[XML_DICT_KEY_9_GOAL_LIST]
    output_xml = kwargs['output_xml']

    for obj in object_instance_list:
        for xml_goal in xml_goal_list:
            if xml_goal.text:
                req_subject_object = orchestrator_viewpoint_goal.retrieve_goal_subject_object(
                    xml_goal.text, **kwargs)
                req_actor_object = orchestrator_viewpoint_goal.retrieve_goal_actor_object(
                    xml_goal.text, **kwargs)
                req_activity_object = orchestrator_viewpoint_goal.retrieve_goal_activity_object(
                    xml_goal.text, **kwargs)

                if req_subject_object is not None:
                    if obj == req_subject_object:
                        if hasattr(obj, 'allocated_goal_list'):
                            if xml_goal.id not in obj.allocated_goal_list:
                                obj.add_allocated_goal(xml_goal.id)
                                output_xml.write_object_allocation([[obj, xml_goal]])

                                Logger.set_info(__name__,
                                                f"{xml_goal.__class__.__name__} {xml_goal.name} "
                                                f"is satisfied by "
                                                f"{obj.__class__.__name__} {obj.name}")
                            # Else do nothing
                        else:
                            Logger.set_error(__name__,
                                             f"{obj.__class__.__name__} {obj.name} cannot allocate goals")
                    # Else do nothing
                # Else do nothing

                if req_actor_object is not None:
                    if obj == req_actor_object:
                        if hasattr(obj, 'allocated_goal_list'):
                            if xml_goal.id not in obj.allocated_goal_list:
                                obj.add_allocated_goal(xml_goal.id)
                                output_xml.write_object_allocation([[obj, xml_goal]])

                                Logger.set_info(__name__,
                                                f"{xml_goal.__class__.__name__} {xml_goal.name} "
                                                f"is satisfied by "
                                                f"{obj.__class__.__name__} {obj.name}")
                            # Else do nothing
                        else:
                            Logger.set_error(__name__,
                                             f"{obj.__class__.__name__} {obj.name} cannot allocate goals")
                    # Else do nothing
                # Else do nothing

                if req_activity_object is not None:
                    if obj == req_activity_object:
                        if hasattr(obj, 'allocated_goal_list'):
                            if xml_goal.id not in obj.allocated_goal_list:
                                obj.add_allocated_goal(xml_goal.id)
                                output_xml.write_object_allocation([[obj, xml_goal]])

                                Logger.set_info(__name__,
                                                f"{xml_goal.__class__.__name__} {xml_goal.name} "
                                                f"is satisfied by "
                                                f"{obj.__class__.__name__} {obj.name}")
                            # Else do nothing
                        else:
                            Logger.set_error(__name__,
                                             f"{obj.__class__.__name__} {obj.name} cannot allocate goals")
                    # Else do nothing
                # Else do nothing
            # Else do nothing


def check_object_is_parent_recursively(p_object_parent, p_object_child):
    if p_object_child.parent:
        if p_object_parent == p_object_child.parent:
            is_parent = True
        else:
            is_parent = check_object_is_parent_recursively(p_object_parent, p_object_child.parent)
    else:
        is_parent = False

    return is_parent


def check_object_is_not_family(p_object_a, p_object_b):
    if not check_object_is_parent_recursively(p_object_a, p_object_b) \
            and not check_object_is_parent_recursively(p_object_b, p_object_a):
        is_family = True
    else:
        is_family = False

    return is_family


def retrieve_object_type_requirement_list(p_object, **kwargs):
    requirement_list = []

    if hasattr(p_object, 'type'):
        if not isinstance(p_object.type, datamodel.BaseType):
            object_type, _ = retrieve_type(p_object.type.name, True, **kwargs)

            for requirement_id in object_type.allocated_req_list:
                for xml_requirement in kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST]:
                    if xml_requirement.id == requirement_id:
                        requirement_list.append(xml_requirement)
                    # Else do nothing
        # Else do nothing: base type has no allocated requirement
    # Else do nothing because it is a type

    return requirement_list
