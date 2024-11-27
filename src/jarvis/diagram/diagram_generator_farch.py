"""@defgroup diagram
Jarvis diagram module
"""
# Libraries

# Modules
import plantuml_adapter
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_ATTRIBUTE_LIST, XML_DICT_KEY_11_VIEW_LIST, \
    XML_DICT_KEY_12_TYPE_LIST, XML_DICT_KEY_13_FUN_CONS_LIST, XML_DICT_KEY_14_FUN_PROD_LIST
from jarvis.query import query_object
from . import util
from tools import Logger


def show_fun_elem_function(fun_elem_str, xml_fun_elem_list, xml_function_list,
                           xml_consumer_function_list, xml_producer_function_list, xml_attribute_list):
    """@ingroup diagram
    @anchor show_fun_elem_function
    Creates lists with desired objects for functional element functions allocation, send them to plantuml_adapter.py
    and returns plantuml text
    @param[in] fun_elem_str: name of the functional element
    @param[in] xml_fun_elem_list: list of all functional elements
    @param[in] xml_function_list: list of all functions
    @param[in] xml_consumer_function_list: list of [[flow name, consumer function]]
    @param[in] xml_producer_function_list: list of [[flow name, producer function]]
    @param[in] xml_attribute_list: list of all attributes
    @return plantuml text
    """
    plantuml_text = None

    main_fun_elem = query_object.query_object_by_name(fun_elem_str, **{XML_DICT_KEY_2_FUN_ELEM_LIST: xml_fun_elem_list})
    if not main_fun_elem:
        return plantuml_text

    if not main_fun_elem.allocated_function_list:
        Logger.set_info(__name__,
                        f"No function allocated to {main_fun_elem.name} (no display)")
        return plantuml_text

    main_fun_elem.parent = None
    main_fun_elem.child_list.clear()

    # Get allocated main function to main_fun_elem
    new_function_list = {f for f in xml_function_list
                         if f.id in main_fun_elem.allocated_function_list and f.parent is None}

    if not new_function_list:
        Logger.set_info(__name__,
                        f"No main function allocated to {main_fun_elem.name} (no display)")
        return plantuml_text

    external_function_list, new_consumer_list, new_producer_list = \
        util.get_cons_prod_from_allocated_functions(new_function_list,
                                                    xml_producer_function_list,
                                                    xml_consumer_function_list,
                                                    False)

    Logger.set_debug(__name__, f'list of allocated functions to element: {new_function_list}')
    Logger.set_debug(__name__, f'list of external functions to element: {external_function_list}')
    Logger.set_debug(__name__, f'list of consumer list: {new_consumer_list}')
    Logger.set_debug(__name__, f'list of producer list: {new_producer_list}')

    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=new_function_list,
                                                           fun_elem_list=None,
                                                           consumer_function_list=new_consumer_list,
                                                           producer_function_list=new_producer_list,
                                                           parent_child_dict={},
                                                           data_list=None,
                                                           xml_type_list=None,
                                                           xml_attribute_list=xml_attribute_list)

    Logger.set_info(__name__,
                    f"Function Diagram for {fun_elem_str} generated")

    return plantuml_text


def show_fun_elem_context(fun_elem_str, xml_fun_elem_list, xml_function_list,
                          xml_consumer_function_list, xml_producer_function_list,
                          xml_attribute_list, xml_fun_inter_list, xml_data_list):
    """@ingroup diagram
    @anchor show_fun_elem_context
    Creates lists with desired objects for functional element context, send them to plantuml_adapter.py
    and returns plantuml text
    @param[in] fun_elem_str: name of the functional element
    @param[in] xml_fun_elem_list: list of all functional elements
    @param[in] xml_function_list: list of all functions
    @param[in] xml_consumer_function_list: list of [[flow name, consumer function]]
    @param[in] xml_producer_function_list: list of [[flow name, producer function]]
    @param[in] xml_attribute_list: list of all attributes
    @param[in] xml_fun_inter_list: list of all functional interfaces
    @param[in] xml_data_list: list of all data
    @return plantuml text
    """
    plantuml_text = None

    main_fun_elem = query_object.query_object_by_name(fun_elem_str, **{XML_DICT_KEY_2_FUN_ELEM_LIST: xml_fun_elem_list})
    if not main_fun_elem:
        return plantuml_text

    # Get allocated main function to main_fun_elem
    allocated_function_list = set()
    for xml_function in xml_function_list:
        if xml_function.id in main_fun_elem.allocated_function_list:
            if xml_function.parent is None:
                allocated_function_list.add(xml_function)
            elif main_fun_elem.parent is not None:
                if xml_function.id in main_fun_elem.parent.allocated_function_list:
                    allocated_function_list.add(xml_function)
                # Else do nothing
            # Else do nothing

    new_function_list, new_consumer_list, new_producer_list = util.get_allocated_function_context_lists(
        allocated_function_list,
        xml_consumer_function_list,
        xml_producer_function_list)

    Logger.set_debug(__name__, f'list of functions: {new_function_list}')
    Logger.set_debug(__name__, f'list of consumer list: {new_consumer_list}')
    Logger.set_debug(__name__, f'list of producer list: {new_producer_list}')

    # TODO : fun_elem_inter_list to be removed (not used anymore)
    fun_elem_list, interface_list, fun_elem_inter_list = util.get_fun_inter_for_fun_elem_context(
        main_fun_elem, xml_fun_inter_list, xml_fun_elem_list)

    Logger.set_debug(__name__, f'list of functional element: {fun_elem_list}')
    Logger.set_debug(__name__, f'list of functional interfaces: {interface_list}')

    for fun in new_function_list:
        for elem in xml_fun_elem_list:
            if any(z == fun.id for z in elem.allocated_function_list) and elem not in fun_elem_list:
                fun_elem_list.add(elem)

    for elem in fun_elem_list.copy():
        for str_id in elem.allocated_function_list.copy():
            if str_id not in [i.id for i in new_function_list]:
                elem.allocated_function_list.remove(str_id)

    # Remove parent for main functional element : we do not care about it in context diagram
    if main_fun_elem.parent:
        if main_fun_elem.parent in fun_elem_list:
            fun_elem_list.remove(main_fun_elem.parent)
        # Else do nothing
        main_fun_elem.parent = None

    plantuml_text = plantuml_adapter.get_fun_elem_context_diagram(new_function_list,
                                                                  new_consumer_list,
                                                                  new_producer_list,
                                                                  xml_data_list,
                                                                  xml_attribute_list,
                                                                  fun_elem_list,
                                                                  interface_list)

    Logger.set_info(__name__,
                    f"Context Diagram for {fun_elem_str} generated")

    return plantuml_text


