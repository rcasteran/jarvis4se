""" @defgroup query
Jarvis query module
"""
# Libraries


# Modules
from jarvis.orchestrator import orchestrator_object_inheritance, orchestrator_viewpoint_inheritance


def query_inheritance_add_inherited_object(xml_obj_set, xml_allocated_obj_set, **kwargs):
    return orchestrator_object_inheritance.add_inherited_object(xml_obj_set, xml_allocated_obj_set, **kwargs)


def query_inheritance_remove_inherited_object(pairs_to_reset, xml_allocated_obj_set, **kwargs):
    return orchestrator_object_inheritance.remove_inherited_object(pairs_to_reset, xml_allocated_obj_set, **kwargs)


def query_inheritance_add_inherited_object_children(*xml_obj_set, level=None):
    return orchestrator_object_inheritance.add_inherited_object_children(*xml_obj_set, level=level)


def query_inheritance_retrieve_object_derived_children(obj, level):
    return orchestrator_object_inheritance.retrieve_object_derived_children(obj, level)


def query_inheritance_remove_inherited_object_children(*xml_obj_set, derived_child_id=None):
    return orchestrator_object_inheritance.remove_inherited_object_children(*xml_obj_set, derived_child_id)


def query_inheritance_add_inherited_attribute(xml_attribute_set, *xml_object_set):
    return orchestrator_viewpoint_inheritance.add_inherited_attribute(xml_attribute_set, *xml_object_set)


def query_inheritance_remove_inherited_attribute(xml_attribute_set, to_be_reset_id_set):
    return orchestrator_viewpoint_inheritance.remove_inherited_attribute(xml_attribute_set, to_be_reset_id_set)


def query_inheritance_add_inherited_view(xml_view_set, *xml_obj_set):
    return orchestrator_viewpoint_inheritance.add_inherited_view(xml_view_set, *xml_obj_set)


def query_inheritance_remove_inherited_view(xml_view_set, to_be_removed_id):
    return orchestrator_viewpoint_inheritance.remove_inherited_view(xml_view_set, to_be_removed_id)
