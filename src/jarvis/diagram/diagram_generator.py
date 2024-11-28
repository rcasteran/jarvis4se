"""@defgroup diagram
Jarvis diagram module
"""
# Libraries
import re

# Modules
import plantuml_adapter
from datamodel import FunctionalElement
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_INFORMATION_LIST, XML_DICT_KEY_11_ATTRIBUTE_LIST, \
    XML_DICT_KEY_12_VIEW_LIST, XML_DICT_KEY_13_TYPE_LIST, XML_DICT_KEY_14_FUN_CONS_LIST, \
    XML_DICT_KEY_15_FUN_PROD_LIST, XML_DICT_KEY_16_ACT_CONS_LIST, XML_DICT_KEY_17_ACT_PROD_LIST
from jarvis.query import query_object, question_answer, query_inheritance
from jarvis import util as jarvis_util
from . import diagram_generator_chain
from . import diagram_generator_farch
from . import diagram_generator_fana
from . import diagram_generator_parch
from . import util
from tools import Logger


def filter_show_command(diagram_name_str, **kwargs):
    """Entry point for all diagrams (i.e. 'show' command) from command_parser.py"""
    plantuml_string = None
    wanted_diagram_str = diagram_name_str[0].replace('"', "").strip()
    regex = r"(decomposition|context|chain|sequence|state|function|state sequence)\s(.*)"
    specific_diagram_str = re.search(regex, wanted_diagram_str, re.MULTILINE)
    if specific_diagram_str:
        if 'sequence' not in specific_diagram_str.group(2):
            diagram_type_str = specific_diagram_str.group(1)
            diagram_object_str = specific_diagram_str.group(2)
        else:
            diagram_type_str = specific_diagram_str.group(1) + ' sequence'
            diagram_object_str = specific_diagram_str.group(2).replace("sequence ", "")

        plantuml_string = switch_show_filter(diagram_type_str=diagram_type_str,
                                             diagram_object_str=diagram_object_str,
                                             **kwargs)
    else:
        Logger.set_warning(__name__,
                           f"Jarvis does not understand the command {wanted_diagram_str}")

    return plantuml_string


def switch_show_filter(**kwargs):
    """Switch case between diagram types"""
    switch = {
        "function": case_function_diagram,
        "context": case_context_diagram,
        "decomposition": case_decomposition_diagram,
        "chain": case_chain_diagram,
        "sequence": case_sequence_diagram,
        "state": case_state_diagram,
        "state sequence": case_state_sequence_diagram
    }
    get_diagram = switch.get(kwargs['diagram_type_str'], case_no_diagram)
    return get_diagram(**kwargs)


def case_function_diagram(**kwargs):
    """Case for 'show function <functional_element>'"""
    plantuml_string = None

    if kwargs['diagram_object_str'] in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]):
        plantuml_string = diagram_generator_farch.show_fun_elem_function(kwargs['diagram_object_str'],
                                                                         kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
                                                                         kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                                         kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                                                                         kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
                                                                         kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST])

    else:
        Logger.set_warning(__name__,
                           f"Jarvis does not know the functional Element {kwargs['diagram_object_str']}")

    return plantuml_string


