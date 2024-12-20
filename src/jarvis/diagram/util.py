"""@defgroup diagram
Jarvis diagram module
"""
# Modules
from jarvis.query import question_answer, query_object
from tools import Logger


def get_cons_or_prod_paired(function_list, xml_flow_list, xml_opposite_flow_list):
    """Get flow list if opposite flow is existing: e.g. if flow A is consumed and produced by
    function within function_list => Add it"""
    new_flow_list = []

    for func in function_list:
        # Flow = [Data, Function]
        for flow in xml_flow_list:
            if func in flow and flow not in new_flow_list:
                # Oppo = [Data, Function]
                for oppo in xml_opposite_flow_list:
                    if oppo[0] == flow[0] and oppo[1] in function_list:
                        new_flow_list.append(flow)
                        break

    return new_flow_list


def get_cons_prod_from_allocated_elements(allocated_elem_list,
                                          xml_producer_elem_list,
                                          xml_consumer_elem_list,
                                          with_external_elements=True):
    """Get consumers/producers from function's allocated to main_fun_elem (and its descendant)"""
    new_producer_list = []
    new_consumer_list = []
    for allocated_elem in allocated_elem_list:
        if hasattr(allocated_elem, "child_list"):
            allocated_elem.child_list.clear()
        # Else do nothing

        allocated_elem.parent = None

        for xml_producer_elem in xml_producer_elem_list:
            if allocated_elem in xml_producer_elem:
                new_producer_list.append(xml_producer_elem)
            # Else do nothing

        for xml_consumer_elem in xml_consumer_elem_list:
            if allocated_elem in xml_consumer_elem:
                new_consumer_list.append(xml_consumer_elem)
            # Else do nothing

    if with_external_elements:
        external_elem_list, new_consumer_list, new_producer_list = get_ext_cons_prod(
            new_producer_list,
            new_consumer_list,
            xml_producer_elem_list,
            xml_consumer_elem_list)
    else:
        external_elem_list = None

    return external_elem_list, new_consumer_list, new_producer_list


def get_ext_cons_prod(producer_list, consumer_list, xml_producer_elem_list,
                      xml_consumer_elem_list):
    """Get external cons/prod associated to considered element"""
    external_elem_list = set()
    for elem in consumer_list:
        if not any(elem[0] in s for s in producer_list):
            for prod in xml_producer_elem_list:
                if prod[0] == elem[0] and prod[1].parent is None:
                    external_elem_list.add(prod[1])
                    if prod not in producer_list:
                        producer_list.append(prod)

    for elem in producer_list:
        if not any(elem[0] in s for s in consumer_list):
            for cons in xml_consumer_elem_list:
                if cons[0] == elem[0] and cons[1].parent is None:
                    external_elem_list.add(cons[1])
                    if cons not in consumer_list:
                        consumer_list.append(cons)

    return external_elem_list, consumer_list, producer_list


def get_allocated_function_context_lists(allocated_function_list,
                                         xml_consumer_function_list,
                                         xml_producer_function_list):
    """For each function within allocated_function_list, asks the context of the function then
    adds returned list from show_function_context() to current lists"""
    new_function_list = set()
    new_consumer_list = []
    new_producer_list = []

    for fun in allocated_function_list:
        fun_function_list, fun_consumer_list, fun_producer_list = get_function_context_lists(
            fun.name,
            allocated_function_list,
            xml_consumer_function_list,
            xml_producer_function_list)

        for fun_function in fun_function_list:
            new_function_list.add(fun_function)

        for fun_consumer in fun_consumer_list:
            if fun_consumer not in new_consumer_list:
                new_consumer_list.append(fun_consumer)

        for fun_producer in fun_producer_list:
            if fun_producer not in new_producer_list:
                new_producer_list.append(fun_producer)

    return new_function_list, new_consumer_list, new_producer_list


