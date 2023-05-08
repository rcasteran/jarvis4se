"""@defgroup diagram
Jarvis diagram module
"""
# Modules
from jarvis import question_answer


def get_cons_or_prod_paired(function_list, xml_flow_list, xml_opposite_flow_list):
    """Get flow list if opposite flow is existing: e.g. if flow A is consumed and produced by
    function within function_list => Add it"""
    new_flow_list = []

    for func in function_list:
        # Flow = [Data_name, Function]
        for flow in xml_flow_list:
            if func in flow and flow not in new_flow_list:
                # Oppo = [Data_name, Function]
                for oppo in xml_opposite_flow_list:
                    if oppo[0] == flow[0] and oppo[1] in function_list:
                        new_flow_list.append(flow)
                        break

    return new_flow_list


def get_cons_prod_from_allocated_functions(allocated_function_list,
                                           xml_producer_function_list,
                                           xml_consumer_function_list,
                                           with_external_functions=True):
    """Get consumers/producers from function's allocated to main_fun_elem (and its descendant)"""
    new_producer_list = []
    new_consumer_list = []
    for allocated_function in allocated_function_list:
        allocated_function.child_list.clear()
        allocated_function.parent = None
        for elem in xml_producer_function_list:
            if allocated_function in elem:
                new_producer_list.append(elem)
        for elem in xml_consumer_function_list:
            if allocated_function in elem:
                new_consumer_list.append(elem)

    if with_external_functions:
        external_function_list, new_consumer_list, new_producer_list = get_ext_cons_prod(
            new_producer_list,
            new_consumer_list,
            xml_producer_function_list,
            xml_consumer_function_list)
    else:
        external_function_list = None

    return external_function_list, new_consumer_list, new_producer_list


def get_ext_cons_prod(producer_list, consumer_list, xml_producer_function_list,
                      xml_consumer_function_list):
    """Get external cons/prod associated to main_fun_elem allocated functions"""
    external_function_list = set()
    for elem in consumer_list:
        if not any(elem[0] in s for s in producer_list):
            for prod in xml_producer_function_list:
                if prod[0] == elem[0] and prod[1].parent is None:
                    external_function_list.add(prod[1])
                    if prod not in producer_list:
                        producer_list.append(prod)

    for elem in producer_list:
        if not any(elem[0] in s for s in consumer_list):
            for cons in xml_consumer_function_list:
                if cons[0] == elem[0] and cons[1].parent is None:
                    external_function_list.add(cons[1])
                    if cons not in consumer_list:
                        consumer_list.append(cons)

    return external_function_list, consumer_list, producer_list


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
    main = None

    for fun in xml_function_list:
        if diagram_function_str in (fun.name, fun.alias):
            new_function_list.add(fun)
            main = fun
            for xml_producer_flow, xml_producer in xml_producer_function_list:
                if fun == xml_producer:
                    check = False
                    for flow, consumer in xml_consumer_function_list:
                        if xml_producer_flow == flow:
                            if consumer.parent is None:
                                current_func, current_dict = question_answer.get_children(fun)
                                parent_check = question_answer.check_parentality(consumer, main)
                                if consumer not in current_func and parent_check is False:
                                    new_consumer_list.append([xml_producer_flow, consumer])
                                    new_function_list.add(consumer)
                                    check = True
                            elif main.parent == consumer.parent and consumer != main:
                                new_consumer_list.append([flow, consumer])
                                new_function_list.add(consumer)
                                check = True
                    if check:
                        if [xml_producer_flow, xml_producer] not in new_producer_list:
                            new_producer_list.append([xml_producer_flow, xml_producer])

                    if not any(xml_producer_flow in s for s in xml_consumer_function_list):
                        if [xml_producer_flow, xml_producer] not in new_producer_list:
                            new_producer_list.append([xml_producer_flow, xml_producer])

    if main is not None:
        for xml_consumer_flow, xml_consumer in xml_consumer_function_list:
            if xml_consumer == main:
                check = False
                for flow, producer in xml_producer_function_list:
                    if flow == xml_consumer_flow:
                        if producer.parent is None:
                            current_func, current_dict = question_answer.get_children(producer)
                            if main not in current_func:
                                new_producer_list.append([flow, producer])
                                new_function_list.add(producer)
                                check = True
                        elif main.parent == producer.parent and producer != main:
                            new_producer_list.append([flow, producer])
                            new_function_list.add(producer)
                            check = True
                if check:
                    if [xml_consumer_flow, xml_consumer] not in new_consumer_list:
                        new_consumer_list.append([xml_consumer_flow, xml_consumer])

                if not any(xml_consumer_flow in s for s in xml_producer_function_list):
                    if [xml_consumer_flow, xml_consumer] not in new_consumer_list:
                        new_consumer_list.append([xml_consumer_flow, xml_consumer])

    for f in new_function_list:
        f.child_list.clear()

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
                if get_highest_fun_elem_exposing_fun_inter(fun_inter, fun_elem) and \
                        question_answer.check_not_family(main_fun_elem, fun_elem):
                    fun_elem_list.add(fun_elem)
                    if [main_fun_elem, fun_elem, fun_inter] not in fun_elem_inter_list:
                        fun_elem_inter_list.append([main_fun_elem, fun_elem, fun_inter])

    return fun_elem_list, interface_list, fun_elem_inter_list


def get_highest_fun_elem_exposing_fun_inter(fun_inter, fun_elem):
    """Returns True if it's highest fun_elem exposing fun_inter"""
    check = False
    if not fun_elem.parent:
        check = True
    elif not any(a == fun_inter.id for a in fun_elem.parent.exposed_interface_list):
        check = True

    return check


def filter_fun_elem_with_level(main_fun_elem, diagram_level, xml_function_list, xml_fun_elem_list):
    """Clean unwanted fun_elem and functions from xml_lists then returns them"""
    main_fun_elem_list, _ = question_answer.get_children(main_fun_elem, level=diagram_level)
    # Remove (child) elements from xml lists that are below the level asked
    for unwanted_fun_elem in xml_fun_elem_list.symmetric_difference(main_fun_elem_list):
        if not question_answer.check_not_family(unwanted_fun_elem, main_fun_elem):
            for fun in xml_function_list.copy():
                if fun.id in unwanted_fun_elem.allocated_function_list:
                    xml_function_list.remove(fun)
            xml_fun_elem_list.remove(unwanted_fun_elem)
    # Remove (child) elements from external fun_elem (main_fun_elem point of view)
    for unwanted_fun_elem in xml_fun_elem_list.symmetric_difference(main_fun_elem_list):
        if question_answer.check_not_family(unwanted_fun_elem, main_fun_elem) and \
                unwanted_fun_elem.parent is None:
            curr_fun_elem_list, _ = question_answer.get_children(unwanted_fun_elem, level=diagram_level)
            for un_fun_elem in xml_fun_elem_list.symmetric_difference(curr_fun_elem_list):
                if not question_answer.check_not_family(unwanted_fun_elem, un_fun_elem):
                    xml_fun_elem_list.remove(un_fun_elem)

    return xml_function_list, xml_fun_elem_list


def get_level_0_function(fun_elem, function_list, level_0_function_list):
    """Recursively get functions allocated to main_fun_elem and its descendant"""
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