def case_context_diagram(**kwargs):
    """Case for 'show context <functional_element>/<function>'"""
    plantuml_string = None

    if kwargs['diagram_object_str'] in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_1_FUNCTION_LIST]):
        consumed_flow_inheritance = query_inheritance.query_inheritance_add_inherited_object(
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
            **kwargs
        )
        produced_flow_inheritance = query_inheritance.query_inheritance_add_inherited_object(
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
            **kwargs
        )
        child_inheritance = query_inheritance.query_inheritance_add_inherited_object_children(
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST]
        )
        attribute_inheritance = query_inheritance.query_inheritance_add_inherited_attribute(
            kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST])

        plantuml_string = diagram_generator_fana.show_function_context(kwargs['diagram_object_str'],
                                                                       kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                                       kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                                                                       kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
                                                                       kwargs[XML_DICT_KEY_0_DATA_LIST],
                                                                       kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
                                                                       kwargs[XML_DICT_KEY_13_TYPE_LIST])

        query_inheritance.query_inheritance_remove_inherited_object(
            consumed_flow_inheritance,
            kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
            **kwargs
        )
        query_inheritance.query_inheritance_remove_inherited_object(
            produced_flow_inheritance,
            kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
            **kwargs
        )
        query_inheritance.query_inheritance_remove_inherited_object_children(
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            derived_child_id=child_inheritance[2]
        )
        query_inheritance.query_inheritance_remove_inherited_attribute(
            kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
            attribute_inheritance
        )

    elif kwargs['diagram_object_str'] in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_6_STATE_LIST]):
        plantuml_string = show_states_chain([kwargs['diagram_object_str']],
                                            kwargs[XML_DICT_KEY_6_STATE_LIST],
                                            kwargs[XML_DICT_KEY_7_TRANSITION_LIST])

    elif kwargs['diagram_object_str'] in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]):
        child_inheritance = query_inheritance.query_inheritance_add_inherited_object_children(
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
            level=None
        )
        attribute_inheritance = query_inheritance.query_inheritance_add_inherited_attribute(
            kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
            kwargs[XML_DICT_KEY_3_FUN_INTF_LIST]
        )
        func_alloc_inheritance = query_inheritance.query_inheritance_add_inherited_object(
            kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            **kwargs
        )
        fun_inter_alloc_inheritance = query_inheritance.query_inheritance_add_inherited_object(
            kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
            kwargs[XML_DICT_KEY_0_DATA_LIST],
            **kwargs
        )

        plantuml_string = diagram_generator_farch.show_fun_elem_context(kwargs['diagram_object_str'],
                                                                        kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
                                                                        kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                                        kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                                                                        kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
                                                                        kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
                                                                        kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
                                                                        kwargs[XML_DICT_KEY_0_DATA_LIST])

        query_inheritance.query_inheritance_remove_inherited_object_children(
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
            derived_child_id=child_inheritance[2]
        )
        query_inheritance.query_inheritance_remove_inherited_attribute(
            kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
            attribute_inheritance
        )
        query_inheritance.query_inheritance_remove_inherited_object(
            func_alloc_inheritance,
            None,
            **kwargs)
        query_inheritance.query_inheritance_remove_inherited_object(
            fun_inter_alloc_inheritance,
            None,
            **kwargs)
    else:
        Logger.set_warning(__name__,
                           f"Jarvis does not know the function {kwargs['diagram_object_str']} or "
                           f"{kwargs['diagram_object_str']} is not a valid "
                           f"Function/State/Functional Element name/alias")

    return plantuml_string