def get_function_context_lists(diagram_function_str, xml_function_list, xml_consumer_function_list,
                               xml_producer_function_list):
    """Create necessary lists then returns plantuml text for context of function"""
    new_function_list = set()
    new_producer_list = []
    new_consumer_list = []
    main_function = None

    for xml_function in xml_function_list:
        if diagram_function_str in (xml_function.name, xml_function.alias):
            main_function = xml_function
            new_function_list.add(xml_function)
            break
        # Else do nothing

    if main_function is not None:
        for xml_producer_flow, xml_producer_function in xml_producer_function_list:
            if xml_producer_function == main_function:
                check = False
                for xml_consumer_flow, xml_consumer_function in xml_consumer_function_list:
                    if xml_producer_flow == xml_consumer_flow:
                        if xml_consumer_function.parent is None:
                            xml_function_children_list, _ = \
                                query_object.query_object_children_recursively(main_function)
                            parent_check = \
                                query_object.query_object_is_parent_recursively(xml_consumer_function,
                                                                                main_function)
                            if xml_consumer_function not in xml_function_children_list and parent_check is False:
                                new_consumer_list.append([xml_producer_flow, xml_consumer_function])
                                new_function_list.add(xml_consumer_function)
                                check = True
                            # ELse do nothing
                        elif main_function.parent == xml_consumer_function.parent and \
                                xml_consumer_function != main_function:
                            new_consumer_list.append([xml_consumer_flow, xml_consumer_function])
                            new_function_list.add(xml_consumer_function)
                            check = True
                        elif xml_consumer_function != main_function:
                            if len(xml_consumer_function.child_list) == 0:
                                new_consumer_list.append([xml_consumer_flow, xml_consumer_function])
                                new_function_list.add(xml_consumer_function)
                            # Else do nothing
                            check = True

                if check:
                    if [xml_producer_flow, xml_producer_function] not in new_producer_list:
                        new_producer_list.append([xml_producer_flow, xml_producer_function])

                if not any(xml_producer_flow in s for s in xml_consumer_function_list):
                    if [xml_producer_flow, xml_producer_function] not in new_producer_list:
                        new_producer_list.append([xml_producer_flow, xml_producer_function])

        for xml_consumer_flow, xml_consumer_function in xml_consumer_function_list:
            if xml_consumer_function == main_function:
                check = False
                for xml_producer_flow, xml_producer_function in xml_producer_function_list:
                    if xml_producer_flow == xml_consumer_flow:
                        if xml_producer_function.parent is None:
                            xml_function_children_list, _ = \
                                query_object.query_object_children_recursively(main_function)
                            parent_check = \
                                query_object.query_object_is_parent_recursively(xml_producer_function,
                                                                                main_function)
                            if xml_producer_function not in xml_function_children_list and parent_check is False:
                                new_producer_list.append([xml_producer_flow, xml_producer_function])
                                new_function_list.add(xml_producer_function)
                                check = True
                            # ELse do nothing
                        elif main_function.parent == xml_producer_function.parent and\
                                xml_producer_function != main_function:
                            new_producer_list.append([xml_producer_flow, xml_producer_function])
                            new_function_list.add(xml_producer_function)
                            check = True
                        elif xml_producer_function != main_function:
                            if len(xml_producer_function.child_list) == 0:
                                new_producer_list.append([xml_producer_flow, xml_producer_function])
                                new_function_list.add(xml_producer_function)
                            # Else do nothing
                            check = True

                if check:
                    if [xml_consumer_flow, xml_consumer_function] not in new_consumer_list:
                        new_consumer_list.append([xml_consumer_flow, xml_consumer_function])

                if not any(xml_consumer_flow in s for s in xml_producer_function_list):
                    if [xml_consumer_flow, xml_consumer_function] not in new_consumer_list:
                        new_consumer_list.append([xml_consumer_flow, xml_consumer_function])

        for f in new_function_list:
            f.child_list.clear()
    # Else do nothing

    return new_function_list, new_consumer_list, new_producer_list


