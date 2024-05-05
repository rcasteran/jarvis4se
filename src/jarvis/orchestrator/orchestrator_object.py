"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re

# Modules
import datamodel
from jarvis import util
from jarvis.orchestrator import orchestrator_viewpoint_requirement
from jarvis.query import question_answer
from tools import Logger


class ObjectInstanceList(list):
    nb_object_instance_base_type = 8

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
            0: kwargs['xml_data_list'].add,
            1: kwargs['xml_function_list'].add,
            2: kwargs['xml_fun_elem_list'].add,
            3: kwargs['xml_fun_inter_list'].add,
            4: kwargs['xml_phy_elem_list'].add,
            5: kwargs['xml_phy_inter_list'].add,
            6: kwargs['xml_state_list'].add,
            7: kwargs['xml_transition_list'].add,
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

    for elem in obj_type_str_list:
        if "?" not in elem[1]:
            specific_type, base_type = retrieve_type(elem[1], **kwargs)
            existing_object = question_answer.check_get_object(elem[0], **kwargs)

            if existing_object:
                if isinstance(existing_object.type, datamodel.BaseType):
                    Logger.set_info(__name__, f"{existing_object.type} with the name {elem[0]} already exists")
                else:
                    Logger.set_info(__name__, f"{existing_object.type.name} with the name {elem[0]} already exists")
            elif base_type is not None:
                new_object = ObjectInstance(elem[0], base_type, specific_type, **kwargs)
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
        specific_type = question_answer.check_get_object(p_type_str,
                                                         **{'xml_type_list': kwargs['xml_type_list']})
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