def case_decomposition_diagram(**kwargs):
    """Case for 'show decomposition <functional_element>/<function>'"""
    plantuml_string = None

    if ' at level ' in kwargs['diagram_object_str']:
        splitted_str = re.split(" at level ", kwargs['diagram_object_str'])
        diagram_object_str = splitted_str[0]
        try:
            diagram_level = int(splitted_str[1])
            if diagram_level == 0:
                Logger.set_error(__name__,
                                 "Invalid level, please choose a valid level >= 1")
                return plantuml_string
        except ValueError:
            Logger.set_error(__name__,
                             "Invalid level, please choose a valid level >= 1")
            return plantuml_string
    else:
        diagram_object_str = kwargs['diagram_object_str']
        diagram_level = None

    v_inheritance = query_inheritance.query_inheritance_add_inherited_view(kwargs[XML_DICT_KEY_12_VIEW_LIST],
                                                                           kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                                           kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])

    # Check view if activated and filter allocated item
    function_list = util.get_object_list_from_view(diagram_object_str,
                                                   kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                   kwargs[XML_DICT_KEY_12_VIEW_LIST])

    if len(function_list) > 0:
        _, consumer_list, producer_list = \
            util.get_cons_prod_from_view_allocated_data(kwargs[XML_DICT_KEY_0_DATA_LIST],
                                                        kwargs[XML_DICT_KEY_12_VIEW_LIST],
                                                        kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                                                        kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
                                                        function_list)
    else:
        consumer_list = []
        producer_list = []

    if diagram_object_str in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_1_FUNCTION_LIST]):
        child_inheritance = query_inheritance.query_inheritance_add_inherited_object_children(
            function_list,
            level=diagram_level
        )
        attribute_inheritance = query_inheritance.query_inheritance_add_inherited_attribute(
            kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
            function_list
        )

        plantuml_string = diagram_generator_fana.show_function_decomposition(diagram_object_str,
                                                                             function_list,
                                                                             consumer_list,
                                                                             producer_list,
                                                                             kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
                                                                             kwargs[XML_DICT_KEY_13_TYPE_LIST],
                                                                             diagram_level=diagram_level)

        query_inheritance.query_inheritance_remove_inherited_object_children(
            function_list,
            derived_child_id=child_inheritance[2]
        )
        query_inheritance.query_inheritance_remove_inherited_attribute(
            kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
            attribute_inheritance
        )
    elif diagram_object_str in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]):
        fun_elem_list = util.get_object_list_from_view(diagram_object_str,
                                                       kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
                                                       kwargs[XML_DICT_KEY_12_VIEW_LIST])

        if len(fun_elem_list) > 0:
            child_inheritance = query_inheritance.query_inheritance_add_inherited_object_children(
                function_list,
                fun_elem_list,
                level=diagram_level
            )
            attribute_inheritance = query_inheritance.query_inheritance_add_inherited_attribute(
                kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
                function_list,
                fun_elem_list,
                kwargs[XML_DICT_KEY_3_FUN_INTF_LIST]
            )
            func_alloc_inheritance = query_inheritance.query_inheritance_add_inherited_object(
                fun_elem_list,
                function_list,
                **kwargs
            )
            fun_inter_alloc_inheritance = query_inheritance.query_inheritance_add_inherited_object(
                kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
                kwargs[XML_DICT_KEY_0_DATA_LIST],
                **kwargs
            )

            plantuml_string = diagram_generator_farch.show_fun_elem_decomposition(diagram_object_str,
                                                                                  function_list,
                                                                                  consumer_list,
                                                                                  producer_list,
                                                                                  fun_elem_list,
                                                                                  kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
                                                                                  kwargs[XML_DICT_KEY_0_DATA_LIST],
                                                                                  kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
                                                                                  diagram_level)

            query_inheritance.query_inheritance_remove_inherited_object_children(
                function_list,
                fun_elem_list,
                derived_child_id=child_inheritance[2]
            )
            query_inheritance.query_inheritance_remove_inherited_attribute(
                kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
                attribute_inheritance
            )
            query_inheritance.query_inheritance_remove_inherited_object(
                func_alloc_inheritance,
                None,
                **kwargs
            )
            query_inheritance.query_inheritance_remove_inherited_object(
                fun_inter_alloc_inheritance,
                None,
                **kwargs
            )
        # Else do nothing
    elif diagram_object_str in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST]):
        phy_elem_list = util.get_object_list_from_view(diagram_object_str,
                                                       kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST],
                                                       kwargs[XML_DICT_KEY_12_VIEW_LIST])

        if len(phy_elem_list) > 0:
            plantuml_string = diagram_generator_parch.show_phy_elem_decomposition(diagram_object_str,
                                                                                  phy_elem_list,
                                                                                  kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST],
                                                                                  kwargs[XML_DICT_KEY_5_PHY_INTF_LIST])
        # Else do nothing

    else:
        Logger.set_warning(__name__,
                           f"Jarvis does not know the object {diagram_object_str}"
                           f"(i.e. it is not a function, nor a functional element)")

    query_inheritance.query_inheritance_remove_inherited_view(kwargs[XML_DICT_KEY_12_VIEW_LIST], v_inheritance)

    return plantuml_string


