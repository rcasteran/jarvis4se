"""@defgroup plantuml_adapter
Plantuml adapter module
"""

# Modules
import datamodel
from .util import ObjDiagram, StateDiagram, SequenceDiagram
from tools import Logger


def write_function_child(string_obj, function, input_flow_list, output_flow_list,
                         xml_attribute_list):
    """@ingroup plantuml_adapter
    Construct PlantUml text recursively
    @param[in,out] string_obj current PlantUml text
    @param[in] function
    @param[in] input_flow_list
    @param[in] output_flow_list
    @param[in] xml_attribute_list
    @return None
    """

    function_input_port = []
    function_output_port = []
    external_input_port = []
    external_output_port = []
    parent_function_port = []
    count = 1
    nb_component = count_composed_component(function, count)

    # TODO: Create get_port_lists() and optimize
    for p in input_flow_list:
        if p[0][0] == function.name.lower():
            function_input_port.append(p)
        if p[0][0] is None and function.parent is None:
            external_input_port.append(p)
            if p[0][1] == function.name.lower():
                parent_function_port.append(p)

    for q in output_flow_list:
        if q[0][0] == function.name.lower():
            function_output_port.append(q)
        if q[0][0] is None and function.parent is None:
            external_output_port.append(q)
            if q[0][1] == function.name.lower():
                parent_function_port.append(q)

    Logger.set_debug(__name__, f"Function name: {function.name}")
    Logger.set_debug(__name__, f"Input port list: {function_input_port}")
    Logger.set_debug(__name__, f"Output port list: {function_input_port}")
    Logger.set_debug(__name__, f"Parent function port list: {parent_function_port}")
    Logger.set_debug(__name__, f"External input port list: {external_input_port}")
    Logger.set_debug(__name__, f"External output port list: {external_output_port}")

    string_obj.create_port(function_input_port, "in")
    string_obj.create_port(function_output_port, "out")
    string_obj.create_port(parent_function_port, 'None')

    child_with_no_child_list = []
    child_with_child_list = []
    # Create a child list for each parent function
    for child_function in function.child_list:
        Logger.set_debug(__name__, f"{child_function.name} check as child of {function.name}")
        if child_function.child_list:
            child_with_child_list.append(child_function)
        else:
            child_with_no_child_list.append(child_function)

    # For child that has no child: create object
    for fun in child_with_no_child_list:
        string_obj.create_object(fun, xml_attribute_list)

    for child in child_with_child_list:
        string_obj.create_component(child)
        write_function_child(string_obj, child, input_flow_list, output_flow_list,
                             xml_attribute_list)
        nb_component -= 1

    # Close all the brackets depending on the number of component within highest parent
    for i in range(nb_component):
        string_obj.append_string('}\n')

    for component in child_with_child_list:
        string_obj.create_component_attribute(component, xml_attribute_list)

    whole_child_list = child_with_child_list + child_with_no_child_list
    for fun in whole_child_list:
        for i in input_flow_list:
            if i[0][0] == fun.name.lower():
                string_obj.create_port(input_flow_list, "in")
        for j in output_flow_list:
            if j[0][0] == fun.name.lower():
                string_obj.create_port(output_flow_list, "out")

    string_obj.create_port(external_input_port, "in")
    string_obj.create_port(external_output_port, "out")


def count_composed_component(function, count):
    """@ingroup plantuml_adapter
    Count the number of composed function within the higher function
    @param[in] function function to check
    @param[in] count number of component
    @return number of component
    """

    for elem in function.child_list:
        if elem.child_list:
            count += 1
            count_composed_component(elem, count)
            continue
    return count


def write_function_object(string_obj, function, input_flow_list, output_flow_list, check,
                          xml_attribute_list, component_obj=None, compo_diagram=False):
    """@ingroup plantuml_adapter
    Construct the PlantUml text for a function object with associated ports for flow lists.
    @param[in,out] string_obj current PlantUml text
    @param[in] function
    @param[in] input_flow_list
    @param[in] output_flow_list
    @param[in] check
    @param[in] xml_attribute_list
    @param[in] component_obj
    @param[in] compo_diagram
    @return PlantUml text for the function object
    """

    string_obj.create_object(function, xml_attribute_list)

    if check:
        string_obj.append_string('}\n')
        if component_obj:
            string_obj.create_component_attribute(component_obj, xml_attribute_list)

    for p in input_flow_list:
        if compo_diagram:
            if p[0][0] == function.name.lower():
                string_obj.create_port(input_flow_list, "in")
        else:
            if p[0][0] == function.name.lower() or p[0][1] == function.name.lower():
                string_obj.create_port(input_flow_list, "in")
    for q in output_flow_list:
        if compo_diagram:
            if q[0][0] == function.name.lower():
                string_obj.create_port(output_flow_list, "out")
        else:
            if q[0][0] == function.name.lower() or q[0][1] == function.name.lower():
                string_obj.create_port(output_flow_list, "out")


