"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ATTRIBUTE_LIST, XML_DICT_KEY_10_VIEW_LIST, XML_DICT_KEY_11_TYPE_LIST, \
    XML_DICT_KEY_12_FUN_CONS_LIST, XML_DICT_KEY_13_FUN_PROD_LIST
from jarvis import util
from jarvis.orchestrator import orchestrator_viewpoint_requirement
from jarvis.query import query_object, question_answer
from tools import Logger


class ObjectInstanceList(list):
    nb_object_instance_base_type = 9

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
            8: kwargs['output_xml'].write_requirement
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
        8: datamodel.Requirement
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

        # Data() and View() do not have aliases
        if not isinstance(self.object_instance, (datamodel.Data, datamodel.View)):
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
            existing_object = query_object.query_object_by_name(object_name, **kwargs)

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

                check = 1

    return check


def retrieve_type(p_type_str, p_is_silent=False, **kwargs):
    specific_type = None
    base_type = None

    if p_type_str.capitalize() in [str(i) for i in datamodel.BaseType]:
        base_type = next((i for i in [str(i) for i in datamodel.BaseType]
                          if i == p_type_str.capitalize()))
    else:
        specific_type = query_object.query_object_by_name(p_type_str,
                                                          **{XML_DICT_KEY_11_TYPE_LIST: kwargs[XML_DICT_KEY_11_TYPE_LIST]})
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
                            implicit_object = question_answer.get_transition_between_states(p_object_dest,
                                                                                            object_in_context,
                                                                                            **kwargs)

    return implicit_object