def case_chain_diagram(**kwargs):
    """Case for 'show chain <states>/<functions>'"""
    plantuml_string = None

    object_list_str = jarvis_util.cut_string(kwargs['diagram_object_str'])

    if len(object_list_str) > 0:
        xml_function_name_list = query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_1_FUNCTION_LIST])
        result_function = all(t in xml_function_name_list for t in object_list_str)

        xml_state_name_list = query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_6_STATE_LIST])
        result_state = all(t in xml_state_name_list for t in object_list_str)

        xml_fun_elem_name_list = query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
        result_fun_elem = all(t in xml_fun_elem_name_list for t in object_list_str)

        if result_function:
            function_list = util.get_object_list_from_view(object_list_str,
                                                           kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                           kwargs[XML_DICT_KEY_12_VIEW_LIST])

            if len(function_list) > 0:
                consumed_flow_inheritance = query_inheritance.query_inheritance_add_inherited_object(
                    function_list,
                    kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                    **kwargs
                )
                produced_flow_inheritance = query_inheritance.query_inheritance_add_inherited_object(
                    function_list,
                    kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
                    **kwargs
                )
                _, consumer_list, producer_list = \
                    util.get_cons_prod_from_view_allocated_data(kwargs[XML_DICT_KEY_0_DATA_LIST],
                                                                kwargs[XML_DICT_KEY_12_VIEW_LIST],
                                                                kwargs[
                                                                    XML_DICT_KEY_14_FUN_CONS_LIST],
                                                                kwargs[
                                                                    XML_DICT_KEY_15_FUN_PROD_LIST],
                                                                function_list)

                plantuml_string = diagram_generator_chain.show_function_chain(object_list_str,
                                                                              function_list,
                                                                              consumer_list,
                                                                              producer_list,
                                                                              kwargs[XML_DICT_KEY_13_TYPE_LIST],
                                                                              kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST])

                query_inheritance.query_inheritance_remove_inherited_object(
                    consumed_flow_inheritance,
                    kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                    **kwargs
                )
                query_inheritance.query_inheritance_remove_inherited_object(
                    produced_flow_inheritance,
                    kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
                    **kwargs
                )
            else:
                Logger.set_warning(__name__,
                                   f"Nothing to display for the selected view")
        elif result_fun_elem:
            fun_elem_list_from_view = util.get_object_list_from_view(object_list_str,
                                                                     kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
                                                                     kwargs[XML_DICT_KEY_12_VIEW_LIST])

            if len(fun_elem_list_from_view) > 0:
                fun_elem_list = set()
                function_list = set()

                function_list_from_view = util.get_object_list_from_view(object_list_str,
                                                                         kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                                         kwargs[XML_DICT_KEY_12_VIEW_LIST])

                for i in object_list_str:
                    for fun_elem in fun_elem_list_from_view:
                        if i == fun_elem.name or i == fun_elem.alias:
                            fun_elem_list.add(fun_elem)

                            if len(fun_elem.allocated_function_list) > 0:
                                for allocated_function_id in fun_elem.allocated_function_list:
                                    for function in kwargs[XML_DICT_KEY_1_FUNCTION_LIST]:
                                        if function.id == allocated_function_id and function in function_list_from_view:
                                            util.get_fun_elem_function_list(function, function_list, fun_elem)
                            else:
                                Logger.set_info(__name__,
                                                f"No function allocated to {fun_elem.name} (no display)")

                new_function_list, consumer_list, producer_list = \
                    util.get_cons_prod_from_view_allocated_data(kwargs[XML_DICT_KEY_0_DATA_LIST],
                                                                kwargs[XML_DICT_KEY_12_VIEW_LIST],
                                                                kwargs[
                                                                    XML_DICT_KEY_14_FUN_CONS_LIST],
                                                                kwargs[
                                                                    XML_DICT_KEY_15_FUN_PROD_LIST],
                                                                function_list)

                plantuml_string = diagram_generator_chain.show_fun_elem_chain(object_list_str,
                                                                              new_function_list,
                                                                              consumer_list,
                                                                              producer_list,
                                                                              fun_elem_list,
                                                                              kwargs[XML_DICT_KEY_13_TYPE_LIST],
                                                                              kwargs[XML_DICT_KEY_11_ATTRIBUTE_LIST])
            else:
                Logger.set_warning(__name__,
                                   f"Nothing to display for the selected view")
        elif result_state:
            state_list = util.get_object_list_from_view(object_list_str,
                                                        kwargs[XML_DICT_KEY_6_STATE_LIST],
                                                        kwargs[XML_DICT_KEY_12_VIEW_LIST])

            if len(state_list) > 0:
                transition_list = util.filter_allocated_item_from_view(kwargs[XML_DICT_KEY_7_TRANSITION_LIST],
                                                                       kwargs[XML_DICT_KEY_12_VIEW_LIST])

                plantuml_string = show_states_chain(object_list_str, state_list, transition_list)
            else:
                Logger.set_warning(__name__,
                                   f"Nothing to display for the selected view")
        else:
            Logger.set_warning(__name__,
                               f"Jarvis does not know the object(s): {kwargs['diagram_object_str']}"
                               f"(i.e. it is not a function, nor a functional element, nor a state)")
    else:
        Logger.set_error(__name__,
                         f"{kwargs['diagram_object_str']} is not a valid chain")

    return plantuml_string