def get_function_diagrams(function_list, fun_elem_list, consumer_function_list, producer_function_list,
                          parent_child_dict, data_list, xml_type_list, xml_attribute_list):
    """@ingroup plantuml_adapter
    @anchor get_function_diagrams
    Construct the PlantUml text and url for the requested diagram between one of the following:
    - context of function
    - decomposition of function
    - chain of function
    @param[in] function_list
    @param[in] consumer_function_list
    @param[in] producer_function_list
    @param[in] parent_child_dict
    @param[in] data_list
    @param[in] xml_type_list
    @param[in] xml_attribute_list
    @return PlantUml text and url of the diagram
    """

    string_obj = ObjDiagram()
    # Filter output flows
    output_flow_list = get_output_flows(consumer_function_list, producer_function_list,
                                        concatenate=True)
    # Filter input flows
    input_flow_list = get_input_flows(consumer_function_list, producer_function_list,
                                      concatenate=True)

    # Filter consumers and producers list in order to create data flow
    data_flow_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                         parent_child_dict, concatenate=True)

    Logger.set_debug(__name__, f"Output flows list: {output_flow_list}")
    Logger.set_debug(__name__, f"Input flows list: {input_flow_list}")
    Logger.set_debug(__name__, f'Exchanged flows list: {data_flow_list}')

    if data_list:
        per_message_data_flow_list = get_exchanged_flows(consumer_function_list,
                                                         producer_function_list,
                                                         parent_child_dict)
        if len(data_list) == len(per_message_data_flow_list):
            ordered_function_list, ordered_message_list = order_list(per_message_data_flow_list,
                                                                     data_list)
            if per_message_data_flow_list != ordered_message_list:
                for idx, i in enumerate(ordered_message_list):
                    for j in data_flow_list:
                        for k in j[1]:
                            if i[2] == k and i[3]:
                                new = str(idx + 1) + ":" + k
                                j[1].remove(k)
                                j[1].append(new)

    # Loop in order to filter functions and write in output's file, see write_function_child()
    if parent_child_dict:
        if fun_elem_list:
            for fun_elem in fun_elem_list:
                string_obj.create_component(fun_elem)
                check_function = False
                for f in function_list:
                    if any(a == f.id for a in fun_elem.allocated_function_list):
                        if len(fun_elem.allocated_function_list) > 1:
                            check_function = False
                        else:
                            check_function = True
                        write_function_object(string_obj, f, input_flow_list, output_flow_list,
                                              check_function, xml_attribute_list, component_obj=fun_elem)
                if not check_function:
                    string_obj.append_string('}\n')
                    string_obj.create_component_attribute(fun_elem, xml_attribute_list)
        else:
            for function in function_list:
                if function.id not in parent_child_dict.keys():
                    if function.id in parent_child_dict.values():
                        # Function is a parent
                        string_obj.create_component(function)
                        write_function_child(string_obj, function, input_flow_list, output_flow_list,
                                             xml_attribute_list)
                    else:
                        # Function is not a parent:
                        write_function_object(string_obj, function, input_flow_list, output_flow_list,
                                              False, xml_attribute_list, compo_diagram=True)
                # Else do nothing : done as children of function parent
    else:
        for function in function_list:
            write_function_object(string_obj, function, input_flow_list, output_flow_list, False,
                                  xml_attribute_list)

    string_obj.create_input_flow(input_flow_list)
    string_obj.create_output_flow(output_flow_list)
    string_obj.create_data_flow(data_flow_list)

    return string_obj.string


def get_fun_elem_context_diagram(function_list, consumer_function_list, producer_function_list,
                                 data_list, xml_attribute_list, fun_elem_list, fun_inter_list):
    """@ingroup plantuml_adapter
    @anchor get_fun_elem_context_diagram
    Construct the PlantUml text and url for the context diagram for functional elements
    @param[in] function_list TBD
    @param[in] consumer_function_list TBD
    @param[in] producer_function_list TBD
    @param[in] data_list TBD
    @param[in] xml_attribute_list TBD
    @param[in] fun_elem_list TBD
    @param[in] fun_inter_list TBD
    @return PlantUml text and url of the diagram
    """

    string_obj = ObjDiagram()
    interface_list = None

    if fun_inter_list:

        unmerged_data_list = get_exchanged_flows(consumer_function_list, producer_function_list, {})
        interface_list, data_flow_list = get_interface_list(fun_inter_list,
                                                            data_list,
                                                            unmerged_data_list,
                                                            function_list,
                                                            fun_elem_list,
                                                            is_decomposition=False)

        data_flow_list = concatenate_flows(data_flow_list)

    else:

        # Filter consumers and producers list in order to create data flow
        data_flow_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                             {}, concatenate=True)

    # Filter output flows
    output_flow_list = get_output_flows(consumer_function_list, producer_function_list,
                                        concatenate=True)
    # Filter input flows
    input_flow_list = get_input_flows(consumer_function_list, producer_function_list,
                                      concatenate=True)

    # Write external functions
    external_function_list = []
    for function in function_list:
        is_external = True
        for fun_elem in fun_elem_list:
            if any(a == function.id for a in fun_elem.allocated_function_list):
                is_external = False

        if is_external:
            external_function_list.append(function)

    for function in external_function_list:
        string_obj.create_object(function, xml_attribute_list)

    for fun_elem in fun_elem_list:
        string_obj.create_component(fun_elem)
        check_function = False
        for f in function_list:
            if any(a == f.id for a in fun_elem.allocated_function_list):
                if len(fun_elem.allocated_function_list) > 1:
                    check_function = False
                else:
                    check_function = True
                write_function_object(string_obj, f, input_flow_list, output_flow_list,
                                      check_function, xml_attribute_list, component_obj=fun_elem)
        if not check_function:
            string_obj.append_string('}\n')
            string_obj.create_component_attribute(fun_elem, xml_attribute_list)

    string_obj.create_input_flow(input_flow_list)
    string_obj.create_output_flow(output_flow_list)
    string_obj.create_data_flow(data_flow_list)

    if interface_list:
        string_obj.create_interface(interface_list)

    return string_obj.string


