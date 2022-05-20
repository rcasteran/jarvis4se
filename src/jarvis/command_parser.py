#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module with class & methods for parsing jarvis4se commands"""
import re
import pandas as pd
from IPython.display import display, HTML, Markdown

from . import viewpoint_orchestrator
from . import functional_orchestrator
from . import shared_orchestrator
from . import physical_orchestrator
from . import question_answer
from . import diagram_generator


class CmdParser:
    def __init__(self):
        self.commands = [
            (r"(under.*)", self.matched_under),

            (r"(?<= |\n)(.*?) is a function\b(?=.|\n)", matched_function),

            (r"(?<= |\n)(.*?) is a data(?=.\s|\n|.\n)", matched_data),

            (r"(?<= |\n)(.*?) is a state(?=.|\n)", matched_state),

            (r"(?<= |\n)(.*?) is a transition(?=.|\n)", matched_transition),

            (r"(?<= |\n)(.*?) is a functional element(?=.|\n)", matched_functional_element),

            (r"(?<= |\n)(.*?) is a functional interface(?=.|\n)", matched_functional_interface),

            (r"(?<= |\n)(.*?) is a physical element(?=.|\n)", matched_physical_element),

            (r"(?<= |\n)(.*?) is a physical interface(?=.|\n)", matched_physical_interface),

            (r"(?<= |\n)(.*?) is an attribute\b(?=.|\n)", matched_attribute),

            (r"The alias of (.*?) is ([^\.\n]*)", matched_alias),

            (r"(?<= |\n)consider ([^\.\n]*)", matched_consider),

            (r"([^\. \.\n]*) is composed of ([^\.\n]*)", matched_composition),

            (r"([^\. \.\n]*) composes ([^\.\n]*)", matched_composition),

            (r"([^\. \.\n]*) consumes ([^\.\n]*)", matched_consumer),

            (r"([^\. \.\n]*) is an input of ([^\.\n]*)", matched_consumer),

            (r"([^\. \.\n]*) produces ([^\.\n]*)", matched_producer),

            (r"([^\. \.\n]*) is an output of ([^\.\n]*)", matched_producer),

            (r"(?<= |\n)(.*?) exposes ([^\.\n]*)", matched_exposes),

            (r"(?<= |\n)(.*?) is allocated to ([^\.\n]*)", matched_allocation),

            (r"(?<= |\n)(.*?) allocates ([^\.\n]*)", matched_allocation),

            (r"(?<= |\n)delete ([^\.\n]*)", matched_delete),

            (r"The type of (.*?) is ([^\.\n]*)", matched_type),

            (r"([^\. \.\n]*) implies ([^\.\n]*)", matched_implies),

            (r"Condition for (.*?) is:([^\.\n]*)", matched_condition),

            (r"The (source|destination) of (.*?) is ([^\.\n]*)", matched_src_dest),

            (r"(?<= |\n)show (.*?)\n", matched_show),

            (r"\s([A-Za-z\s].*\?)", matched_question_mark),

            (r"list (input|output|child|data|function|transition|interface) ([^\.\n]*)",
             matched_list),

            (r"The ([^type|alias|source|destination].*?) of (.*?) is ([^\.\n]*)",
             matched_described_attribute),
        ]

    def lookup_table(self, string, **kwargs):
        """Lookup table with conditions depending on the match"""
        update_list = []
        for idx, (regex, method) in enumerate(self.commands):
            # 14, 15, 17, 20
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
                if idx in (13, 14, 16, 19):
                    result = reverse(result)
                update = method(result, **kwargs)

            elif result_chain:
                string = ''
                update = self.matched_under(result_chain, **kwargs)

            if update is not None:
                if isinstance(update, list):
                    update_list.append(*update)
                elif isinstance(update, int):
                    update_list.append(update)

        return update_list

    def matched_under(self, chain_name_str, **kwargs):
        """Get "under" declaration"""
        out = []
        for chain, rest in zip(chain_name_str[::2], chain_name_str[1::2]):
            chain = chain.replace("under ", "")
            out.append(viewpoint_orchestrator.add_chain(chain,
                                                        kwargs['xml_chain_list'],
                                                        kwargs['output_xml']))
            self.lookup_table(rest, **kwargs)
        if 1 in out:
            return 1
        else:
            return 0


def matched_function(function_name_str_list, **kwargs):
    """Get function's declaration (does not match if "function" is not at the end)"""
    out = functional_orchestrator.add_function_by_name(function_name_str_list,
                                                       kwargs['xml_function_list'],
                                                       kwargs['output_xml'])
    return out


def matched_data(data_str_list, **kwargs):
    """Get data declaration"""
    out = functional_orchestrator.add_data(data_str_list, kwargs['xml_data_list'],
                                           kwargs['output_xml'])
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


