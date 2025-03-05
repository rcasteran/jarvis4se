"""@defgroup diagram
Jarvis diagram module
"""
# Libraries

# Modules
import datamodel
import plantuml_adapter
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_GOAL_LIST, XML_DICT_KEY_10_ACTIVITY_LIST, XML_DICT_KEY_11_INFORMATION_LIST, XML_DICT_KEY_12_ATTRIBUTE_LIST, \
    XML_DICT_KEY_13_VIEW_LIST, XML_DICT_KEY_14_TYPE_LIST, XML_DICT_KEY_15_FUN_CONS_LIST, \
    XML_DICT_KEY_16_FUN_PROD_LIST, XML_DICT_KEY_17_ACT_CONS_LIST, XML_DICT_KEY_18_ACT_PROD_LIST
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
                                                           activity_list=None,
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


def show_function_context(diagram_function_str, **kwargs):
    xml_function_list = kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
    xml_consumer_function_list = kwargs[XML_DICT_KEY_15_FUN_CONS_LIST]
    xml_producer_function_list = kwargs[XML_DICT_KEY_16_FUN_PROD_LIST]
    xml_data_list = kwargs[XML_DICT_KEY_0_DATA_LIST]

    xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]
    xml_consumer_activity_list = kwargs[XML_DICT_KEY_17_ACT_CONS_LIST]
    xml_producer_activity_list = kwargs[XML_DICT_KEY_18_ACT_PROD_LIST]

    xml_attribute_list = kwargs[XML_DICT_KEY_12_ATTRIBUTE_LIST]
    xml_type_list = kwargs[XML_DICT_KEY_14_TYPE_LIST]

    new_function_list, new_consumer_list, new_producer_list = util.get_function_context_lists(
        diagram_function_str,
        xml_function_list,
        xml_consumer_function_list,
        xml_producer_function_list)

    allocated_activity_list = set()
    parent_child_dict = {}
    for new_function in new_function_list:
        for allocated_activity_id in new_function.allocated_activity_list:
            for xml_activity in xml_activity_list:
                if xml_activity.id == allocated_activity_id:
                    allocated_activity_list.add(xml_activity)
                    parent_child_dict[xml_activity.id] = new_function.id
                # Else do nothing

    new_activity_list, new_activity_consumer_list, new_activity_producer_list = \
        util.get_allocated_function_context_lists(allocated_activity_list,
                                                  xml_consumer_activity_list,
                                                  xml_producer_activity_list)

    for new_activity_consumer in new_activity_consumer_list:
        is_allocated = False
        for new_consumer in new_consumer_list:
            if isinstance(new_consumer[0], datamodel.Data):
                for allocated_info_id in new_consumer[0].allocated_info_list:
                    if new_activity_consumer[0].id == allocated_info_id:
                        is_allocated = True
                        break
                    # Else do nothing
            # Else do nothing

        if not is_allocated:
            for new_producer in new_producer_list:
                if isinstance(new_producer[0], datamodel.Data):
                    for allocated_info_id in new_producer[0].allocated_info_list:
                        if new_activity_consumer[0].id == allocated_info_id:
                            is_allocated = True
                            break
                        # Else do nothing
                # Else do nothing
        # Else do nothing

        if not is_allocated:
            new_consumer_list.append(new_activity_consumer)
        # Else do nothing

    for new_activity_producer in new_activity_producer_list:
        is_allocated = False
        for new_producer in new_producer_list:
            if isinstance(new_producer[0], datamodel.Data):
                for allocated_info_id in new_producer[0].allocated_info_list:
                    if new_activity_producer[0].id == allocated_info_id:
                        is_allocated = True
                        break
                    # Else do nothing
            # Else do nothing

        if not is_allocated:
            for new_consumer in new_consumer_list:
                if isinstance(new_consumer[0], datamodel.Data):
                    for allocated_info_id in new_consumer[0].allocated_info_list:
                        if new_activity_producer[0].id == allocated_info_id:
                            is_allocated = True
                            break
                        # Else do nothing
                # Else do nothing
        # Else do nothing

        if not is_allocated:
            new_producer_list.append(new_activity_producer)
        # Else do nothing

    for new_activity in new_activity_list:
        is_consumer = False
        is_producer = False
        for new_consumer in new_consumer_list:
            if new_activity == new_consumer[1]:
                is_consumer = True
                break
            # Else do nothing

        if not is_consumer:
            for new_producer in new_producer_list:
                if new_activity == new_producer[1]:
                    is_producer = True
                    break
                # Else do nothing
        # Else do nothing

        if is_consumer or is_producer:
            new_function_list.add(new_activity)
        # Else do nothing


    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=new_function_list,
                                                           activity_list=allocated_activity_list,
                                                           fun_elem_list=None,
                                                           consumer_function_list=new_consumer_list,
                                                           producer_function_list=new_producer_list,
                                                           parent_child_dict=parent_child_dict,
                                                           data_list=xml_data_list,
                                                           xml_type_list=xml_type_list,
                                                           xml_attribute_list=xml_attribute_list)

    Logger.set_info(__name__,
                    f"Context Diagram {diagram_function_str} generated")

    return plantuml_text


