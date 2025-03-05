""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
import datamodel
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
from . import orchestrator_object, orchestrator_object_allocation
from jarvis import util
from tools import Logger


def add_view(p_str_list, **kwargs):
    """
        Check if each string in view_name_str is not already corresponding to an actual
        object's name, create new View() object, instantiate it, write it within XML and
        then returns update_list.

            Parameters:
                p_str_list ([str]) : Lists of string from jarvis cell
                xml_view_list ([Function]) : view list from xml parsing
                output_xml (XmlWriter3SE object) : XML's file object

            Returns:
                1 if update, else 0
        """
    xml_view_list = kwargs[XML_DICT_KEY_13_VIEW_LIST]
    output_xml = kwargs['output_xml']
    view_list = []
    update = 0

    # Create a list with all view names already in the xml
    xml_view_name_list = orchestrator_object.check_object_name_in_list(xml_view_list)

    for elem in p_str_list:
        view_name = elem.replace('"', "")

        # Loop on the list and create set for functions
        if view_name not in xml_view_name_list:
            # Instantiate view class
            view = datamodel.View(name=view_name, uid=util.get_unique_id())
            # Add view to new set() and existing set() from xml
            xml_view_list.add(view)
            view_list.append(view)

        activate_view(view_name, xml_view_list)

        if view_list:
            output_xml.write_view(view_list)
            for view in view_list:
                Logger.set_info(__name__,
                                view.name + " is a view")
            update = 1

    return update


def activate_view(view_name, xml_view_list):
    """Activates View from view's name str"""
    for view in xml_view_list:
        if view_name == view.name:
            view.set_activation(True)
        else:
            view.set_activation(False)


def check_get_consider(consider_str_list, **kwargs):
    """
    Check and get all "consider xxx" strings. If corresponds to an actual object not yet added to
    the current view => add it to View object and as allocatedItem within xml
    Args:
        consider_str_list ([strings]): list of strings (separated by comma is possible)
        xml_function_list ([Function]) : Function list from xml parsing
        xml_fun_elem_list ([Fun Elem]) : Functional Element list from xml parsing
        xml_data_list ([Data]) : Data list from xml parsing
        xml_view_list ([View]) : View list from xml parsing
        output_xml (XmlWriter3SE object) : XML's file object

    Returns:
        update ([0/1]) : 1 if update, else 0
    """
    update = 0

    # [data, function, fun_elem] case
    xml_data_list = kwargs[XML_DICT_KEY_0_DATA_LIST]
    xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
    xml_fun_elem_list = kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]

    # [information, activity, phy_elem] case
    xml_information_list = kwargs[XML_DICT_KEY_11_INFORMATION_LIST]
    xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]
    xml_phy_elem_list = kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST]

    # Create lists with all object names/aliases already in the xml
    xml_data_name_list = orchestrator_object.check_object_name_in_list(xml_data_list)
    xml_function_name_list = orchestrator_object.check_object_name_in_list(xml_function_list)
    xml_fun_elem_name_list = orchestrator_object.check_object_name_in_list(xml_fun_elem_list)
    xml_information_name_list = orchestrator_object.check_object_name_in_list(xml_information_list)
    xml_activity_name_list = orchestrator_object.check_object_name_in_list(xml_activity_list)
    xml_phy_elem_name_list = orchestrator_object.check_object_name_in_list(xml_phy_elem_list)

    consider_str_list = util.cut_chain_from_string_list(consider_str_list)

    for consider_str in consider_str_list:
        is_data_related = (consider_str in [*xml_fun_elem_name_list, *xml_function_name_list,
                                            *xml_data_name_list])
        is_information_related = (consider_str in [*xml_phy_elem_name_list, *xml_activity_name_list,
                                                   *xml_information_name_list])
        if is_data_related:
            update = orchestrator_object_allocation.check_add_allocated_item_to_view(consider_str, **kwargs)
        elif is_information_related:
            update = orchestrator_object_allocation.check_add_allocated_item_to_view(consider_str, **kwargs)
        else:
            Logger.set_warning(__name__,
                               f'Object {consider_str} does not exist, available object types are:\n'
                               f'- Functional Element, Function and Data\n'
                               f'- Physical Element, Activity and Information')

    return update
