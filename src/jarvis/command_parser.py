#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module with class & methods for parsing jarvis4se commands"""
import re
from IPython.display import display, HTML, Markdown

from . import viewpoint_orchestrator
from . import functional_orchestrator
from . import shared_orchestrator
from .question_answer import get_object_list, get_pandas_table, find_question
from .diagram_generator import filter_show_command


class CmdParser:
    def __init__(self, generator):
        self.commands = [
            (r"(under.*)", self.matched_under),

            (r"(?<= |\n)(.*?) extends ([^.|\n]*)", matched_extend),

            (r"(?<= |\n)(.*?) is a ([^state|transition][^\.\n]*)",
             matched_specific_obj),

            (r"(?<= |\n)(.*?) is a state(?=.|\n)", matched_state),

            (r"(?<= |\n)(.*?) is a transition(?=.|\n)", matched_transition),

            (r"(?<= |\n)(.*?) is an attribute\b(?=.|\n)", matched_attribute),

            (r"(?<= |\n)(.*?) inherits from ([^.|\n]*)", matched_inherits),

            (r"The alias of (.*?) is ([^.|\n]*)", matched_alias),

            (r"(?<= |\n)consider ([^.|\n]*)", matched_consider),

            (r"([^\. \.\n]*) is composed of ([^.|\n]*)", matched_composition),

            (r"([^. |.|\n].*) composes ([^.|\n]*)", matched_composition),

            (r"([^. |.|\n].*) consumes ([^.|\n]*)", matched_consumer),

            (r"([^. |.|\n].*) is an input of ([^.|\n]*)", matched_consumer),

            (r"([^. |.|\n].*) produces ([^.|\n]*)", matched_producer),

            (r"([^. |.|\n].*) is an output of ([^.|\n]*)", matched_producer),

            (r"(?<= |\n)(.*?) exposes ([^.|\n]*)", matched_exposes),

            (r"(?<= |\n)(.*?) is allocated to ([^.|\n]*)", matched_allocation),

            (r"(?<= |\n)(.*?) allocates ([^.|\n]*)", matched_allocation),

            (r"(?<= |\n)delete ([^.|\n]*)", matched_delete),

            (r"The type of (.*?) is ([^.|\n]*)", matched_type),

            (r"([^. |.|\n].*) implies ([^.|\n]*)", matched_implies),

            (r"Condition for (.*?) is:([^.|\n]*)", matched_condition),

            (r"The (source|destination) of (.*?) is ([^.|\n]*)", matched_src_dest),

            (r"(?<= |\n)show (.*?)\n", self.matched_show),

            (r"\s([A-Za-z\s].*\?)", matched_question_mark),

            (r"list (input|output|child|data|function|transition|interface) ([^.|\n]*)",
             matched_list),

            (r"The ([^type|alias|source|destination].*?) of (.*?) is ([^.|\n]*)",
             matched_described_attribute),
        ]
        self.reverse = (r"([^. |.|\n].*) composes ([^.|\n]*)",
                        r"([^. |.|\n].*) consumes ([^.|\n]*)",
                        r"([^. |.|\n].*) produces ([^.|\n]*)",
                        r"(?<= |\n)(.*?) is allocated to ([^.|\n]*)")

        self.generator = generator

    def lookup_table(self, string, **kwargs):
        """Lookup table with conditions depending on the match"""
        update_list = []
        for regex, method in self.commands:
            result_chain = None
            result = None
            update = None
            if regex == r"(under.*)":
                result_chain = re.split(regex, string)
                del result_chain[0]
            # Only one diagram per cell can be output
            elif regex == r"(?<= |\n)show (.*?)\n":
                result = re.search(regex, string, re.MULTILINE)
            else:
                # Transform to avoid duplicated function's declaration within cells input
                result = []
                [result.append(x) for x in re.findall(regex, string, re.MULTILINE)
                 if x not in result]

            if result and not result_chain:
                # self.reverse : ("composes", "consumes", "produces", "is allocated to")
                if regex in self.reverse:
                    result = reverse(result)
                update = method(result, **kwargs)

            elif result_chain:
                string = ''
                update = self.matched_under(result_chain, **kwargs)

            if update is not None:
                if isinstance(update, int):
                    update_list.append(update)

        return update_list

    def matched_under(self, chain_name_str, **kwargs):
        """Get "under" declaration"""
        out = []
        for chain, rest in zip(chain_name_str[::2], chain_name_str[1::2]):
            chain = chain.replace("under ", "")
            out.append(viewpoint_orchestrator.add_view(chain,
                                                       kwargs['xml_view_list'],
                                                       kwargs['output_xml']))
            self.lookup_table(rest, **kwargs)
        if 1 in out:
            return 1

        return 0

    def matched_show(self, diagram_name_str, **kwargs):
        """Get "show" declaration"""
        out = filter_show_command(diagram_name_str, **kwargs)
        if out:
            url = self.generator.get_diagram_url(out)
            hyper = get_hyperlink(url)
            display(HTML(hyper))
            print("Overview :")
            display(Markdown(f'![figure]({url})'))