def matched_functional_element(functional_elem_name_str_list, **kwargs):
    """Get Functional element's declaration"""
    out = functional_orchestrator.add_fun_elem_by_name(functional_elem_name_str_list,
                                                       kwargs['xml_fun_elem_list'],
                                                       kwargs['output_xml'])
    return out


def matched_functional_interface(functional_inter_name_str_list, **kwargs):
    """Get Functional interface's declaration"""
    out = functional_orchestrator.add_fun_inter_by_name(functional_inter_name_str_list,
                                                        kwargs['xml_fun_inter_list'],
                                                        kwargs['output_xml'])
    return out


def matched_physical_element(physical_elem_name_str_list, **kwargs):
    """Get Physical element's declaration"""
    out = physical_orchestrator.add_phy_elem_by_name(physical_elem_name_str_list,
                                                     kwargs['xml_phy_elem_list'],
                                                     kwargs['output_xml'])
    return out


def matched_physical_interface(physical_inter_name_str_list, **kwargs):
    """Get Physical interface's declaration"""
    out = physical_orchestrator.add_phy_inter_by_name(physical_inter_name_str_list,
                                                      kwargs['xml_phy_inter_list'],
                                                      kwargs['output_xml'])
    return out


def matched_attribute(attribute_name_str, **kwargs):
    """Get "attribute" declaration"""
    out = viewpoint_orchestrator.add_attribute(attribute_name_str,
                                               kwargs['xml_attribute_list'],
                                               kwargs['output_xml'])
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
                                                    kwargs['xml_chain_list'],
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
                                                        kwargs['xml_chain_list'],
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


def matched_show(diagram_name_str, **kwargs):
    """Get "show" declaration"""
    out = diagram_generator.filter_show_command(diagram_name_str, **kwargs)
    if out:
        hyper = get_hyperlink(out)
        display(HTML(hyper))
        print("Overview :")
        display(Markdown(f'![figure]({out})'))


def get_hyperlink(path):
    """Convert file path into clickable form."""
    text = "Click to open in new tab"
    # convert the url into link
    return f'<a href="{path}" target="_blank">{text}</a>'


def matched_question_mark(question_str, **kwargs):
    """Gets "?" declaration"""
    out = question_answer.find_question(question_str, **kwargs)
    if out:
        for elem in out:
            if isinstance(elem, str):
                print(elem)
            else:
                display(elem)


def matched_list(object_str, **kwargs):
    """Gets list declaration"""
    out = question_answer.get_object_list(object_str, **kwargs)
    if out:
        for i in out:
            if "Child" in i[0] or "Function" in i[0]:
                title = i.pop(0)
                df = pd.DataFrame(i, columns=["Object's name", "Relationship's type"])
                df = df.T
                # Could be usefull to add it with button next to table but needs ipywidgets ...
                # df.to_clipboard(excel=True)
                df = df.style\
                    .set_caption(title)\
                    .set_properties(**{'white-space': 'nowrap'})
                display(df)
            elif "Input" in i[0]:
                title = i.pop(0)
                df = pd.DataFrame(i, columns=["Data name", "Producer"])
                df = df.T
                df = df.style\
                    .set_caption(title)\
                    .set_properties(**{'white-space': 'nowrap'})
                df = df.to_html().replace("\\n", "<br>")
                display(HTML(df))
            elif "Output" in i[0]:
                title = i.pop(0)
                df = pd.DataFrame(i, columns=["Data name", "Consumer"])
                df = df.T
                df = df.style\
                    .set_caption(title)\
                    .set_properties(**{'white-space': 'nowrap'})
                df = df.to_html().replace("\\n", "<br>")
                display(HTML(df))
            elif "Data" in i[0] or "Transition" in i[0]:
                if "Transition" in i[0]:
                    first = 3
                    last = 4
                else:
                    first = 1
                    last = 5
                title = i.pop(0)
                df = pd.DataFrame(i)
                df = df.T
                for idx in range(first, last):
                    df.iloc[idx] = df.iloc[idx].str.join("\\n")
                df = df.style\
                    .set_caption(title)\
                    .set_properties(**{'white-space': 'nowrap'})
                df = df.to_html().replace("\\n", "<br>")
                display(HTML(df))
            elif "Interface" in i[0]:
                title = i.pop(0)
                df = pd.DataFrame(i,
                                  columns=["Interface ", "Last connected functional element"])
                df = df.T
                df = df.style\
                    .set_caption(title)\
                    .set_properties(**{'white-space': 'nowrap'})
                df = df.to_html().replace("\\n", "<br>")
                display(HTML(df))


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