def case_sequence_diagram(**kwargs):
    """Case for 'show sequence <functional_elements>/<functions>/<functional_interface>'"""
    plantuml_string = None
    object_list_str = re.split(r',(?![^[]*\])', kwargs['diagram_object_str'].replace(", ", ","))
    object_list_str = [s.rstrip() for s in object_list_str]
    if object_list_str:
        if len(object_list_str) == 1 and \
                any(s == object_list_str[0] for s in
                    query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_3_FUN_INTF_LIST])):
            plantuml_string = get_fun_inter_sequence_diagram(object_list_str.pop(), **kwargs)
        elif len(object_list_str) >= 1:
            # Check view if activated and filter allocated item,
            # if not activated then no item filtered
            # if not any item under view return string
            xml_data_list = util.filter_allocated_item_from_view(kwargs[XML_DICT_KEY_0_DATA_LIST],
                                                                 kwargs[XML_DICT_KEY_12_VIEW_LIST])

            if len(xml_data_list) > 0:
                if all(i in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_1_FUNCTION_LIST])
                       for i in object_list_str):

                    if len(xml_data_list) != len(kwargs[XML_DICT_KEY_0_DATA_LIST]):
                        xml_cons = [i for i in kwargs[XML_DICT_KEY_14_FUN_CONS_LIST]
                                    if any(a == i[0] for a in [d for d in xml_data_list])]
                        xml_prod = [i for i in kwargs[XML_DICT_KEY_15_FUN_PROD_LIST]
                                    if any(a == i[0] for a in [d for d in xml_data_list])]
                    else:
                        xml_cons = kwargs[XML_DICT_KEY_14_FUN_CONS_LIST]
                        xml_prod = kwargs[XML_DICT_KEY_15_FUN_PROD_LIST]

                    plantuml_string = show_functions_sequence(object_list_str,
                                                              kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                              xml_cons,
                                                              xml_prod,
                                                              xml_data_list)

                elif all(i in query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
                         for i in object_list_str):
                    if len(xml_data_list) != len(kwargs[XML_DICT_KEY_0_DATA_LIST]):
                        kwargs[XML_DICT_KEY_14_FUN_CONS_LIST] = \
                            [i for i in kwargs[XML_DICT_KEY_14_FUN_CONS_LIST]
                             if any(a == i[0] for a in [d for d in xml_data_list])]
                        kwargs[XML_DICT_KEY_15_FUN_PROD_LIST] = \
                            [i for i in kwargs[XML_DICT_KEY_15_FUN_PROD_LIST]
                             if any(a == i[0] for a in [d for d in xml_data_list])]
                    kwargs[XML_DICT_KEY_0_DATA_LIST] = xml_data_list
                    plantuml_string = get_fun_elem_sequence_diagram(object_list_str, **kwargs)

                else:
                    Logger.set_error(__name__,
                                     f"{kwargs['diagram_object_str']} is not a valid sequence, available sequences "
                                     f"are:\n"
                                     f"- show sequence Function_A, Function_B, ...\n"
                                     f"- show sequence Functional_element_A, Functional_element_B, ...\n"
                                     f"- show sequence Functional_interface\n")

    return plantuml_string


def case_state_diagram(**kwargs):
    """Case for 'show state <functional_element>'"""
    plantuml_string = None
    xml_fun_elem_name_list = query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
    if kwargs['diagram_object_str'] in xml_fun_elem_name_list:
        plantuml_string = show_fun_elem_state_machine(kwargs['diagram_object_str'],
                                                      kwargs[XML_DICT_KEY_6_STATE_LIST],
                                                      kwargs[XML_DICT_KEY_7_TRANSITION_LIST],
                                                      kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST])
    else:
        Logger.set_error(__name__,
                         f"Jarvis does not know the functional Element {kwargs['diagram_object_str']}")

    return plantuml_string