def get_fun_inter_for_fun_elem_context(main_fun_elem, xml_fun_inter_list, xml_fun_elem_list):
    """Get functional interfaces and associated functional elements"""
    fun_elem_list = set()
    interface_list = set()
    fun_elem_inter_list = []

    # Add main_fun_elem to filtered fun_elem_list and remove it from xml_fun_elem_list
    fun_elem_list.add(main_fun_elem)
    xml_fun_elem_list.remove(main_fun_elem)

    # Get exposed interfaces of fun_elem
    for interface in xml_fun_inter_list:
        if any(i == interface.id for i in main_fun_elem.exposed_interface_list):
            interface_list.add(interface)

    # Get fun_elem pair for fun_inter
    for fun_inter in interface_list:
        for fun_elem in xml_fun_elem_list:
            if any(i == fun_inter.id for i in fun_elem.exposed_interface_list):
                if check_is_highest_fun_elem_exposing_fun_inter(fun_inter, fun_elem) and \
                        query_object.query_object_is_not_family(main_fun_elem, fun_elem):
                    fun_elem_list.add(fun_elem)
                    if [main_fun_elem, fun_elem, fun_inter] not in fun_elem_inter_list:
                        fun_elem_inter_list.append([main_fun_elem, fun_elem, fun_inter])

    return fun_elem_list, interface_list, fun_elem_inter_list


def check_is_highest_fun_elem_exposing_fun_inter(fun_inter, fun_elem):
    """Returns True if it's highest fun_elem exposing fun_inter"""
    check = False
    if not fun_elem.parent:
        check = True
    elif not any(a == fun_inter.id for a in fun_elem.parent.exposed_interface_list):
        check = True

    return check


def filter_fun_elem_with_level(main_fun_elem, diagram_level, xml_function_list, xml_fun_elem_list):
    """Clean unwanted fun_elem and functions from xml_lists then returns them"""
    main_fun_elem_list, _ = query_object.query_object_children_recursively(main_fun_elem,
                                                                           None,
                                                                           None,
                                                                           None,
                                                                           diagram_level)
    # Remove (child) elements from xml lists that are below the level asked
    for unwanted_fun_elem in xml_fun_elem_list.symmetric_difference(main_fun_elem_list):
        if not query_object.query_object_is_not_family(unwanted_fun_elem, main_fun_elem):
            for fun in xml_function_list.copy():
                if fun.id in unwanted_fun_elem.allocated_function_list:
                    xml_function_list.remove(fun)
            xml_fun_elem_list.remove(unwanted_fun_elem)
    # Remove (child) elements from external fun_elem (main_fun_elem point of view)
    for unwanted_fun_elem in xml_fun_elem_list.symmetric_difference(main_fun_elem_list):
        if query_object.query_object_is_not_family(unwanted_fun_elem, main_fun_elem) and \
                unwanted_fun_elem.parent is None:
            curr_fun_elem_list, _ = query_object.query_object_children_recursively(unwanted_fun_elem,
                                                                                   None,
                                                                                   None,
                                                                                   None,
                                                                                   diagram_level)
            for un_fun_elem in xml_fun_elem_list.symmetric_difference(curr_fun_elem_list):
                if not query_object.query_object_is_not_family(unwanted_fun_elem, un_fun_elem):
                    xml_fun_elem_list.remove(un_fun_elem)

    return xml_function_list, xml_fun_elem_list


def get_level_0_function(fun_elem, function_list, level_0_function_list):
    """Recursively get functions allocated to fun_elem and its descendant"""
    for function_id in fun_elem.allocated_function_list:
        for function in function_list:
            if function.id == function_id and function not in level_0_function_list:
                if fun_elem.child_list == set() is True:
                    level_0_function_list.add(function)
                else:
                    # Check if any function child is allocated to any element child
                    function_child_id_list = [elem.id for elem in function.child_list]
                    allocated_function_id_list = []
                    for fun_elem_child in fun_elem.child_list:
                        for allocated_function_id in fun_elem_child.allocated_function_list:
                            allocated_function_id_list.append(allocated_function_id)

                    if not any(fid in function_child_id_list for fid in allocated_function_id_list):
                        # Check function parent
                        if function.parent is None:
                            level_0_function_list.add(function)
                        else:
                            if function.parent.id not in fun_elem.allocated_function_list:
                                level_0_function_list.add(function)

    for child in fun_elem.child_list:
        get_level_0_function(child, function_list, level_0_function_list)