def matched_extend(type_str_list, **kwargs):
    """Get extend declaration"""
    out = viewpoint_orchestrator.check_set_extends(type_str_list,
                                                   kwargs['xml_type_list'],
                                                   kwargs['output_xml'])
    return out


def matched_specific_obj(obj_type_str, **kwargs):
    """Get "is a" declaration"""
    out = shared_orchestrator.check_add_specific_obj_by_type(obj_type_str, **kwargs)
    return out


def matched_state(state_name_str_list, **kwargs):
    """Get state's declaration"""
    out = functional_orchestrator.add_state_by_name(state_name_str_list,
                                                    kwargs['xml_state_list'],
                                                    kwargs['output_xml'])
    return out


def matched_transition(transition_name_str_list, **kwargs):
    """Get transition's declaration"""
    out = functional_orchestrator.add_transition_by_name(transition_name_str_list,
                                                         kwargs['xml_transition_list'],
                                                         kwargs['output_xml'])
    return out


def matched_attribute(attribute_name_str, **kwargs):
    """Get "attribute" declaration"""
    out = viewpoint_orchestrator.add_attribute(attribute_name_str,
                                               kwargs['xml_attribute_list'],
                                               kwargs['output_xml'])
    return out


def matched_inherits(inherits_str, **kwargs):
    """Get inherits from declaration"""
    out = shared_orchestrator.check_add_inheritance(inherits_str, **kwargs)
    return out


def matched_alias(alias_str_list, **kwargs):
    """Get "alias" declaration"""
    out = shared_orchestrator.check_set_object_alias(alias_str_list, **kwargs)
    return out


def matched_consider(consider_str_list, **kwargs):
    """Get "consider" declaration"""
    out = viewpoint_orchestrator.check_get_consider(consider_str_list,
                                                    kwargs['xml_function_list'],
                                                    kwargs['xml_fun_elem_list'],
                                                    kwargs['xml_data_list'],
                                                    kwargs['xml_view_list'],
                                                    kwargs['output_xml'])
    return out


def matched_composition(parent_child_name_str_list, **kwargs):
    """Get composition relationship command (match for "is composed by' or "composes")"""
    out = shared_orchestrator.check_add_child(parent_child_name_str_list,
                                              **{
                                                  'xml_function_list': kwargs['xml_function_list'],
                                                  'xml_state_list': kwargs['xml_state_list'],
                                                  'xml_fun_elem_list': kwargs['xml_fun_elem_list'],
                                                  'xml_phy_elem_list': kwargs['xml_phy_elem_list'],
                                                  'output_xml': kwargs['output_xml'],
                                              })
    return out