def case_state_sequence_diagram(**kwargs):
    """Case for 'show state sequence <state>'"""
    plantuml_string = None
    xml_state_name_list = query_object.query_object_name_in_list(kwargs[XML_DICT_KEY_6_STATE_LIST])
    if kwargs['diagram_object_str'] in xml_state_name_list:
        plantuml_string = show_state_allocated_function(kwargs['diagram_object_str'],
                                                        kwargs[XML_DICT_KEY_6_STATE_LIST],
                                                        kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                                                        kwargs[XML_DICT_KEY_14_FUN_CONS_LIST],
                                                        kwargs[XML_DICT_KEY_15_FUN_PROD_LIST],
                                                        kwargs[XML_DICT_KEY_0_DATA_LIST])
    else:
        Logger.set_error(__name__,
                         f"Jarvis does not know the State {kwargs['diagram_object_str']}")

    return plantuml_string


def case_no_diagram(**kwargs):
    """Default Case when no command has been found"""
    Logger.set_warning(__name__,
                       f"Jarvis does not understand the command {kwargs['diagram_type_str']}")


def show_state_allocated_function(state_str, state_list, function_list, xml_consumer_function_list,
                                  xml_producer_function_list, xml_data_list):
    """Creates lists with desired objects for <state> function's allocation, send them to
    plantuml_adapter.py then returns plantuml_text"""
    allocated_function_id_list = set()
    state_name = ''
    for state in state_list:
        if state_str in (state.name, state.alias):
            if not state.allocated_function_list:
                Logger.set_info(__name__,
                                f"No function allocated to {state.name} (no display)")
                return None

            state_name = state.name
            for fun_id in state.allocated_function_list:
                allocated_function_id_list.add(fun_id)

    for function in function_list:
        if function.id in allocated_function_id_list.copy():
            allocated_function_id_list.remove(function.id)
            allocated_function_id_list.add(function.name)

    diagram_str = show_functions_sequence(allocated_function_id_list, function_list,
                                          xml_consumer_function_list, xml_producer_function_list,
                                          xml_data_list, True)

    diagram_str = f'box "{state_name}"\n{diagram_str}end box\n'

    Logger.set_info(__name__,
                    f"Function Sequence Diagram for {state_str} generated")

    return diagram_str


def show_fun_elem_state_machine(fun_elem_str, xml_state_list, xml_transition_list,
                                xml_fun_elem_list):
    """Creates lists with desired objects for <functional_element> state, send them to
    plantuml_adapter.py then returns plantuml_text"""
    new_fun_elem_list = set()
    plantuml_text = None

    main_fun_elem = query_object.query_object_by_name(fun_elem_str, **{XML_DICT_KEY_2_FUN_ELEM_LIST: xml_fun_elem_list})
    if main_fun_elem:
        if main_fun_elem.allocated_state_list:
            new_fun_elem_list.add(main_fun_elem)

            new_state_list = {s for s in xml_state_list if s.id in main_fun_elem.allocated_state_list}

            new_transition_list = util.get_transition_list(new_state_list, xml_transition_list)

            plantuml_text = plantuml_adapter.get_state_machine_diagram(new_state_list,
                                                                       new_transition_list,
                                                                       xml_fun_elem_list)

            Logger.set_info(__name__,
                            f"State Machine Diagram for {fun_elem_str} generated")
        else:
            Logger.set_error(__name__,
                             f"No state allocated to {main_fun_elem.name} (no display)")
    else:
        Logger.set_error(__name__,
                         f"Element {fun_elem_str} is not a functional element (no display)")

    return plantuml_text


