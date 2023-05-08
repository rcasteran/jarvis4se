# Libraries
import re
import uuid
import os
import requests
from IPython.display import display, HTML, Markdown


# Modules
from jarvis.orchestrator import functional_orchestrator, shared_orchestrator, viewpoint_orchestrator
from .question_answer import get_object_list, get_pandas_table, find_question
from jarvis.diagram import diagram_generator
from tools import get_hyperlink
from tools import Config
from tools import Logger


class CmdParser:
    def __init__(self, generator):
        self.commands = [
            (r"under ([^.|\n]*)", self.matched_under),

            (r"([^. |\n][^.|\n]*) extends ([^.|\n]*)", matched_extend),

            (r"([^. |\n][^.|\n]*) is a ((?!attribute)[^.|\n]*)",
             matched_specific_obj),

            (r"([^. |\n][^.|\n]*) is an attribute", matched_attribute),

            (r"([^. |\n][^.|\n]*) inherits from ([^.|\n]*)", matched_inherits),

            (r"The alias of (.*?) is ([^.|\n]*)", matched_alias),

            (r"consider ([^.|\n]*)", matched_consider),

            (r"([^. |\n][^.|\n]*) is composed of ([^.|\n]*)", matched_composition),

            (r"([^. |\n][^.|\n]*) composes ([^.|\n]*)", matched_composition),

            (r"([^. |\n][^.|\n]*) compose ([^.|\n]*)", matched_composition),

            (r"([^. |\n][^.|\n]*) consumes ([^.|\n]*)", matched_consumer),

            (r"([^. |\n][^.|\n]*) is an input of ([^.|\n]*)", matched_consumer),

            (r"([^. |\n][^.|\n]*) produces ([^.|\n]*)", matched_producer),

            (r"([^. |\n][^.|\n]*) is an output of ([^.|\n]*)", matched_producer),

            (r"([^. |\n][^.|\n]*) exposes ([^.|\n]*)", matched_exposes),

            (r"([^. |\n][^.|\n]*) expose ([^.|\n]*)", matched_exposes),

            (r"([^. |\n][^.|\n]*) is allocated to ([^.|\n]*)", matched_allocation),

            (r"([^. |\n][^.|\n]*) allocates ([^.|\n]*)", matched_allocation),

            (r"delete ([^.|\n]*)", matched_delete),

            (r"The type of (.*?) is ([^.|\n]*)", matched_type),

            (r"([^. |\n][^.|\n]*) implies ([^.|\n]*)", matched_implies),

            (r"([^. |\n][^.|\n]*) imply ([^.|\n]*)", matched_implies),

            (r"Condition for (.*?) is:([^.|\n]*)", matched_condition),

            (r"The (source|destination) of (.*?) is ([^.|\n]*)", matched_src_dest),

            (r"show ([^.|\n]*)", self.matched_show),

            (r"(.*?)\?", matched_question_mark),

            (r"list (input|output|child|data|function|transition|interface) ([^.|\n]*)",
             matched_list),

            (r"The ((?!type|alias|source|destination).*) of (.*?) is ([^.|\n]*)",
             matched_described_attribute),
        ]

        self.reverse = (r"([^. |\n][^.|\n]*) composes ([^.|\n]*)",
                        r"([^. |\n][^.|\n]*) compose ([^.|\n]*)",
                        r"([^. |\n][^.|\n]*) consumes ([^.|\n]*)",
                        r"([^. |\n][^.|\n]*) produces ([^.|\n]*)",
                        r"([^. |\n][^.|\n]*) is allocated to ([^.|\n]*)")

        self.generator = generator

    def lookup_table(self, string, **kwargs):
        """Lookup table with conditions depending on the match"""
        update_list = []
        for regex, method in self.commands:
            result_chain = None
            result = None
            update = None
            if regex == r"under ([^.|\n]*)":
                result_chain = re.split(regex, string)
                del result_chain[0]
            # Only one diagram per cell can be output
            elif regex == r"show ([^.|\n]*)":
                result = re.search(regex, string, re.MULTILINE)
            else:
                # Transform to avoid duplicated function's declaration within cells input
                result = []
                [result.append(x) for x in re.findall(regex, string, re.MULTILINE) if x not in result]

            if result and not result_chain:
                # self.reverse
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
        out = diagram_generator.filter_show_command(diagram_name_str, **kwargs)
        if out:
            if Config.is_diagram_file:
                url = self.generator.get_diagram_url(out)
                # Generate and set unique identifier of length 10 integers
                identi = uuid.uuid4()
                identi = str(identi.int)[:10]

                if not os.path.isdir("diagrams"):
                    os.makedirs("diagrams")

                current_file_path = str('./diagrams/Diagram' + identi + '.svg')
                try:
                    response = requests.get(url)
                    with open(current_file_path, "wb") as file_writer:
                        file_writer.write(response.content)
                    url = current_file_path
                except EnvironmentError as ex:
                    Logger.set_error(__name__,
                                     f"Unable to write the diagram {current_file_path}: {str(ex)}")
            else:
                url = self.generator.get_diagram_url(out)

            hyper = get_hyperlink(url)
            display(HTML(hyper))
            # Single display (not related to logging)
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


def matched_question_mark(question_str, **kwargs):
    """Gets "?" declaration"""
    out = find_question(question_str, **kwargs)
    if out:
        for elem in out:
            if isinstance(elem, str):
                # Single display (not related to logging)
                print(elem)
            else:
                display(elem)


def matched_list(object_str, **kwargs):
    """Gets list declaration"""
    out = get_object_list(object_str, **kwargs)
    if out:
        for i in out:
            display(HTML(get_pandas_table(i)))


def matched_described_attribute(described_attribute_str, **xml_dicts):
    """Get the described attribute value for an object"""
    out = viewpoint_orchestrator.check_add_object_attribute(
        described_attribute_str,
        **xml_dicts
        )
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