def get_level_0_activity(phy_elem, activity_list, level_0_activity_list):
    """Recursively get activities allocated to phy_elem and its descendant"""
    for activity_id in phy_elem.allocated_activity_list:
        for activity in activity_list:
            if activity.id == activity_id and activity not in level_0_activity_list:
                level_0_activity_list.add(activity)
            # Else do nothing

    for child in phy_elem.child_list:
        get_level_0_activity(child, activity_list, level_0_activity_list)


def get_object_list_from_view(obj_str, xml_obj_list, xml_view_list):
    """Returns current object's list by checking view"""
    filtered_item_list = filter_allocated_item_from_view(xml_obj_list, xml_view_list)

    if len(xml_obj_list) == len(filtered_item_list):
        return xml_obj_list

    if isinstance(obj_str, str):
        for obj in xml_obj_list:
            if obj_str in (obj.name, obj.alias) and not any(item == obj for item in filtered_item_list):
                filtered_item_list.append(obj)
    elif isinstance(obj_str, list):
        for object_name in obj_str:
            for obj in xml_obj_list:
                if object_name in (obj.name, obj.alias) and \
                        not any(item == obj for item in filtered_item_list):
                    filtered_item_list.append(obj)

    for new_obj in filtered_item_list:
        if hasattr(new_obj, "child_list"):
            child_list = set()
            for child in new_obj.child_list:
                if child in filtered_item_list:
                    child_list.add(child)
            new_obj.child_list.clear()
            new_obj.child_list = child_list
        # Else do nothing

    return filtered_item_list


def filter_allocated_item_from_view(xml_item_list, xml_view_list):
    """For a type of item from xml, check if a View is activated and if the item is in its
    allocated item's list"""
    if any(j.activated for j in xml_view_list):
        filtered_item_list = []
        activated_view_name = ''
        for view in xml_view_list:
            if view.activated:
                activated_view_name = view.name
                for item in xml_item_list:
                    if item.id in view.allocated_item_list:
                        filtered_item_list.append(item)
                break
            # Else do nothing
    else:
        filtered_item_list = xml_item_list

    return filtered_item_list


def check_get_flows(function_list, xml_flow_list):
    """Get flow_list associated with function_list and xml_flow_list"""
    new_flow_list = []

    for function in function_list:
        for xml_flow, xml_function in xml_flow_list:
            if function == xml_function:
                if [xml_flow, xml_function] not in new_flow_list:
                    new_flow_list.append([xml_flow, xml_function])

    for xml_flow, xml_function in new_flow_list.copy():
        if [xml_flow, xml_function.parent] in new_flow_list:
            new_flow_list.remove([xml_flow, xml_function.parent])

    return new_flow_list