# TODO: Clean-up once inheritance has been validated (Create method for Function and others
#  objects?)
def show_function_decomposition(diagram_function_str, function_list, consumer_function_list,
                                producer_function_list, diagram_level, **kwargs):
    xml_activity_list = kwargs[XML_DICT_KEY_10_ACTIVITY_LIST]
    xml_consumer_activity_list = kwargs[XML_DICT_KEY_17_ACT_CONS_LIST]
    xml_producer_activity_list = kwargs[XML_DICT_KEY_18_ACT_PROD_LIST]
    xml_attribute_list = kwargs[XML_DICT_KEY_12_ATTRIBUTE_LIST]
    xml_type_list = kwargs[XML_DICT_KEY_14_TYPE_LIST]

    """Create necessary lists then returns plantuml text for decomposition of function"""
    main_fun = query_object.query_object_by_name(diagram_function_str, **{XML_DICT_KEY_1_FUNCTION_LIST: function_list})

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
            for cons in consumer_function_list.copy():
                if k in cons:
                    consumer_function_list.remove([cons[0], k])
                    Logger.set_debug(__name__, f"[{cons[0]}, {k.name} removed]")

            for prod in producer_function_list.copy():
                if k in prod:
                    producer_function_list.remove([prod[0], k])
                    Logger.set_debug(__name__, f"[{prod[0]}, {k.name} removed]")
    else:
        main_function_list, main_parent_dict = query_object.query_object_children_recursively(main_fun)
        # derived = add_inherited_object_children(main_fun)
        # if derived:
        #     main_function_list = main_function_list.union(derived[0])
        #     main_parent_dict.update(derived[1])

    Logger.set_debug(__name__, f"main function list: {main_function_list}")
    Logger.set_debug(__name__, f"consumer function list: {consumer_function_list}")
    Logger.set_debug(__name__, f"producer function list: {producer_function_list}")

    main_consumer_list = util.check_get_flows(main_function_list, consumer_function_list)
    main_producer_list = util.check_get_flows(main_function_list, producer_function_list)

    ext_prod_fun_list, ext_producer_list, ext_prod_parent_dict = util.get_external_flow_with_level(
        main_consumer_list, main_function_list, main_fun, producer_function_list, diagram_level)

    ext_cons_fun_list, ext_consumer_list, ext_cons_parent_dict = util.get_external_flow_with_level(
        main_producer_list, main_function_list, main_fun, consumer_function_list, diagram_level)

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

    allocated_activity_list = set()
    parent_child_dict = {}
    for new_function in new_function_list:
        for allocated_activity_id in new_function.allocated_activity_list:
            for xml_activity in xml_activity_list:
                if xml_activity.id == allocated_activity_id:
                    allocated_activity_list.add(xml_activity)
                    parent_child_dict[xml_activity.id] = new_function.id
                # Else do nothing

    if allocated_activity_list != set():
        new_activity_list, new_activity_consumer_list, new_activity_producer_list = \
            util.get_allocated_function_context_lists(allocated_activity_list,
                                                      xml_consumer_activity_list,
                                                      xml_producer_activity_list)

        for new_activity_consumer in new_activity_consumer_list:
            is_allocated = False
            for new_consumer in new_consumer_list:
                if isinstance(new_consumer[0], datamodel.Data):
                    for allocated_info_id in new_consumer[0].allocated_info_list:
                        if new_activity_consumer[0].id == allocated_info_id:
                            is_allocated = True
                            break
                        # Else do nothing
                # Else do nothing

            if not is_allocated:
                for new_producer in new_producer_list:
                    if isinstance(new_producer[0], datamodel.Data):
                        for allocated_info_id in new_producer[0].allocated_info_list:
                            if new_activity_consumer[0].id == allocated_info_id:
                                is_allocated = True
                                break
                            # Else do nothing
                    # Else do nothing
            # Else do nothing

            if not is_allocated:
                new_consumer_list.append(new_activity_consumer)
            # Else do nothing

        for new_activity_producer in new_activity_producer_list:
            is_allocated = False
            for new_producer in new_producer_list:
                if isinstance(new_producer[0], datamodel.Data):
                    for allocated_info_id in new_producer[0].allocated_info_list:
                        if new_activity_producer[0].id == allocated_info_id:
                            is_allocated = True
                            break
                        # Else do nothing
                # Else do nothing

            if not is_allocated:
                for new_consumer in new_consumer_list:
                    if isinstance(new_consumer[0], datamodel.Data):
                        for allocated_info_id in new_consumer[0].allocated_info_list:
                            if new_activity_producer[0].id == allocated_info_id:
                                is_allocated = True
                                break
                            # Else do nothing
                    # Else do nothing
            # Else do nothing

            if not is_allocated:
                new_producer_list.append(new_activity_producer)
            # Else do nothing

        for new_activity in new_activity_list:
            is_allocated = False
            for allocated_activity in allocated_activity_list:
                if new_activity == allocated_activity:
                    is_allocated = True
                    break
                # Else do nothing

            if not is_allocated:
                is_consumer = False
                is_producer = False
                for new_consumer in new_consumer_list:
                    if new_activity == new_consumer[1]:
                        is_consumer = True
                        break
                    # Else do nothing

                if not is_consumer:
                    for new_producer in new_producer_list:
                        if new_activity == new_producer[1]:
                            is_producer = True
                            break
                        # Else do nothing
                # Else do nothing

                if is_consumer or is_producer:
                    new_function_list.add(new_activity)
                # Else do nothing
            # Else do nothing
    # Else do nothing

    plantuml_text = plantuml_adapter.get_function_diagrams(function_list=new_function_list,
                                                           activity_list=allocated_activity_list,
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