def get_interface_list(fun_inter_list, data_list, data_flow_list, function_list, fun_elem_list,
                       is_decomposition=True):
    """@ingroup plantuml_adapter
    Get list of functional interfaces with the functional elements exposing them.
    Functional interface is returned only when specifed data is allocated to it
    @param[in] fun_inter_list TBD
    @param[in] data_list TBD
    @param[in] data_flow_list TBD
    @param[in] function_list TBD
    @param[in] fun_elem_list TBD
    @param[in] is_decomposition indicates if decomposition is required (True) or not (False)
    @return functional interfaces list
    """

    interface_list = []
    removed_data_flow_list = []
    initial_data = list(data_flow_list)
    idx = 0
    # Get all fun_inter with allocated data within data_flow_list and create interface list
    # [[producer, consumer, fun_inter]...]
    for fun_inter in fun_inter_list:
        Logger.set_debug(__name__, f"Interface {fun_inter.name}, allocated data {fun_inter.allocated_data_list}")
        if fun_inter.allocated_data_list:
            for data_id in fun_inter.allocated_data_list:
                for data in data_list:
                    if data_id == data.id:
                        for data_flow in data_flow_list.copy():
                            if data.name == data_flow[2]:
                                first_fun = None
                                second_fun = None
                                for fun in function_list:
                                    if data_flow[0] == fun.name.lower():
                                        first_fun = fun
                                    if data_flow[1] == fun.name.lower():
                                        second_fun = fun

                                if first_fun or second_fun:
                                    # Need to check consistency between [elem1, elem2, fun_inter] and [fun1, fun2, data]
                                    # before adding to the list
                                    is_first_fun_elem = False
                                    is_second_fun_elem = False
                                    for fun_elem in fun_elem_list:
                                        if any(exposed_fun_inter_id == fun_inter.id for exposed_fun_inter_id in
                                               fun_elem.exposed_interface_list):
                                            if first_fun and not is_first_fun_elem:
                                                is_first_fun_elem = any(allocated_fun_id ==
                                                                        first_fun.id for allocated_fun_id
                                                                        in fun_elem.allocated_function_list)
                                            if second_fun and not is_second_fun_elem:
                                                is_second_fun_elem = any(allocated_fun_id ==
                                                                         second_fun.id for allocated_fun_id
                                                                         in fun_elem.allocated_function_list)

                                    if (first_fun and is_first_fun_elem and not second_fun) or \
                                            (second_fun and is_second_fun_elem and not first_fun) or \
                                            (first_fun and is_first_fun_elem and second_fun and is_second_fun_elem):
                                        Logger.set_debug(__name__, f"[{first_fun}, {second_fun}, {fun_inter}] added")
                                        interface_list.insert(idx, [first_fun, second_fun, fun_inter])
                                        removed_data_flow_list.insert(idx, data_flow)
                                        data_flow_list.remove(data_flow)
                                        idx += 1
                                        break
        else:
            Logger.set_info(__name__, f"{fun_inter.name} does not have any allocated data (no display)")

    output_list, interface_list = get_fun_elem_from_fun_inter(interface_list, fun_elem_list, is_decomposition)

    if not output_list:
        return None, initial_data

    # (re)Add [producer, consumer, data_name] to data_flow_list if no interface exposed
    if any(isinstance(s, list) for s in interface_list):
        for idx, rest_inter in enumerate(interface_list):
            if isinstance(rest_inter, list):
                data_flow_list.append(removed_data_flow_list[idx])

    return output_list, data_flow_list