def show_states_chain(state_list_str, xml_state_list, xml_transition_list):
    """Creates lists with desired objects for <states> chain, send them to plantuml_adapter.py
    then returns plantuml_text"""
    new_state_list = set()
    new_transition_list = set()
    context_state_list = set()
    spaced_state_list = ", ".join(state_list_str)

    for state_str in state_list_str:
        for state in xml_state_list:
            if state_str in (state.name, state.alias):
                state.child_list.clear()
                state.set_parent(None)
                new_state_list.add(state)
            else:
                context_state_list.add(state)

    if len(state_list_str) > 1:
        # In case of chain diagram, discard the context
        context_state_list = new_state_list
    # Else do nothing

    for state in new_state_list.copy():
        # State list depends on transition reachable from the state
        for transition in xml_transition_list:
            if transition.source == state.id:
                for context_state in context_state_list:
                    if transition.destination == context_state.id:
                        context_state.child_list.clear()
                        context_state.set_parent(None)
                        new_state_list.add(context_state)
                        new_transition_list.add(transition)
            # Else do nothing
            if transition.destination == state.id:
                for context_state in context_state_list:
                    if transition.source == context_state.id:
                        context_state.child_list.clear()
                        context_state.set_parent(None)
                        new_state_list.add(context_state)
                        new_transition_list.add(transition)
            # Else do nothing

    plantuml_text = plantuml_adapter.get_state_machine_diagram(sorted(new_state_list, key=lambda x: x.name,
                                                                      reverse=False),
                                                               sorted(new_transition_list, key=lambda x: x.name,
                                                                      reverse=False))
    if len(state_list_str) == 1:
        Logger.set_info(__name__,
                        f"Context Diagram {str(spaced_state_list)} generated")
    else:
        Logger.set_info(__name__,
                        f"Chain Diagram {str(spaced_state_list)} generated")

    return plantuml_text


def show_functions_sequence(function_name_list, xml_function_list, xml_consumer_function_list,
                            xml_producer_function_list, xml_data_list, str_out=False):
    """Creates lists with desired objects for <functions> sequence, send them to plantuml_adapter.py
    then returns plantuml_text"""
    new_function_list = set()

    for function_name in function_name_list:
        fun = query_object.query_object_by_name(function_name, **{XML_DICT_KEY_1_FUNCTION_LIST: xml_function_list})
        if fun:
            fun.child_list.clear()
            new_function_list.add(fun)
        else:
            Logger.set_warning(__name__, f'{function_name} is unknown')

    new_consumer_list = util.get_cons_or_prod_paired(new_function_list,
                                                     xml_consumer_function_list,
                                                     xml_producer_function_list)

    new_producer_list = util.get_cons_or_prod_paired(new_function_list,
                                                     xml_producer_function_list,
                                                     xml_consumer_function_list)
    # (Re)Filter data_list with only produced(same data in consumed since paired) and functions
    # asked for sequence i.e. new_function_list used in get_cons_or_prod_paired()
    # => TBC/TBT
    new_data_list = {s for s in xml_data_list if any(s in j for j in new_producer_list)}

    for new_data in new_data_list:
        for pred in new_data.predecessor_list.copy():
            if pred not in new_data_list:
                new_data.predecessor_list.remove(pred)

    plantuml_text = plantuml_adapter.get_sequence_diagram(new_function_list,
                                                          new_consumer_list,
                                                          new_producer_list,
                                                          {},
                                                          new_data_list, str_out)
    if not str_out:
        Logger.set_info(__name__,
                        "Sequence Diagram " + str(", ".join(function_name_list)) + " generated")

    return plantuml_text


def get_fun_inter_sequence_diagram(fun_inter_str, **kwargs):
    """
    Check and get all "show sequence Fun_inter" strings, find Fun_inter obj and then get/filter
    needed lists for plantuml_adapter.
    Args:
        fun_inter_str: functional interface name/alias from input cell
        **kwargs: whole lists

    Returns:
        plantuml_text (str) : plantuml text
    """
    new_consumer_list = []
    new_producer_list = []
    new_fun_elem_list = set()
    fun_inter = query_object.query_object_by_name(
        fun_inter_str, **{XML_DICT_KEY_3_FUN_INTF_LIST: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST]})

    if fun_inter:
        data_list_fun_inter = question_answer.get_fun_intf_data(fun_inter, None, False, **kwargs)['data']
        for elem in data_list_fun_inter:
            fun_elem_data = None
            if elem['Last consumer Functional element(s)']:
                fun_elem_cons = query_object.query_object_by_name(
                    elem['Last consumer Functional element(s)'].pop(),
                    **{XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]})
                fun_elem_data = query_object.query_object_by_name(
                    elem['Data'],
                    **{XML_DICT_KEY_0_DATA_LIST: kwargs[XML_DICT_KEY_0_DATA_LIST]})
            else:
                fun_elem_cons = []

            if elem['Last producer Functional element(s)']:
                fun_elem_prod = query_object.query_object_by_name(
                    elem['Last producer Functional element(s)'].pop(),
                    **{XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]})
                fun_elem_data = query_object.query_object_by_name(
                    elem['Data'],
                    **{XML_DICT_KEY_0_DATA_LIST: kwargs[XML_DICT_KEY_0_DATA_LIST]})
            else:
                fun_elem_prod = []

            if fun_elem_cons and fun_elem_prod:
                new_consumer_list.append([fun_elem_data, fun_elem_cons])
                new_producer_list.append([fun_elem_data, fun_elem_prod])
                new_fun_elem_list.add(fun_elem_cons)
                new_fun_elem_list.add(fun_elem_prod)
            # Else do nothing

    if new_consumer_list and new_producer_list:
        plantuml_text = plantuml_adapter.get_sequence_diagram(new_fun_elem_list,
                                                              new_consumer_list,
                                                              new_producer_list,
                                                              {},
                                                              kwargs[XML_DICT_KEY_0_DATA_LIST])

        return plantuml_text

    else:
        Logger.set_warning(__name__,
                           f"No data found for {fun_inter.name}")


