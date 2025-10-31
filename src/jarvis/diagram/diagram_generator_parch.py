"""@defgroup diagram
Jarvis diagram module
"""
# Libraries

# Modules
import plantuml_adapter
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
from jarvis.query import query_object
from tools import Logger
from . import util


def show_phy_elem_context(phy_elem_str, **kwargs):
    """@ingroup diagram
    @anchor show_fun_elem_context
    Creates lists with desired objects for physical element context, send them to plantuml_adapter.py
    and returns plantuml text
    @param[in] phy_elem_str: name of the physical element
    @param[in] **kwargs: dictionaries
    @return plantuml text
    """
    plantuml_text = None
    xml_phy_elem_list = kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST]
    xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]
    xml_consumer_activity_list = kwargs[XML_DICT_KEY_17_ACT_CONS_LIST]
    xml_producer_activity_list = kwargs[XML_DICT_KEY_18_ACT_PROD_LIST]
    xml_attribute_list = kwargs[XML_DICT_KEY_12_ATTRIBUTE_LIST]
    xml_phy_inter_list = kwargs[XML_DICT_KEY_5_PHY_INTF_LIST]
    xml_information_list = kwargs[XML_DICT_KEY_11_INFORMATION_LIST]

    main_phy_elem = query_object.query_object_by_name(phy_elem_str, **{XML_DICT_KEY_4_PHY_ELEM_LIST: xml_phy_elem_list})
    if not main_phy_elem:
        return plantuml_text

    # Get allocated activities to physical element
    allocated_activity_list = set()
    for xml_activity in xml_activity_list:
        if xml_activity.id in main_phy_elem.allocated_activity_list:
            allocated_activity_list.add(xml_activity)
        # Else do nothing

    new_activity_list, new_consumer_list, new_producer_list = util.get_allocated_function_context_lists(
        allocated_activity_list,
        xml_consumer_activity_list,
        xml_producer_activity_list)

    Logger.set_debug(__name__, f'list of activities: {new_activity_list}')
    Logger.set_debug(__name__, f'list of consumer list: {new_consumer_list}')
    Logger.set_debug(__name__, f'list of producer list: {new_producer_list}')

    # TODO : phy_elem_inter_list to be removed (not used anymore)
    phy_elem_list, interface_list, phy_elem_inter_list = util.get_fun_inter_for_fun_elem_context(
        main_phy_elem, xml_phy_inter_list, xml_phy_elem_list)

    Logger.set_debug(__name__, f'list of physical element: {phy_elem_list}')
    Logger.set_debug(__name__, f'list of physical interfaces: {interface_list}')

    for activity in new_activity_list:
        for elem in xml_phy_elem_list:
            if any(z == activity.id for z in elem.allocated_activity_list) and elem not in phy_elem_list:
                phy_elem_list.add(elem)

    for elem in phy_elem_list.copy():
        for str_id in elem.allocated_activity_list.copy():
            if str_id not in [i.id for i in new_activity_list]:
                elem.allocated_activity_list.remove(str_id)

    # Remove parent for main physical element : we do not care about it in context diagram
    if main_phy_elem.parent:
        if main_phy_elem.parent in phy_elem_list:
            phy_elem_list.remove(main_phy_elem.parent)
            for main_phy_elem_parent_child in main_phy_elem.parent.child_list:
                main_phy_elem_parent_child.parent = None
        # Else do nothing

    plantuml_text = plantuml_adapter.get_fun_elem_context_diagram(new_activity_list,
                                                                  new_consumer_list,
                                                                  new_producer_list,
                                                                  xml_information_list,
                                                                  xml_attribute_list,
                                                                  phy_elem_list,
                                                                  interface_list)

    Logger.set_info(__name__,
                    f"Context Diagram for {phy_elem_str} generated")

    return plantuml_text


def show_phy_elem_decomposition(phy_elem_str, xml_activity_list, xml_consumer_activity_list,
                                xml_producer_activity_list, xml_phy_elem_list, xml_attribute_list, xml_phy_inter_list):
    """@ingroup diagram
    @anchor show_phy_elem_decomposition
    Creates lists with desired objects for physical element decomposition, send them to plantuml_adapter.py
    and returns plantuml text
    @param[in] phy_elem_str: name of the physical element
    @param[in] xml_activity_list: list of all activities
    @param[in] xml_consumer_activity_list: list of [[flow, consumer activity]]
    @param[in] xml_producer_activity_list: list of [[flow, producer activity]]
    @param[in] xml_fun_elem_list: list of all physical elements
    @param[in] xml_attribute_list: list of all attributes
    @param[in] xml_fun_inter_list: list of all physical interfaces
    @return plantuml text
    """
    plantuml_text = None

    main_phy_elem = query_object.query_object_by_name(phy_elem_str, **{XML_DICT_KEY_4_PHY_ELEM_LIST: xml_phy_elem_list})
    if not main_phy_elem:
        return plantuml_text

    main_phy_elem.parent = None

    allocated_activity_list = set()
    if main_phy_elem.child_list != set():
        util.get_level_0_activity(main_phy_elem, xml_activity_list, allocated_activity_list)

    if allocated_activity_list != set():
        external_activity_list, new_consumer_list, new_producer_list = \
            util.get_cons_prod_from_allocated_elements(
                allocated_activity_list,
                xml_producer_activity_list,
                xml_consumer_activity_list)

        if not allocated_activity_list:
            xml_phy_elem_list = set()
            xml_phy_elem_list.add(main_phy_elem)
            for child in main_phy_elem.child_list:
                xml_phy_elem_list.add(child)
        # Else do nothing
    else:
        external_activity_list, xml_phy_elem_list = set(), set()
        new_consumer_list, new_producer_list = [], []

    Logger.set_debug(__name__, f'list of allocated activities: {allocated_activity_list}')
    Logger.set_debug(__name__, f'list of external activities: {external_activity_list}')
    Logger.set_debug(__name__, f'list of consumer list: {new_consumer_list}')
    Logger.set_debug(__name__, f'list of producer list: {new_producer_list}')

    plantuml_text = plantuml_adapter.get_phy_elem_decomposition(main_phy_elem,
                                                                xml_phy_elem_list,
                                                                allocated_activity_list,
                                                                new_consumer_list,
                                                                new_producer_list,
                                                                external_activity_list,
                                                                xml_attribute_list,
                                                                xml_phy_inter_list)
    Logger.set_info(__name__,
                    f"Decomposition Diagram for {phy_elem_str} generated")

    return plantuml_text