def show_fun_elem_decomposition(fun_elem_str, xml_function_list, xml_consumer_function_list,
                                xml_producer_function_list, xml_fun_elem_list, xml_attribute_list,
                                xml_data_list, xml_fun_inter_list, diagram_level=None):
    """@ingroup diagram
    @anchor show_fun_elem_decomposition
    Creates lists with desired objects for functional element decomposition, send them to plantuml_adapter.py
    and returns plantuml text
    @param[in] fun_elem_str: name of the functional element
    @param[in] xml_fun_elem_list: list of all functional elements
    @param[in] xml_function_list: list of all functions
    @param[in] xml_consumer_function_list: list of [[flow name, consumer function]]
    @param[in] xml_producer_function_list: list of [[flow name, producer function]]
    @param[in] xml_attribute_list: list of all attributes
    @param[in] xml_fun_inter_list: list of all functional interfaces
    @param[in] xml_data_list: list of all data
    @return plantuml text
    """
    plantuml_text = None

    main_fun_elem = query_object.query_object_by_name(fun_elem_str, **{XML_DICT_KEY_2_FUN_ELEM_LIST: xml_fun_elem_list})
    if not main_fun_elem:
        return plantuml_text

    main_fun_elem.parent = None

    if diagram_level:
        xml_function_list, xml_fun_elem_list = util.filter_fun_elem_with_level(main_fun_elem,
                                                                               diagram_level,
                                                                               xml_function_list,
                                                                               xml_fun_elem_list)

    allocated_function_list = set()
    if main_fun_elem.child_list != set():
        util.get_level_0_function(main_fun_elem, xml_function_list, allocated_function_list)

    if allocated_function_list != set():
        external_function_list, new_consumer_list, new_producer_list = \
            util.get_cons_prod_from_allocated_functions(
                allocated_function_list,
                xml_producer_function_list,
                xml_consumer_function_list)

        if external_function_list:
            for fun in external_function_list:
                for child in fun.child_list.copy():
                    if not any(t == child for t in external_function_list):
                        fun.child_list.remove(child)
        else:
            xml_fun_elem_list = set()
            xml_fun_elem_list.add(main_fun_elem)
            for child in main_fun_elem.child_list:
                xml_fun_elem_list.add(child)
    else:
        external_function_list, xml_fun_elem_list = set(), set()
        new_consumer_list, new_producer_list = [], []

    Logger.set_debug(__name__, f'list of allocated functions: {allocated_function_list}')
    Logger.set_debug(__name__, f'list of external functions: {external_function_list}')
    Logger.set_debug(__name__, f'list of consumer list: {new_consumer_list}')
    Logger.set_debug(__name__, f'list of producer list: {new_producer_list}')
    Logger.set_debug(__name__, f'list of functional interfaces: {xml_fun_inter_list}')

    plantuml_text = plantuml_adapter.get_fun_elem_decomposition(main_fun_elem, xml_fun_elem_list,
                                                                allocated_function_list,
                                                                new_consumer_list,
                                                                new_producer_list,
                                                                external_function_list,
                                                                xml_attribute_list,
                                                                xml_data_list,
                                                                xml_fun_inter_list)
    Logger.set_info(__name__,
                    f"Decomposition Diagram for {fun_elem_str} generated")

    return plantuml_text
