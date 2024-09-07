""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries


# Modules
import datamodel
from . import orchestrator_object


def add_inherited_object(xml_obj_set, xml_allocated_obj_set, **kwargs):
    """Allocation Inheritance"""
    inherited_object_list = []
    for elem in xml_obj_set:
        if elem.derived:
            if isinstance(elem.type, datamodel.BaseType):
                elem_type = elem.type
            else:
                _, elem_type = orchestrator_object.retrieve_type(elem.type.name, True, **kwargs)

            if elem_type == datamodel.BaseType.FUNCTION:
                for data, fun in xml_allocated_obj_set.copy():
                    if fun == elem.derived:
                        xml_allocated_obj_set.append([data, elem])
                        inherited_object_list.append([elem, data])
                    # Else do nothing
            elif elem_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
                pair = [elem, {i for i in elem.derived.allocated_function_list
                               if i not in elem.allocated_function_list and i in xml_allocated_obj_set}]
                elem.allocated_function_list = elem.allocated_function_list.union(
                    elem.derived.allocated_function_list)
                inherited_object_list.append(pair)
            elif elem_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
                pair = [elem, {i for i in elem.derived.allocated_data_list
                               if i not in elem.allocated_data_list and i in xml_allocated_obj_set}]
                elem.allocated_data_list = elem.allocated_data_list.union(
                    elem.derived.allocated_data_list)
                inherited_object_list.append(pair)
            # Else do nothing

    return inherited_object_list


def remove_inherited_object(pairs_to_reset, xml_allocated_obj_set, **kwargs):
    """Reset Allocation Inheritance"""
    for pair in pairs_to_reset:
        if isinstance(pair[0].type, datamodel.BaseType):
            elem_type = pair[0].type
        else:
            _, elem_type = orchestrator_object.retrieve_type(pair[0].type.name, True, **kwargs)

        if elem_type == datamodel.BaseType.FUNCTION:
            xml_allocated_obj_set.remove([pair[1], pair[0]])
        elif elem_type == datamodel.BaseType.FUNCTIONAL_ELEMENT:
            [pair[0].allocated_function_list.remove(fun_id) for fun_id in pair[1]]
        elif elem_type == datamodel.BaseType.FUNCTIONAL_INTERFACE:
            [pair[0].allocated_data_list.remove(data_id) for data_id in pair[1]]
        # Else do nothing


def add_inherited_object_children(*xml_obj_set, level=None):
    """Check if object from xml_obj_set is derived, if yes:
    - call retrieve_object_derived_children()
    - returns derived_parent_dict of derived objects id, derived_child_set of derived objects and
    derived_child_id_list
    Parameter:
    - obj: set() of objects
    - level: diagram level"""
    derived_child_set = set()
    derived_parent_dict = {}
    derived_child_id_list = set()

    for xml_set in xml_obj_set:
        for elem in xml_set:
            if elem.derived:
                partial_child_set, partial_parent_dict, partial_child_id_set = retrieve_object_derived_children(elem,
                                                                                                                level)
                derived_child_set = derived_child_set.union(partial_child_set)
                derived_parent_dict.update(partial_parent_dict)
                derived_child_id_list = derived_child_id_list.union(partial_child_id_set)

    return derived_child_set, derived_parent_dict, derived_child_id_list


def retrieve_object_derived_children(obj, level):
    """Add derived object childs to object and set derived parent to object"""
    derived_parent_dict = {}

    [obj.add_child(c) for c in obj.derived.child_list
     if c.parent == obj.derived]
    [c.set_parent(obj) for c in obj.derived.child_list
     if c.parent == obj.derived]
    for child in obj.derived.child_list:
        derived_parent_dict[str(child.id)] = str(obj.id)
    derived_child_set = orchestrator_object.retrieve_object_children_recursively(obj.derived,
                                                                                 None,
                                                                                 None,
                                                                                 None,
                                                                                 level)[0]
    derived_child_id_list = {c.id for c in obj.derived.child_list}
    obj.derived.child_list.clear()
    derived_child_set.remove(obj.derived)

    return derived_child_set, derived_parent_dict, derived_child_id_list


def remove_inherited_object_children(*xml_obj_set, derived_child_id=None):
    """Check if there is first level derived child id list, if yes reset original child/parent
    relationships"""
    if derived_child_id:
        for xml_set in xml_obj_set:
            for elem in xml_set:
                if elem.derived:
                    child_pop = [c for c in elem.child_list
                                 if c.id in [f for f in derived_child_id]]
                    [elem.derived.add_child(c) for c in child_pop]
                    [c.set_parent(elem.derived) for c in child_pop]
