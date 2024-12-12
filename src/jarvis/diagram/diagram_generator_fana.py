"""@defgroup diagram
Jarvis diagram module
"""
# Libraries

# Modules
import plantuml_adapter
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_INFORMATION_LIST, XML_DICT_KEY_11_ATTRIBUTE_LIST, \
    XML_DICT_KEY_12_VIEW_LIST, XML_DICT_KEY_13_TYPE_LIST, XML_DICT_KEY_14_FUN_CONS_LIST, \
    XML_DICT_KEY_15_FUN_PROD_LIST, XML_DICT_KEY_16_ACT_CONS_LIST, XML_DICT_KEY_17_ACT_PROD_LIST
from jarvis.query import query_object
from . import util
from tools import Logger


def show_activity_context(diagram_activity_str, xml_activity_list, xml_consumer_activity_list,
                          xml_producer_activity_list, xml_information_list, xml_attribute_list,
                          xml_type_list):

    new_function_list, new_consumer_list, new_producer_list = util.get_function_context_lists(
        diagram_activity_str,
        xml_activity_list,
        xml_consumer_activity_list,
        xml_producer_activity_list)

    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=new_function_list,
                                                           fun_elem_list=None,
                                                           consumer_function_list=new_consumer_list,
                                                           producer_function_list=new_producer_list,
                                                           parent_child_dict={},
                                                           data_list=xml_information_list,
                                                           xml_type_list=xml_type_list,
                                                           xml_attribute_list=xml_attribute_list)

    Logger.set_info(__name__,
                    f"Context Diagram {diagram_activity_str} generated")

    return plantuml_text


def show_function_context(diagram_function_str, xml_function_list, xml_consumer_function_list,
                          xml_producer_function_list, xml_data_list, xml_attribute_list,
                          xml_type_list):

    new_function_list, new_consumer_list, new_producer_list = util.get_function_context_lists(
        diagram_function_str,
        xml_function_list,
        xml_consumer_function_list,
        xml_producer_function_list)

    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=new_function_list,
                                                           fun_elem_list=None,
                                                           consumer_function_list=new_consumer_list,
                                                           producer_function_list=new_producer_list,
                                                           parent_child_dict={},
                                                           data_list=xml_data_list,
                                                           xml_type_list=xml_type_list,
                                                           xml_attribute_list=xml_attribute_list)

    Logger.set_info(__name__,
                    f"Context Diagram {diagram_function_str} generated")

    return plantuml_text


# TODO: Clean-up once inheritance has been validated (Create method for Function and others
#  objects?)
def show_function_decomposition(diagram_function_str, xml_function_list, xml_consumer_function_list,
                                xml_producer_function_list, xml_attribute_list, xml_type_list,
                                diagram_level=None):
    """Create necessary lists then returns plantuml text for decomposition of function"""
    main_fun = query_object.query_object_by_name(diagram_function_str, **{XML_DICT_KEY_1_FUNCTION_LIST: xml_function_list})

    if not main_fun:
        return

    main_parent = main_fun.parent

    if diagram_level:
        full_fun_list, _ = query_object.query_object_children_recursively(main_fun)
        main_function_list, main_parent_dict = \
            query_object.query_object_children_recursively(main_fun,
                                                           None,
                                                           None,
                                                           None,
                                                           diagram_level)
        # derived = add_inherited_object_children(main_fun, level=diagram_level)
        # if derived:
        #     main_function_list = main_function_list.union(derived[0])
        #     main_parent_dict.update(derived[1])

        # Remove functions and flows that are not in the diagram level
        for k in full_fun_list.symmetric_difference(main_function_list):
            Logger.set_debug(__name__, f"{k.name} not in diagram level {diagram_level}")
            for cons in xml_consumer_function_list.copy():
                if k in cons:
                    xml_consumer_function_list.remove([cons[0], k])
                    Logger.set_debug(__name__, f"[{cons[0]}, {k.name} removed]")

            for prod in xml_producer_function_list.copy():
                if k in prod:
                    xml_producer_function_list.remove([prod[0], k])
                    Logger.set_debug(__name__, f"[{prod[0]}, {k.name} removed]")
    else:
        main_function_list, main_parent_dict = query_object.query_object_children_recursively(main_fun)
        # derived = add_inherited_object_children(main_fun)
        # if derived:
        #     main_function_list = main_function_list.union(derived[0])
        #     main_parent_dict.update(derived[1])

    Logger.set_debug(__name__, f"main function list: {main_function_list}")
    Logger.set_debug(__name__, f"consumer function list: {xml_consumer_function_list}")
    Logger.set_debug(__name__, f"producer function list: {xml_producer_function_list}")

    main_consumer_list = util.check_get_flows(main_function_list, xml_consumer_function_list)
    main_producer_list = util.check_get_flows(main_function_list, xml_producer_function_list)

    ext_prod_fun_list, ext_producer_list, ext_prod_parent_dict = util.get_external_flow_with_level(
        main_consumer_list, main_function_list, main_fun, xml_producer_function_list, diagram_level)

    ext_cons_fun_list, ext_consumer_list, ext_cons_parent_dict = util.get_external_flow_with_level(
        main_producer_list, main_function_list, main_fun, xml_consumer_function_list, diagram_level)

    new_function_list = main_function_list.union(ext_prod_fun_list).union(ext_cons_fun_list)
    new_consumer_list = main_consumer_list + ext_consumer_list
    new_producer_list = main_producer_list + ext_producer_list
    new_parent_dict = {**main_parent_dict, **ext_cons_parent_dict, **ext_prod_parent_dict}

    for function in new_function_list:
        if main_parent and function.parent is main_parent:
            function.parent = None
        if function.child_list:
            for j in function.child_list.copy():
                if j not in new_function_list:
                    function.child_list.remove(j)

    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=new_function_list,
                                                           fun_elem_list=None,
                                                           consumer_function_list=new_consumer_list,
                                                           producer_function_list=new_producer_list,
                                                           parent_child_dict=new_parent_dict,
                                                           data_list=None,
                                                           xml_type_list=xml_type_list,
                                                           xml_attribute_list=xml_attribute_list)

    Logger.set_info(__name__,
                    f"Decomposition Diagram {diagram_function_str} generated")

    return plantuml_text