def get_fun_elem_from_fun_inter(interface_list, fun_elem_list, is_decomposition=True):
    """@ingroup plantuml_adapter
    Get list of functional interfaces with the functional elements exposing them from interface_list =
    [[producer, consumer, fun_inter]...] and put value to False if (first, second, interface)
    have been added to output_list (i.e. fun_elem_1/fun_elem_2 have been found for a fun_inter)
    @param[in] interface_list TBD
    @param[in] fun_elem_list TBD
    @param[in] is_decomposition indicates if decomposition is required (True) or not (False)
    @return functional interfaces list
    """

    output_list = []
    for ix, (first, second, interface) in enumerate(interface_list):
        fun_elem_1 = None
        fun_elem_2 = None
        if first:
            for elem_1 in fun_elem_list:
                if any(s == interface.id for s in elem_1.exposed_interface_list):
                    if is_decomposition:
                        if not elem_1.child_list:
                            fun_elem_1 = elem_1
                        else:
                            check = True
                            for child in elem_1.child_list:
                                if any(s == interface.id for s in child.exposed_interface_list):
                                    check = False
                            if check:
                                fun_elem_1 = elem_1
                    else:
                        fun_elem_1 = elem_1

        if second:
            for elem_2 in fun_elem_list:
                if not first:
                    if is_decomposition:
                        if any(s == interface.id for s in elem_2.exposed_interface_list):
                            if not elem_2.child_list:
                                fun_elem_2 = elem_2
                            else:
                                check = True
                                for child in elem_2.child_list:
                                    if any(s == interface.id for s in child.exposed_interface_list):
                                        check = False
                                if check:
                                    fun_elem_2 = elem_2
                    else:
                        fun_elem_2 = elem_2
                else:
                    if any(s == interface.id for s in elem_2.exposed_interface_list) and \
                            elem_2 != fun_elem_1:
                        if is_decomposition:
                            if not elem_2.child_list:
                                fun_elem_2 = elem_2
                            else:
                                check = True
                                for child in elem_2.child_list:
                                    if any(s == interface.id for s in child.exposed_interface_list):
                                        check = False

                                if check:
                                    fun_elem_2 = elem_2
                        else:
                            fun_elem_2 = elem_2

        if not (not fun_elem_1 and not fun_elem_2):
            if [fun_elem_1, fun_elem_2, interface] not in output_list:
                output_list.append([fun_elem_1, fun_elem_2, interface])
            interface_list[ix] = False

    return output_list, interface_list


def check_child_allocation(string_obj, fun_elem, function_list, xml_attribute_list):
    """@ingroup plantuml_adapter
    Check for each function allocated to a functional element if not allocated to any
    functional element child: in that case => write function object string.
    @param[in,out] string_obj current PlantUml text
    @param[in] fun_elem functional element to check
    @param[in] function_list list of functions
    @param[in] xml_attribute_list xml list of attributes
    @return None
    """

    for function in function_list:
        if function.id in fun_elem.allocated_function_list:
            fun_elem_child_allocated_function_list = []
            for c in fun_elem.child_list:
                for j in c.allocated_function_list:
                    fun_elem_child_allocated_function_list.append(j)

            if not any(s == function.id for s in fun_elem_child_allocated_function_list):
                write_function_object(string_obj, function, [], [], False, xml_attribute_list)


def recursive_decomposition(string_obj, main_fun_elem, function_list, xml_attribute_list,
                            first_iter=False):
    """@ingroup plantuml_adapter
    Create PlantUml text for functional elements recursively
    @param[in,out] string_obj current PlantUml text
    @param[in] main_fun_elem
    @param[in] function_list list of functions
    @param[in] xml_attribute_list xml list of attributes
    @param[in] first_iter
    @return None
    """

    if first_iter is True:
        string_obj.create_component(main_fun_elem)
        check_child_allocation(string_obj, main_fun_elem, function_list, xml_attribute_list)
        if main_fun_elem.child_list:
            recursive_decomposition(string_obj, main_fun_elem, function_list, xml_attribute_list)
    else:
        for c in main_fun_elem.child_list:
            string_obj.create_component(c)
            check_child_allocation(string_obj, c, function_list, xml_attribute_list)
            if c.child_list:
                recursive_decomposition(string_obj, c, function_list, xml_attribute_list)
            string_obj.append_string('}\n')
            string_obj.create_component_attribute(c, xml_attribute_list)
        string_obj.create_component_attribute(main_fun_elem, xml_attribute_list)


