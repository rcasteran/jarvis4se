"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re

# Modules
import datamodel
from jarvis import util
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
            spec_obj_type = None
            if elem[1].capitalize() in [str(i) for i in datamodel.BaseType]:
                base_type = next((i for i in [str(i) for i in datamodel.BaseType]
                                  if i == elem[1].capitalize()))
            else:
                spec_obj_type = question_answer.check_get_object(elem[1],
                                                                 **{'xml_type_list': kwargs['xml_type_list']})
                if not spec_obj_type:
                    Logger.set_error(__name__,
                                     f"No valid type found for {elem[1]}")
                    continue
                base_type = get_base_type_recursively(spec_obj_type)
            if base_type is None:
                Logger.set_error(__name__,
                                 f"No valid base type found for {elem[1]}")
                continue

            existing_object = question_answer.check_get_object(elem[0], **kwargs)
            if existing_object:
                if isinstance(existing_object.type, datamodel.BaseType):
                    Logger.set_info(__name__, f"{existing_object.type} with the name {elem[0]} already exists")
                else:
                    Logger.set_info(__name__, f"{existing_object.type.name} with the name {elem[0]} already exists")
                continue

            new_object = ObjectInstance(elem[0], base_type, spec_obj_type, **kwargs)
            if isinstance(new_object.get_instance().type, datamodel.BaseType):
                Logger.set_info(__name__,
                                f"{new_object.get_instance().name} is a {str(new_object.get_instance().type)}")
            else:
                Logger.set_info(__name__,
                                f"{new_object.get_instance().name} is a {new_object.get_instance().type.name}")

            object_instance_per_base_type_list[new_object.base_type_idx].append(new_object.get_instance())

    check = 0
    if any(object_instance_per_base_type_list):
        for object_base_type, object_instance_list in enumerate(object_instance_per_base_type_list):
            if object_instance_list:
                object_instance_list.write_instance(**kwargs)
                check = 1

    return check


def get_base_type_recursively(obj_type):
    """Checks type: if it's a BaseType or its base else recursively return """
    if isinstance(obj_type, datamodel.BaseType):
        base_type = obj_type
    elif obj_type.base in [str(i) for i in datamodel.BaseType]:
        base_type = obj_type.base
    else:
        base_type = get_base_type_recursively(obj_type.base)

    return base_type
