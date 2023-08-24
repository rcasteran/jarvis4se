"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re

# Modules
import datamodel
from jarvis import util


class ObjectInstanceList(list):
    nb_object_instance_base_type = 8

    def __init__(self, p_base_type_idx):
        super().__init__()
        self.base_type_idx = p_base_type_idx

    def write_instance(self, output_xml):
        # Object write routine list must be in the same order as object_instance_list in ObjectInstance
        # Object write routine has a size of nb_object_instance_base_type
        object_write_routine_list = {
            0: output_xml.write_data,
            1: output_xml.write_function,
            2: output_xml.write_functional_element,
            3: output_xml.write_functional_interface,
            4: output_xml.write_physical_element,
            5: output_xml.write_physical_interface,
            6: output_xml.write_state,
            7: output_xml.write_transition,
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