def get_fun_elem_decomposition(main_fun_elem, fun_elem_list, allocated_function_list, consumer_list,
                               producer_list, external_function_list, xml_attribute_list,
                               data_list, fun_inter_list):
    """@ingroup plantuml_adapter
    @anchor get_fun_elem_decomposition
    Construct the PlantUml text for the functional element decomposition diagram
    @param[in] main_fun_elem main functional element
    @param[in] fun_elem_list functional element list
    @param[in] allocated_function_list list of allocated functions to main functional element
    @param[in] consumer_list filtered consumers list
    @param[in] producer_list filtered producers list
    @param[in] external_function_list filtered external functions list
    @param[in] xml_attribute_list xml list of attributes
    @param[in] data_list data list
    @param[in] fun_inter_list functional interface list
    @return PlantUml text of the diagram
    """

    string_obj = ObjDiagram()
    interface_list = None

    if fun_inter_list:
        unmerged_data_list = get_exchanged_flows(consumer_list, producer_list, {})
        interface_list, data_flow_list = get_interface_list(fun_inter_list,
                                                            data_list,
                                                            unmerged_data_list,
                                                            allocated_function_list.
                                                            union(external_function_list),
                                                            fun_elem_list,
                                                            is_decomposition=True)

        data_flow_list = concatenate_flows(data_flow_list)

    else:
        # Filter consumers and producers list in order to create data flow
        data_flow_list = get_exchanged_flows(consumer_list, producer_list, {}, concatenate=True)

    # Write external functions that are not already allocated to external components
    external_function_not_allocated_list = []
    for function in external_function_list:
        is_external = True
        for fun_elem in fun_elem_list:
            if any(a == function.id for a in fun_elem.allocated_function_list):
                is_external = False

        if is_external:
            external_function_not_allocated_list.append(function)

    for function in external_function_not_allocated_list:
        string_obj.create_object(function, xml_attribute_list)

    # Write functional element decompo recursively and add allocated functions
    recursive_decomposition(string_obj, main_fun_elem, allocated_function_list, xml_attribute_list,
                            first_iter=True)
    string_obj.append_string('}\n')
    string_obj.create_component_attribute(main_fun_elem, xml_attribute_list)
    # Write external fun_elem
    for elem in fun_elem_list:
        if elem != main_fun_elem and elem.parent is None:
            recursive_decomposition(string_obj, elem, external_function_list, xml_attribute_list,
                                    first_iter=True)
            string_obj.append_string('}\n')
            string_obj.create_component_attribute(elem, xml_attribute_list)

    # Write data flows
    string_obj.create_data_flow(data_flow_list)
    if interface_list:
        string_obj.create_interface(interface_list)

    return string_obj.string


def get_sequence_diagram(function_list, consumer_function_list, producer_function_list,
                         parent_child_dict, data_list, str_out=False):
    """@ingroup plantuml_adapter
    @anchor get_sequence_diagram
    Construct the PlantUml text for the sequence diagrams
    @param[in] function_list TBD
    @param[in] consumer_function_list TBD
    @param[in] producer_function_list TBD
    @param[in] parent_child_dict TBD
    @param[in] data_list TBD
    @return PlantUml text of the diagram
    """

    seq_obj_string = SequenceDiagram()

    message_list = get_exchanged_flows(consumer_function_list, producer_function_list,
                                       parent_child_dict)
    ordered_function_list, ordered_message_list = order_list(message_list, data_list)

    if ordered_function_list:
        for fun_name in ordered_function_list:
            for f in function_list:
                if fun_name == f.name.lower():
                    seq_obj_string.create_participant(f)
    else:
        for f in function_list:
            seq_obj_string.create_participant(f)

    seq_obj_string.create_sequence_message(ordered_message_list)

    return seq_obj_string.string


def get_predecessor_list(data):
    """@ingroup plantuml_adapter
    Get the predecessor's list for a Data object
    @param[in] data data object
    @return predecessor list
    """

    predecessor_list = set()
    if data.predecessor_list:
        for predecessor in data.predecessor_list:
            predecessor_list.add(predecessor)

    return predecessor_list


def check_sequence(predecessor_list, sequence):
    """@ingroup plantuml_adapter
    Check if predecessors of a data are in a sequence
    @param[in] predecessor_list predecessor list
    @param[in] sequence sequence
    @return TRUE (predecessors are in the sequence) or FALSE
    """

    check = False
    if predecessor_list == set():
        check = None
        return check

    pred_set = set()
    seq_set = set()
    for pred in predecessor_list:
        pred_set.add(pred.name)
    for elem in sequence:
        seq_set.add(elem[2].name)

    if pred_set.issubset(seq_set):
        check = True
        return check

    return check


def clean_predecessor_list(message_object_list):
    """@ingroup plantuml_adapter
    Delete predecessor if not in the message's list
    @param[in] message_object_list TBD
    @return updated message list
    """

    for message in message_object_list:
        pred_list = get_predecessor_list(message[2])
        for pred in pred_list:
            if not any(pred in s for s in message_object_list):
                message[2].predecessor_list.remove(pred)

    return message_object_list


def get_sequence(message, message_object_list, sequence_list, sequence=None, index=None):
    """@ingroup plantuml_adapter
    Return a sequence for a given message
    @param[in] message TBD
    @param[in] message_object_list TBD
    @param[in] sequence_list TBD
    @param[in] sequence TBD
    @param[in] index TBD
    @return sequence
    """
    if not sequence:
        sequence = []
        index = 0
    if message not in sequence and not any(message in s for s in sequence_list) is True:
        message[3] = True
        sequence.insert(index, message)
        index += 1
        for mess in message_object_list:
            if message[2] in mess[2].predecessor_list:
                get_sequence(mess, message_object_list, sequence_list, sequence, index)

    return sequence