def get_fun_elem_sequence_diagram(fun_elem_str, **kwargs):
    """
    Check and get all "show sequence Fun_elem_A, Fun_elem_B, ..." strings, find objects and
    then get/filter needed lists for plantuml_adapter.
    Args:
        fun_elem_str: functional elements name/alias from input cell
        **kwargs: dict with whole lists/sets

    Returns:
        plantuml_text (str) : plantuml_text
    """
    new_consumer_list = []
    new_producer_list = []

    new_fun_elem_list = {
        query_object.query_object_by_name(i, **{XML_DICT_KEY_2_FUN_ELEM_LIST: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST]})
        for i in fun_elem_str
    }

    for fun_elem in new_fun_elem_list:
        temp_fun_set = question_answer.get_allocation_object(
            fun_elem,
            kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
            **kwargs
        )

        if isinstance(fun_elem.derived, FunctionalElement):
            get_derived_if_in_view = util.filter_allocated_item_from_view(
                {fun_elem.derived}, kwargs[XML_DICT_KEY_12_VIEW_LIST]
            )
            # If type(list) has been returned from activated View()
            # then add it's allocated func

            # TODO not used in the code
            if isinstance(get_derived_if_in_view, list):
                alloc_derived_func_set = question_answer.get_allocation_object(
                    fun_elem.derived,
                    kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
                    **kwargs
                )
                # if alloc_derived_func_set is not None and temp_fun_set is not None:
                # allocated_fun_set.update(alloc_derived_func_set)

        if temp_fun_set is not None:
            for fun in temp_fun_set:
                new_consumer_list.extend(
                    get_fun_elem_for_cons_prod_lists(
                        fun_elem, fun, kwargs[XML_DICT_KEY_14_FUN_CONS_LIST]
                    )
                )
                new_producer_list.extend(
                    get_fun_elem_for_cons_prod_lists(
                        fun_elem, fun, kwargs[XML_DICT_KEY_15_FUN_PROD_LIST]
                    )
                )

        fun_elem.child_list.clear()
        fun_elem.parent = None

    if new_consumer_list and new_producer_list:

        for i in new_consumer_list:
            if not any(i[0] in s for s in new_producer_list):
                new_consumer_list.remove(i)

        for j in new_producer_list:
            if not any(j[0] in s for s in new_consumer_list):
                new_producer_list.remove(j)

    if new_consumer_list and new_producer_list:
        plantuml_text = plantuml_adapter.get_sequence_diagram(new_fun_elem_list,
                                                              new_consumer_list,
                                                              new_producer_list,
                                                              {},
                                                              kwargs[XML_DICT_KEY_0_DATA_LIST])

        return plantuml_text

    else:
        Logger.set_warning(__name__,
                           f"Not any data allocated to interfaces exposed by {', '.join(fun_elem_str)}")


def get_fun_elem_for_cons_prod_lists(fun_elem, func_obj, cons_or_prod_list):
    """
    From cons or prod list [[data_1, function_1_str], [data_2, function_2_str], ...]
    returns [[data_1, Function(1)], [data_2, Function(2)], ...]
    """
    output = []
    for cons_or_prod in cons_or_prod_list:
        if cons_or_prod[1] == func_obj:
            output.append([cons_or_prod[0], fun_elem])

    return output
