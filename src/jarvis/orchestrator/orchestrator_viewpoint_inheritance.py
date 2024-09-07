""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries


# Modules
from tools import Logger


def add_inherited_attribute(xml_attribute_set, *xml_object_set):
    """Attribute inheritance"""
    modified_attrib_set = set()
    derived_elem = set()

    for xml_set in xml_object_set:
        [derived_elem.add(e) for e in xml_set if e.derived]

    for attribute in xml_attribute_set:
        for der_obj in derived_elem:
            is_attribute = False
            for obj_id, value in attribute.described_item_list:
                if obj_id == der_obj.id:
                    is_attribute = True
                    Logger.set_info(__name__, f'Attribute "{attribute.name}" specialized for "{der_obj.name}" with '
                                              f'value "{value}"')
                    break

            if not is_attribute:
                for obj_id, value in attribute.described_item_list.copy():
                    if obj_id == der_obj.derived.id:
                        attribute.add_described_item((der_obj.id, value))
                        modified_attrib_set.add((attribute.id, der_obj.id, value))
                    # Else do nothing
            # Else do nothing

    return modified_attrib_set


def remove_inherited_attribute(xml_attribute_set, to_be_reset_id_set):
    """Reset attributes"""
    for attribute in xml_attribute_set:
        [attribute.described_item_list.remove((e[1], e[2])) for e in to_be_reset_id_set
         if e[0] == attribute.id]


def add_inherited_view(xml_view_set, *xml_obj_set):
    """View inheritance"""
    temp_view_set = set()
    derived_elem_set = set()

    for xml_set in xml_obj_set:
        [derived_elem_set.add(e) for e in xml_set if e.derived]

    for view in xml_view_set:
        for item_id in view.allocated_item_list.copy():
            for obj in derived_elem_set:
                if item_id == obj.derived.id:
                    temp_view_set.add((view.id, obj.id))
                    view.add_allocated_item(obj.id)

    return temp_view_set


def remove_inherited_view(xml_view_set, to_be_removed_id):
    """Reset views"""
    for view in xml_view_set:
        for ids in to_be_removed_id:
            if view.id == ids[0]:
                view.allocated_item_list.remove(ids[1])
            # Else do nothing