def get_external_flow_with_level(main_flow_list, main_function_list, main_fun, xml_flow_list,
                                 level):
    """Returns external functions list, flow lists and parent dict"""
    ext_flow_fun_list = set()
    ext_flow_list = []
    ext_flow_parent_dict = {}
    for flow, _ in main_flow_list:
        for xml_flow, xml_fun in xml_flow_list:
            if flow == xml_flow and xml_fun.parent == main_fun.parent:
                ext_flow_fun_list.add(xml_fun)
            elif flow == xml_flow and query_object.query_object_is_not_family(main_fun, xml_fun) and \
                    xml_fun.parent is None:
                ext_flow_fun_list.add(xml_fun)
            elif flow == xml_flow and not query_object.query_object_is_parent_recursively(xml_fun, main_fun) \
                    and [xml_flow, xml_fun.parent] not in xml_flow_list:
                ext_flow_fun_list.add(xml_fun)

    for fun in ext_flow_fun_list.copy():
        if fun.child_list:
            function_list_dict = query_object.query_object_children_recursively(fun,
                                                                                None,
                                                                                None,
                                                                                None,
                                                                                level)
            ext_flow_fun_list.update(function_list_dict[0])
            ext_flow_parent_dict.update(function_list_dict[1])

    for flow, _ in main_flow_list:
        for xml_flow, xml_fun in xml_flow_list:
            if flow == xml_flow and xml_fun in ext_flow_fun_list and \
                    xml_fun not in main_function_list:
                # ext_flow_list.append([xml_flow, xml_fun])
                if not xml_fun.child_list:
                    if [xml_flow, xml_fun] not in ext_flow_list:
                        ext_flow_list.append([xml_flow, xml_fun])
                else:
                    temp = []
                    for k in xml_fun.child_list:
                        temp.append([xml_flow, k])
                    if not any(t in temp for t in xml_flow_list):
                        if [xml_flow, xml_fun] not in ext_flow_list:
                            ext_flow_list.append([xml_flow, xml_fun])

    for fun in ext_flow_fun_list.copy():
        if not any(a == fun for a in [i[1] for i in ext_flow_list]) and not fun.child_list:
            ext_flow_fun_list.remove(fun)

    for fun in ext_flow_fun_list.copy():
        if not any(a == fun for a in [i[1] for i in ext_flow_list]) and \
                not any(i in fun.child_list for i in ext_flow_fun_list) and \
                fun != main_fun:
            ext_flow_fun_list.remove(fun)

    return ext_flow_fun_list, ext_flow_list, ext_flow_parent_dict


def get_cons_prod_from_view_allocated_flow(xml_flow_list, xml_view_list, xml_consumer_elem_list,
                                           xml_producer_elem_list, elem_list):
    """If a view is activated, returns filtered consumer/producer lists"""
    new_elem_list = []
    new_consumer_list = []
    new_producer_list = []
    new_flow_list = filter_allocated_item_from_view(xml_flow_list, xml_view_list)

    if len(new_flow_list) == len(xml_flow_list):
        for prod in xml_producer_elem_list:
            if any(item == prod[1] for item in elem_list):
                new_producer_list.append(prod)
                if prod[1] not in new_elem_list:
                    new_elem_list.append(prod[1])

        for cons in xml_consumer_elem_list:
            if any(item == cons[1] for item in elem_list):
                new_consumer_list.append(cons)
                if cons[1] not in new_elem_list:
                    new_elem_list.append(cons[1])
    else:
        for cons in xml_consumer_elem_list:
            if any(item == cons[0] for item in new_flow_list) and \
                    any(item == cons[1] for item in elem_list):
                new_consumer_list.append(cons)
                if cons[1] not in new_elem_list:
                    new_elem_list.append(cons[1])

        for prod in xml_producer_elem_list:
            if any(item == prod[0] for item in new_flow_list) and \
                    any(item == prod[1] for item in elem_list):
                new_producer_list.append(prod)
                if prod[1] not in new_elem_list:
                    new_elem_list.append(prod[1])

    if len(new_consumer_list) == 0 and len(new_producer_list) == 0:
        new_elem_list = elem_list

    return new_elem_list, new_consumer_list, new_producer_list


def get_parent_dict(element, element_list, parent_dict):
    if element.parent:
        parent_dict[element.id] = element.parent.id

        if element.parent not in element_list:
            element_list.add(element.parent)
            element.parent.child_list.clear()

        element.parent.add_child(element)

        get_parent_dict(element.parent, element_list, parent_dict)


def get_fun_elem_function_list(function, function_list, fun_elem):
    if function.parent:
        if function.parent.id in fun_elem.allocated_function_list:
            get_fun_elem_function_list(function.parent, function_list, fun_elem)
        else:
            function_list.add(function)
    else:
        function_list.add(function)


def get_transition_list(p_state_list, p_transition_list):
    """Get transitions if state(s) from state_list are source/destination"""
    transition_list = set()
    for state in p_state_list:
        for transition in p_transition_list:
            if state.id == transition.source:
                transition_list.add(transition)
            if state.id == transition.destination:
                transition_list.add(transition)

    return transition_list