def get_sequences(message_object_list):
    """@ingroup plantuml_adapter
    Group all sequences into a sequence list
    @param[in] message_object_list
    @return sequence list
    """

    sequence_list = []
    for message in message_object_list:
        if not message[2].predecessor_list:
            sequence = get_sequence(message, message_object_list, sequence_list)
            sequence_list.append(sequence)

    return sequence_list


def post_check_sequence(sequence_list):
    """@ingroup plantuml_adapter
    Check if message isn't missing in sequence, insert it at the good place and loop if not
    well ordered (predecessor after each one)
    @param[in] sequence_list TBD
    @return sequence list ordered
    """

    for (idx, i) in enumerate(sequence_list):
        pred = i[2].predecessor_list
        if check_sequence(pred, sequence_list[:idx]) is True:
            pass
        elif check_sequence(pred, sequence_list[:idx]) is False:
            for (index, elem) in enumerate(sequence_list.copy()):
                curr_pred = elem[2].predecessor_list
                if check_sequence(curr_pred, sequence_list[:index]) is True:
                    sequence_list.remove(i)
                    sequence_list.insert(index + 1, i)
                    index += 1
                else:
                    continue
        elif check_sequence(pred, sequence_list[:idx]) is None:
            pass
        idx += 1

    for (new_idx, message) in enumerate(sequence_list):
        new_pred = message[2].predecessor_list
        if check_sequence(new_pred, sequence_list[:new_idx]) is False:
            post_check_sequence(sequence_list)

    return sequence_list


def get_sequence_list(message_object_list):
    """@ingroup plantuml_adapter
    Call for sequences then clean_up and post_check
    @param[in] message_object_list TBD
    @return sequence list
    """
    sequence_list = get_sequences(message_object_list)

    sequence_list = sorted(sequence_list, key=lambda x: len(x), reverse=True)
    # Could be possible to implement this part within post_check_sequence()
    for (index, i) in enumerate(sequence_list):
        main_list = sequence_list[0]
        if index > 0:
            start = 0
            for j in i.copy():
                if not j[2].predecessor_list:
                    i.remove(j)
                    main_list.insert(start, j)
                    start += 1

    sequence_list = [item for sub in sequence_list for item in sub]
    sequence_list = post_check_sequence(sequence_list)

    return sequence_list


def order_list(message_list, data_list):
    """@ingroup plantuml_adapter
    Order functions and messages
    @param[in] message_list TBD
    @param[in] data_list TBD
    @return ordered message list and ordered function list
    """

    ordered_message_list = []
    ordered_function_list = []
    message_object_list = []

    for i in message_list:
        for data in data_list:
            if i[2] == data.name:
                message_object_list.append([i[0], i[1], data, False])

    message_object_list = clean_predecessor_list(message_object_list)
    ordored_message_object_list = get_sequence_list(message_object_list)

    # Add index for each item within the list
    for idx, t in enumerate(ordored_message_object_list):
        ordered_message_list.insert(idx, [t[0], t[1], t[2].name, t[3]])

    # Create the ordered(from ordered message list) function's list
    # Starting with producers
    for idx, m in enumerate(ordered_message_list):
        if m[0] not in ordered_function_list:
            ordered_function_list.insert(idx, m[0])
    # Finishing with consumers
    for j in message_list:
        if j[1] not in ordered_function_list:
            ordered_function_list.append(j[1])

    return ordered_function_list, ordered_message_list


def get_exchanged_flows(consumer_function_list, producer_function_list, parent_child_dict,
                        concatenate=False):
    """@ingroup plantuml_adapter
    Return list of exchanged flows [[producer, consumer, data]], i.e. data that have
    producer and consumer
    @param[in] consumer_function_list TBD
    @param[in] producer_function_list TBD
    @param[in] parent_child_dict TBD
    @param[in] concatenate TBD
    @return list of exchanged flows
    """

    output_list = []

    for producer_flow, producer_function in producer_function_list:
        Logger.set_debug(__name__, f'Producer flow: {producer_flow}; '
                                   f'function: {producer_function.id}, {producer_function.name}')
        if not producer_function.child_list or not parent_child_dict:
            for cons_flow, consumer_function in consumer_function_list:
                Logger.set_debug(__name__, f'Consumer flow: {cons_flow}; '
                                           f'function: {consumer_function.id}, {consumer_function.name}')
                if (not consumer_function.child_list or not parent_child_dict) and cons_flow == producer_flow:
                    output_list.append(
                        [producer_function.name.lower(), consumer_function.name.lower(),
                         producer_flow])

    if concatenate:
        output_list = concatenate_flows(output_list)

    return output_list