def check_object_relationship(p_object_src, p_object_dest, p_context, **kwargs):
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
                     f"Relationship detected in requirement between {object_src_type} {p_object_src.name} and "
                     f"{object_dest_type} {p_object_dest.name}")
    if object_src_type == datamodel.BaseType.FUNCTION or object_src_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
        # Relationship with DATA, ATTRIBUTE
        if object_dest_type == datamodel.BaseType.DATA:
            if object_src_type == datamodel.BaseType.FUNCTION:
                xml_consumer_function_list = kwargs[XML_DICT_KEY_12_FUN_CONS_LIST]
                xml_producer_function_list = kwargs[XML_DICT_KEY_13_FUN_PROD_LIST]

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
            is_value_defined = False
            for described_object, value in p_object_dest.described_item_list:
                if described_object == p_object_src:
                    is_value_defined = True
                    if value in p_context:
                        Logger.set_info(__name__,
                                        f"{object_dest_type} {p_object_dest.name} of "
                                        f"{object_src_type} {p_object_src.name} has a value {value}")
                        is_relationship = True
                        break
                    # Else do nothing

            if not is_relationship:
                if not is_value_defined:
                    Logger.set_warning(__name__,
                                       f"Value of {object_dest_type} {p_object_dest.name} is not defined for "
                                       f"{object_src_type} {p_object_src.name}")
                else:
                    Logger.set_warning(__name__,
                                       f"Value of {object_dest_type} {p_object_dest.name} is different from the one "
                                       f"given for {object_src_type} {p_object_src.name}")
            # Else do nothing
        # Else do nothing
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
            # TODO: relationship between fun_elem and fun_intf
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
            # TODO: relationship between fun_elem and attribute
            print(f"Relationship detected between {object_src_type}: {p_object_src.name} and "
                  f"{object_dest_type}: {p_object_dest.name}")
            print("Attribute case")
        elif object_dest_type == datamodel.BaseType.DATA:
            for allocated_fun_id in p_object_src.allocated_function_list:
                for xml_function in kwargs[XML_DICT_KEY_1_FUNCTION_LIST]:
                    if allocated_fun_id == xml_function.id:
                        if ([p_object_dest, xml_function] in kwargs[XML_DICT_KEY_12_FUN_CONS_LIST] or
                                [p_object_dest, xml_function] in kwargs[XML_DICT_KEY_13_FUN_PROD_LIST]):
                            is_relationship = True
                            break
                        # Else do nothing
                    # Else do nothing

            if not is_relationship:
                Logger.set_warning(__name__,
                                   f"{object_src_type} {p_object_src.name} has no allocated function "
                                   f"producing or consuming {object_dest_type} {p_object_dest.name}")
            # Else do nothing
        # Else do nothing
    elif object_src_type == datamodel.BaseType.PHYSICAL_ELEMENT:
        # Relationship with FUNCTIONAL_ELEMENT, ATTRIBUTE
        if object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
            print("Functional element case")
        elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
            print("Attribute case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    elif object_src_type == datamodel.BaseType.PHYSICAL_INTERFACE:
        # Relationship with FUNCTIONAL_INTERFACE, ATTRIBUTE
        if object_dest_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
            print("Functional interface case")
        elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
            print("Attribute case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    elif object_src_type == datamodel.BaseType.STATE:
        # Relationship with FUNCTION, FUNCTIONAL_ELEMENT, ATTRIBUTE
        if object_dest_type == datamodel.BaseType.FUNCTION:
            print("Function case")
        elif object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
            print("Functional element case")
        elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
            print("Attribute case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    elif object_src_type == datamodel.BaseType.TRANSITION:
        # Relationship with STATE
        if object_dest_type == datamodel.BaseType.STATE:
            print("State case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    else:
        # Warn about improper object source type
        print(f"Relationship not supported between {object_src_type}: {p_object_src.name} and "
              f"{object_dest_type}: {p_object_dest.name}")

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
                        if xml_requirement.id not in obj.allocated_req_list:
                            obj.add_allocated_requirement(xml_requirement.id)
                            output_xml.write_object_allocation([[obj, xml_requirement]])

                            Logger.set_info(__name__,
                                            f"Requirement {xml_requirement.name} is satisfied by "
                                            f"{obj.name}")
                        # Else do nothing
                    # Else do nothing
                # Else do nothing

                if len(req_object_object_list) > 0:
                    for req_object_object in req_object_object_list:
                        if obj == req_object_object:
                            if xml_requirement.id not in obj.allocated_req_list:
                                obj.add_allocated_requirement(xml_requirement.id)
                                output_xml.write_object_allocation([[obj, xml_requirement]])

                                Logger.set_info(__name__,
                                                f"Requirement {xml_requirement.name} is satisfied by "
                                                f"{obj.name}")
                            # Else do nothing
                        # Else do nothing
                # Else do nothing

                if len(req_condition_object_list) > 0:
                    for req_condition_object in req_condition_object_list:
                        if obj == req_condition_object and obj != req_subject_object:
                            if xml_requirement.id not in obj.allocated_req_list:
                                obj.add_allocated_requirement(xml_requirement.id)
                                output_xml.write_object_allocation([[obj, xml_requirement]])

                                Logger.set_info(__name__,
                                                f"Requirement {xml_requirement.name} is satisfied by "
                                                f"{obj.name}")
                            # Else do nothing
                        # Else do nothing
                # Else do nothing

                if len(req_temporal_object_list) > 0:
                    for req_temporal_object in req_temporal_object_list:
                        if obj == req_temporal_object and obj != req_subject_object:
                            if xml_requirement.id not in obj.allocated_req_list:
                                obj.add_allocated_requirement(xml_requirement.id)
                                output_xml.write_object_allocation([[obj, xml_requirement]])

                                Logger.set_info(__name__,
                                                f"Requirement {xml_requirement.name} is satisfied by "
                                                f"{obj.name}")
                            # Else do nothing
                        # Else do nothing
                # Else do nothing
            # Else do nothing


def check_object_is_parent_recursively(p_object_parent, p_object_child):
    is_parent = False

    if p_object_child.parent:
        if p_object_parent == p_object_child.parent:
            is_parent = True
        else:
            check_object_is_parent_recursively(p_object_parent, p_object_child.parent)
    # Else do nothing

    return is_parent


def check_object_is_not_family(p_object_a, p_object_b):
    if not check_object_is_parent_recursively(p_object_a, p_object_b) \
            and not check_object_is_parent_recursively(p_object_b, p_object_a):
        is_family = True
    else:
        is_family = False

    return is_family
