"""@defgroup diagram
Jarvis diagram module
"""
# Libraries

# Modules
import plantuml_adapter
from jarvis import question_answer
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

    main_fun_elem = question_answer.check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
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

    main_fun_elem = question_answer.check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
    if not main_fun_elem:
        return plantuml_text

    # Get allocated main function to main_fun_elem
    allocated_function_list = {f for f in xml_function_list
                               if f.id in main_fun_elem.allocated_function_list and f.parent is None}

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
        if any(a == elem for a in main_fun_elem.child_list):
            fun_elem_list.remove(elem)

    # Remove parent for main functional element : we do not care about it in context diagram
    if main_fun_elem.parent:
        fun_elem_list.remove(main_fun_elem.parent)

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
    @anchor show_fun_elem_context
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

    main_fun_elem = question_answer.check_get_object(fun_elem_str, **{'xml_fun_elem_list': xml_fun_elem_list})
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

        for fun in external_function_list:
            for child in fun.child_list.copy():
                if not any(t == child for t in external_function_list):
                    fun.child_list.remove(child)
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