def get_output_flows(consumer_function_list, producer_function_list, concatenate=False):
    """@ingroup plantuml_adapter
    Return list of output flows [[None/parent_name, producer, data]], i.e. data that
    have only producer
    @param[in] consumer_function_list TBD
    @param[in] producer_function_list TBD
    @param[in] concatenate TBD
    @return list of output flows
    """
    flow_consumer_name_list = []
    flow_child_consumer_list = []
    temp_input_list = []
    output_list = []

    for flow, cons in consumer_function_list:
        flow_consumer_name_list.append([flow, cons.name.lower()])
        if cons.child_list is not None:
            for child in cons.child_list:
                flow_child = [flow, child.name.lower()]
                if [flow, child] in consumer_function_list:
                    flow_child_consumer_list.append(flow_child)

    for consumer_flow, consumer_function in consumer_function_list:
        if len(consumer_function.child_list) > 0:
            if len(flow_child_consumer_list) > 0:
                if not any(consumer_flow in sublist for sublist in flow_child_consumer_list):
                    temp_input_list.append([consumer_function.name.lower(), consumer_flow])
            if len(flow_child_consumer_list) == 0:
                temp_input_list.append([consumer_function.name.lower(), consumer_flow])

    for producer_flow, producer_function in producer_function_list:
        # TODO to be checked because returns flow with both producer and consumer (same output as get_exchanged_flows)
        # for name, flow in temp_input_list:
        #     if producer_flow == flow:
        #         flow_child_consumer_list = [name, producer_function.name.lower(), producer_flow]
        #         output_list.append(flow_child_consumer_list)

        # Looking for outputs (i.e. flow with only producer's function)
        if not any(producer_flow in sublist for sublist in flow_consumer_name_list):
            if not any(producer_flow in sub for sub in output_list):
                output_list.append([None, producer_function.name.lower(), producer_flow])

    if concatenate:
        output_list = concatenate_flows(output_list)

    return output_list


def get_input_flows(consumer_function_list, producer_function_list, concatenate=False):
    """@ingroup plantuml_adapter
    Return list of input flow [[None/parent_name, consumer, data]], i.e. data that
    have only consumer
    @param[in] consumer_function_list TBD
    @param[in] producer_function_list TBD
    @param[in] concatenate TBD
    @return list of input flows
    """

    flow_producer_name_list = []
    flow_child_producer_list = []
    temp_input_list = []
    output_list = []

    for flow, prod in producer_function_list:
        flow_producer_name_list.append([flow, prod.name.lower()])
        if prod.child_list is not None:
            for child in prod.child_list:
                flow_child = [flow, child.name.lower()]
                if [flow, child] in producer_function_list:
                    flow_child_producer_list.append(flow_child)

    for producer_flow, producer_function in producer_function_list:
        if len(producer_function.child_list) > 0:
            if len(flow_child_producer_list) > 0:
                if not any(producer_flow in sublist for sublist in flow_child_producer_list):
                    temp_input_list.append([producer_function.name.lower(), producer_flow])
            if len(flow_child_producer_list) == 0:
                temp_input_list.append([producer_function.name.lower(), producer_flow])

    for cons_flow, consumer_fun in consumer_function_list:
        # TODO to be checked because returns flow with both producer and consumer (same output as get_exchanged_flows)
        # for name, flow in temp_input_list:
        #     if cons_flow == flow:
        #         flow_child_producer_list = [name, consumer_fun.name.lower(), cons_flow]
        #         output_list.append(flow_child_producer_list)

        if not any(cons_flow in sublist for sublist in flow_producer_name_list):
            if not any(cons_flow in sublist for sublist in output_list):
                output_list.append([None, consumer_fun.name.lower(), cons_flow])

    if concatenate:
        output_list = concatenate_flows(output_list)
    return output_list


def concatenate_flows(input_list):
    """@ingroup plantuml_adapter
    Concatenate the flows with same consumer and producer: from [[cons=A, prod=B, flow_1],
    [cons=A, prod=B, flow_2]] to [[cons=A, prod=B, [flow_1, flow_2]].
    Adaptation for flow notation in PlantUml
    @param[in] input_list
    @return list of output flows
    """

    output_list = []
    per_function_name_filtered_list = set(map(lambda x: (x[0], x[1]), input_list))
    per_flow_filtered_list = [[y[2] for y in input_list if y[0] == x and y[1] == z] for x, z in
                              per_function_name_filtered_list]
    for idx, function in enumerate(per_function_name_filtered_list):
        output_list.append([function, per_flow_filtered_list[idx]])

    return output_list