def check_object_relationship(object_src, object_dest, context, **kwargs):
    is_relationship = False

    if isinstance(object_src.type, datamodel.BaseType):
        object_src_type = object_src.type
    else:
        object_src_type = object_src.type.name

    if isinstance(object_dest.type, datamodel.BaseType):
        object_dest_type = object_dest.type
    else:
        object_dest_type = object_dest.type.name

    if object_src_type == datamodel.BaseType.FUNCTION or object_src_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
        # Relationship with DATA, ATTRIBUTE
        Logger.set_debug(__name__,
                         f"Relationship detected in requirement between {object_src_type} {object_src.name} and "
                         f"{object_dest_type} {object_dest.name}")
        if object_dest_type == datamodel.BaseType.DATA:
            if object_src_type == datamodel.BaseType.FUNCTION:
                xml_consumer_function_list = kwargs['xml_consumer_function_list']
                xml_producer_function_list = kwargs['xml_producer_function_list']

                for xml_consumer_function in xml_consumer_function_list:
                    if xml_consumer_function[0] == object_dest.name and xml_consumer_function[1] == object_src:
                        Logger.set_info(__name__,
                                        f"{object_src_type} {object_src.name} consumes "
                                        f"{object_dest_type} {object_dest.name}")
                        is_relationship = True
                        break

                if not is_relationship:
                    for xml_producer_function in xml_producer_function_list:
                        if xml_producer_function[0] == object_dest.name and xml_producer_function[1] == object_src:
                            Logger.set_info(__name__,
                                            f"{object_src_type} {object_src.name} produces "
                                            f"{object_dest_type} {object_dest.name}")
                            is_relationship = True
                            break
                # Else do nothing

                if not is_relationship:
                    Logger.set_warning(__name__,
                                       f"{object_src_type} {object_src.name} does not consume nor produce "
                                       f"{object_dest_type} {object_dest.name}")
                # Else do nothing
            else:
                print("Data for Functional interface")
        elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
            # Check if value of the attribute is in relationship context
            is_value_defined = False
            for described_object, value in object_dest.described_item_list:
                if described_object == object_src:
                    is_value_defined = True
                    if value in context:
                        Logger.set_info(__name__,
                                        f"{object_dest_type} {object_dest.name} of "
                                        f"{object_src_type} {object_src.name} has a value {value}")
                        is_relationship = True
                        break
                    # Else do nothing

            if not is_relationship:
                if not is_value_defined:
                    Logger.set_warning(__name__,
                                       f"Value of {object_dest_type} {object_dest.name} is not defined for "
                                       f"{object_src_type} {object_src.name}")
                else:
                    Logger.set_warning(__name__,
                                       f"Value of {object_dest_type} {object_dest.name} is different from the one "
                                       f"given for {object_src_type} {object_src.name}")
            # Else do nothing
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    elif object_src_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
        # Relationship with FUNCTION, FUNCTIONAL_INTERFACE, STATE, ATTRIBUTE
        print(f"Relationship detected between {object_src_type}: {object_src.name} and "
              f"{object_dest_type}: {object_dest.name}")
        if object_dest_type == datamodel.BaseType.FUNCTION:
            print("Function case")
        elif object_dest_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
            print("Functional interface case")
        elif object_dest_type == datamodel.BaseType.STATE:
            print("State case")
        elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
            print("Attribute case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    elif object_src_type == datamodel.BaseType.PHYSICAL_ELEMENT:
        # Relationship with FUNCTIONAL_ELEMENT, ATTRIBUTE
        print(f"Relationship detected between {object_src_type}: {object_src.name} and "
              f"{object_dest_type}: {object_dest.name}")
        if object_dest_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
            print("Functional element case")
        elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
            print("Attribute case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    elif object_src_type == datamodel.BaseType.PHYSICAL_INTERFACE:
        # Relationship with FUNCTIONAL_INTERFACE, ATTRIBUTE
        print(f"Relationship detected between {object_src_type}: {object_src.name} and "
              f"{object_dest_type}: {object_dest.name}")
        if object_dest_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
            print("Functional interface case")
        elif object_dest_type == datamodel.BaseType.ATTRIBUTE:
            print("Attribute case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    elif object_src_type == datamodel.BaseType.STATE:
        # Relationship with FUNCTION, FUNCTIONAL_ELEMENT, ATTRIBUTE
        print(f"Relationship detected between {object_src_type}: {object_src.name} and "
              f"{object_dest_type}: {object_dest.name}")
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
        print(f"Relationship detected between {object_src_type}: {object_src.name} and "
              f"{object_dest_type}: {object_dest.name}")
        if object_dest_type == datamodel.BaseType.STATE:
            print("State case")
        else:
            # Warn about improper relationship between source type and destination type
            print("Not supported")
    else:
        # Warn about improper object source type
        print("Not supported")

    return is_relationship


def check_object_instance_list_requirement(object_instance_list, **kwargs):
    xml_requirement_list = kwargs['xml_requirement_list']
    output_xml = kwargs['output_xml']

    for obj in object_instance_list:
        for xml_requirement in xml_requirement_list:
            req_subject_object = orchestrator_viewpoint_requirement.retrieve_req_subject_object(
                xml_requirement.description, **kwargs)
            req_object_object_list = orchestrator_viewpoint_requirement.retrieve_req_object_object_list(
                xml_requirement.description, **kwargs)

            if req_subject_object is not None:
                if obj == req_subject_object:
                    obj.add_allocated_requirement(xml_requirement)
                    output_xml.write_object_allocation([[obj, xml_requirement]])

                    Logger.set_info(__name__,
                                    f"Requirement {xml_requirement.name} is satisfied by "
                                    f"{obj.name}")
            # Else do nothing

            if len(req_object_object_list) > 0:
                for req_object_object in req_object_object_list:
                    if obj == req_object_object:
                        obj.add_allocated_requirement(xml_requirement)
                        output_xml.write_object_allocation([[obj, xml_requirement]])

                        Logger.set_info(__name__,
                                        f"Requirement {xml_requirement.name} is satisfied by "
                                        f"{obj.name}")
            # Else do nothing
