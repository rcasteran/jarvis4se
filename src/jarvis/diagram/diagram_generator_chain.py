"""@defgroup diagram
Jarvis diagram module
"""
# Libraries

# Modules
import plantuml_adapter
from . import util
from tools import Logger


def show_function_chain(function_list_str, xml_function_list, xml_consumer_function_list,
                        xml_producer_function_list, xml_type_list, xml_attribute_list):
    new_function_list = set()
    new_parent_dict = {}
    new_producer_list = []
    new_consumer_list = []

    for i in function_list_str:
        for fun in xml_function_list:
            if i == fun.name or i == fun.alias:
                new_function_list.add(fun)

                util.get_parent_dict(fun, new_function_list, new_parent_dict)

                for xml_consumer_flow, xml_consumer in xml_consumer_function_list:
                    if fun == xml_consumer:
                        fun.child_list.clear()
                        if [xml_consumer_flow, fun] not in new_consumer_list and \
                                [xml_consumer_flow, fun] not in xml_producer_function_list:
                            new_consumer_list.append([xml_consumer_flow, fun])

                for xml_producer_flow, xml_producer in xml_producer_function_list:
                    if fun == xml_producer:
                        fun.child_list.clear()
                        if [xml_producer_flow, fun] not in new_producer_list and \
                                [xml_producer_flow, fun] not in xml_consumer_function_list:
                            new_producer_list.append([xml_producer_flow, fun])

    Logger.set_debug(__name__, f"function list: {new_function_list}")
    Logger.set_debug(__name__, f"consumer function list: {new_consumer_list}")
    Logger.set_debug(__name__, f"producer function list: {new_producer_list}")
    Logger.set_debug(__name__, f"parent list: {new_parent_dict}")

    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=new_function_list,
                                                           fun_elem_list=None,
                                                           consumer_function_list=new_consumer_list,
                                                           producer_function_list=new_producer_list,
                                                           parent_child_dict=new_parent_dict,
                                                           data_list=None,
                                                           xml_type_list=xml_type_list,
                                                           xml_attribute_list=xml_attribute_list)

    Logger.set_info(__name__,
                    f'Chain Diagram {str(", ".join(function_list_str))} generated')

    return plantuml_text


def show_fun_elem_chain(fun_elem_list_str, xml_function_list, xml_consumer_function_list, xml_producer_function_list,
                        xml_fun_elem_list, xml_type_list, xml_attribute_list):
    parent_child_dict = {}

    for i in fun_elem_list_str:
        for fun_elem in xml_fun_elem_list:
            if i == fun_elem.name or i == fun_elem.alias:
                if len(fun_elem.allocated_function_list) > 0:
                    for allocated_function_id in fun_elem.allocated_function_list:
                        parent_child_dict[allocated_function_id] = fun_elem.id

    external_function_list, new_consumer_list, new_producer_list = \
        util.get_cons_prod_from_allocated_functions(xml_function_list,
                                                    xml_producer_function_list,
                                                    xml_consumer_function_list,
                                                    False)

    Logger.set_debug(__name__, f'list of allocated functions to element: {xml_function_list}')
    Logger.set_debug(__name__, f'list of external functions to element: {external_function_list}')
    Logger.set_debug(__name__, f'list of consumer list: {new_consumer_list}')
    Logger.set_debug(__name__, f'list of producer list: {new_producer_list}')

    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=xml_function_list,
                                                           fun_elem_list=xml_fun_elem_list,
                                                           consumer_function_list=new_consumer_list,
                                                           producer_function_list=new_producer_list,
                                                           parent_child_dict=parent_child_dict,
                                                           data_list=None,
                                                           xml_type_list=None,
                                                           xml_attribute_list=xml_attribute_list)

    Logger.set_info(__name__,
                    f'Chain Diagram {str(", ".join(fun_elem_list_str))} generated')

    return plantuml_text