def get_state_machine_diagram(xml_state_list, xml_transition_list, fun_elem_list=None):
    """@ingroup plantuml_adapter
    @anchor get_state_machine_diagram
    Construct  the PlantUml text and url for state machine diagrams
    @param[in] xml_state_list TBD
    @param[in] xml_transition_list TBD
    @param[in] fun_elem_list TBD
    @return PlantUml text and url diagram for state machine diagram
    """

    state_obj_string = StateDiagram()
    objects_conditions_list = get_objects_conditions_list(xml_state_list, xml_transition_list)
    already_added_state_id_list = []
    for state in xml_state_list:
        if not state.parent and state.child_list:
            check = False
            if fun_elem_list:
                for fun_elem in fun_elem_list:
                    if state.id in fun_elem.allocated_state_list:
                        if fun_elem.parent is None:
                            check = True
                            state_obj_string.create_state(fun_elem, True)

            write_composed_state(state_obj_string, state, already_added_state_id_list,
                                 objects_conditions_list)
            if check:
                state_obj_string.append_string('}\n')

    for s in xml_state_list:
        if s.id not in already_added_state_id_list:
            check = False
            if fun_elem_list:
                for fun_elem in fun_elem_list:
                    if s.id in fun_elem.allocated_state_list:
                        if fun_elem.parent is None:
                            check = True
                            state_obj_string.create_state(fun_elem, True)
            write_state(state_obj_string, s, already_added_state_id_list, objects_conditions_list)
            if check:
                state_obj_string.append_string('}\n')

    for p in objects_conditions_list.copy():
        if (p[0].id and not p[1].id) or (not p[0].id and p[1].id):
            state_obj_string.create_transition([p])
            objects_conditions_list.remove(p)

    return state_obj_string.string


def get_objects_conditions_list(xml_state_list, xml_transition_list):
    """@ingroup plantuml_adapter
    Return all conditions associated to a list of state within a list of transition
    @param[in] xml_state_list TBD
    @param[in] xml_transition_list TBD
    @return conditions list
    """

    objects_conditions_list = []
    formatted_transition_list = []
    # Create transition's list [src_id, dest_id, [conditions]]
    for i in xml_transition_list:
        formatted_transition_list.append([i.source, i.destination, i.condition_list])

    # Create transition's list [src_state_obj, dest_state_obj, [conditions]]
    for j in formatted_transition_list:
        result = match_transition_states(j, xml_state_list)
        if result:
            objects_conditions_list.append(result)

    return objects_conditions_list


def write_state(state_obj_string, state, new, objects_conditions_list):
    """@ingroup plantuml_adapter
    Returns simple state string for PlantUml text
    @param[in, out] state_obj_string TBD
    @param[in] state TBD
    @param[in] new TBD
    @param[in, out] objects_conditions_list TBD
    @return None
    """

    if not state.parent and not state.child_list:
        state_obj_string.create_state(state)
        new.append(state.id)

    for j in objects_conditions_list:
        if all(x in new for x in [j[0].id, j[1].id]):
            state_obj_string.create_transition([j])
            objects_conditions_list.remove(j)


def write_composed_state(state_obj_string, state, new, objects_conditions_list, output_str='',
                         count=0):
    """@ingroup plantuml_adapter
    Returns composed state string for PlantUml text
    @param[in, out] state_obj_string TBD
    @param[in] state TBD
    @param[in] new TBD
    @param[in, out] objects_conditions_list TBD
    @param[in] output_str TBD
    @param[in] count TBD
    @return None
    """

    state_obj_string.create_state(state, parent=True)
    new.insert(count, state.id)
    count += 1
    for i in state.child_list:
        if not i.child_list:
            state_obj_string.create_state(i)
            new.insert(count + 1, i.id)
        else:
            write_composed_state(state_obj_string, i, new, objects_conditions_list, output_str,
                                 count)

    for j in objects_conditions_list:
        if all(x in new for x in [j[0].id, j[1].id]):
            state_obj_string.create_transition([j])
            objects_conditions_list.remove(j)

    state_obj_string.append_string("}\n" * count)


def match_transition_states(transition, xml_state_list):
    """@ingroup plantuml_adapter
    Return transition with associated state.
    If not, create default ENTRY or EXIT if one is missing
    @param[in] transition TBD
    @param[in] xml_state_list TBD
    @return transition
    """
    out = None
    source_state, destination_state = get_source_and_dest(transition, xml_state_list)

    if source_state is not None and destination_state is not None:
        out = [source_state, destination_state, transition[2]]
    elif source_state is not None and destination_state is None:
        n = datamodel.State()
        n.set_name('EXIT')
        xml_state_list.add(n)
        out = [source_state, n, transition[2]]
    elif source_state is None and destination_state is not None:
        n = datamodel.State()
        n.set_name('ENTRY')
        xml_state_list.add(n)
        out = [n, destination_state, transition[2]]

    return out


def get_source_and_dest(transition, xml_state_list):
    """@ingroup plantuml_adapter
    Iterate over states id to get source and destination objects
    @param[in] transition TBD
    @param[in] xml_state_list TBD
    @return source and destination objects
    """
    source_state = None
    destination_state = None

    for a, b in zip(xml_state_list, xml_state_list):
        if transition[0] == a.id:
            source_state = a
        if transition[1] == b.id:
            destination_state = b
        if destination_state and source_state:
            return source_state, destination_state

    return source_state, destination_state