def matched_consumer(consumer_str_list, **kwargs):
    """Get consumer declaration"""
    out = functional_orchestrator.check_add_consumer_function(
        consumer_str_list,
        kwargs['xml_consumer_function_list'],
        kwargs['xml_producer_function_list'],
        kwargs['xml_function_list'],
        kwargs['xml_data_list'],
        kwargs['output_xml'])
    return out


def matched_producer(producer_str_list, **kwargs):
    """Get producer declaration"""
    out = functional_orchestrator.check_add_producer_function(
        producer_str_list,
        kwargs['xml_consumer_function_list'],
        kwargs['xml_producer_function_list'],
        kwargs['xml_function_list'],
        kwargs['xml_data_list'],
        kwargs['output_xml'])
    return out


def matched_allocation(allocation_str_list, **kwargs):
    """Get allocation declaration"""
    out = shared_orchestrator.check_add_allocation(allocation_str_list, **kwargs)
    return out


def matched_exposes(exposes_str_list, **kwargs):
    """Get 'exposes' declaration"""
    out = functional_orchestrator.check_add_exposes(exposes_str_list,
                                                    kwargs['xml_fun_elem_list'],
                                                    kwargs['xml_fun_inter_list'],
                                                    kwargs['xml_data_list'],
                                                    kwargs['output_xml'])
    return out


def matched_delete(delete_str_list, **kwargs):
    """Get delete declaration"""
    out = shared_orchestrator.check_and_delete_object(delete_str_list, **kwargs)
    return out


def matched_type(type_str_list, **kwargs):
    """Get set_type declaration"""
    out = shared_orchestrator.check_set_object_type(type_str_list, **kwargs)
    return out


def matched_implies(data_predecessor_str_set, **kwargs):
    """Get predecessor declaration"""
    out = functional_orchestrator.check_add_predecessor(data_predecessor_str_set,
                                                        kwargs['xml_data_list'],
                                                        kwargs['xml_view_list'],
                                                        kwargs['output_xml'])
    return out


def matched_condition(condition_str_list, **kwargs):
    """Get set_condition declaration"""
    out = functional_orchestrator.check_add_transition_condition(condition_str_list,
                                                                 kwargs['xml_transition_list'],
                                                                 kwargs['output_xml'])
    return out


def matched_src_dest(src_dest_str, **kwargs):
    """Get source/destination declaration for transition"""
    out = functional_orchestrator.check_add_src_dest(src_dest_str,
                                                     kwargs['xml_transition_list'],
                                                     kwargs['xml_state_list'],
                                                     kwargs['output_xml'])
    return out


def get_hyperlink(path):
    """Convert file path into clickable form."""
    text = "Click to open in new tab"
    # convert the url into link
    return f'<a href="{path}" target="_blank">{text}</a>'


def matched_question_mark(question_str, **kwargs):
    """Gets "?" declaration"""
    out = find_question(question_str, **kwargs)
    if out:
        for elem in out:
            if isinstance(elem, str):
                print(elem)
            else:
                display(elem)


def matched_list(object_str, **kwargs):
    """Gets list declaration"""
    out = get_object_list(object_str, **kwargs)
    if out:
        for i in out:
            display(HTML(get_pandas_table(i)))


def matched_described_attribute(described_attribute_str, **kwargs):
    """Get the described attribute value for an object"""
    out = viewpoint_orchestrator.check_add_object_attribute(described_attribute_str,
                                                            kwargs['xml_attribute_list'],
                                                            kwargs['xml_function_list'],
                                                            kwargs['xml_fun_elem_list'],
                                                            kwargs['xml_fun_inter_list'],
                                                            kwargs['output_xml'])
    return out


def reverse(inverted_list):
    """Reverses input tuple strings"""
    sorted_list = []
    for tuples in inverted_list:
        new_tup = ()
        for k in reversed(tuples):
            new_tup = new_tup + (k,)
        sorted_list.append(new_tup)
    return sorted_list
