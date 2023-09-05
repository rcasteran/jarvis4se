"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re
import os
import requests
from IPython.display import display, HTML, Markdown


# Modules
from jarvis.orchestrator import orchestrator_functional, orchestrator_shared, orchestrator_viewpoint, \
    orchestrator_requirement, orchestrator_object
from jarvis.query import question_answer, query_object_list
from jarvis.diagram import diagram_generator
from jarvis.handler import handler_question
from jarvis import util
from tools import get_hyperlink
from tools import Config
from tools import Logger


class CmdParser:
    def __init__(self, generator):
        self.command_list = [
            (r"under ([^.|\n]*)", self.matched_under),
            (r"([^. |\n][^.|\n]*) extends ([^.|\n]*)", orchestrator_viewpoint.check_set_extends),
            (r"([^. |\n][^.|\n]*) is a ((?!attribute)[^.|\n]*)", orchestrator_object.check_add_specific_obj_by_type),
            (r"([^. |\n][^.|\n]*) is an attribute", orchestrator_viewpoint.add_attribute),
            (r"([^. |\n][^.|\n]*) inherits from ([^.|\n]*)", orchestrator_shared.check_add_inheritance),
            (r"The alias of (.*?) is ([^.|\n]*)", orchestrator_shared.check_set_object_alias),
            (r"consider ([^.|\n]*)", orchestrator_viewpoint.check_get_consider),
            (r"([^. |\n][^.|\n]*) is composed of ([^.|\n]*)", orchestrator_shared.check_add_child),
            (r"([^. |\n][^.|\n]*) composes ([^.|\n]*)", orchestrator_shared.check_add_child),
            (r"([^. |\n][^.|\n]*) compose ([^.|\n]*)", orchestrator_shared.check_add_child),
            (r"([^. |\n][^.|\n]*) consumes ([^.|\n]*)", orchestrator_functional.check_add_consumer_function),
            (r"([^. |\n][^.|\n]*) is an input of ([^.|\n]*)", orchestrator_functional.check_add_consumer_function),
            (r"([^. |\n][^.|\n]*) produces ([^.|\n]*)", orchestrator_functional.check_add_producer_function),
            (r"([^. |\n][^.|\n]*) is an output of ([^.|\n]*)", orchestrator_functional.check_add_producer_function),
            (r"([^. |\n][^.|\n]*) exposes ([^.|\n]*)", orchestrator_functional.check_add_exposes),
            (r"([^. |\n][^.|\n]*) expose ([^.|\n]*)", orchestrator_functional.check_add_exposes),
            (r"([^. |\n][^.|\n]*) is allocated to ([^.|\n]*)", orchestrator_shared.check_add_allocation),
            (r"([^. |\n][^.|\n]*) are allocated to ([^.|\n]*)", orchestrator_shared.check_add_allocation),
            (r"([^. |\n][^.|\n]*) allocates ([^.|\n]*)", orchestrator_shared.check_add_allocation),
            (r"delete ([^.|\n]*)", orchestrator_shared.check_and_delete_object),
            (r"The type of (.*?) is ([^.|\n]*)", orchestrator_shared.check_set_object_type),
            (r"([^. |\n][^.|\n]*) implies ([^.|\n]*)", orchestrator_functional.check_add_predecessor),
            (r"([^. |\n][^.|\n]*) imply ([^.|\n]*)", orchestrator_functional.check_add_predecessor),
            (r"([^. |\n][^.|\n]*) shall ([^.|\n]*)", orchestrator_requirement.check_add_requirement),
            (r"([^. |\n][^.|\n]*) is satisfied by ([^.|\n]*)", orchestrator_requirement.check_add_allocation),
            (r"([^. |\n][^.|\n]*) are satisfied by ([^.|\n]*)", orchestrator_requirement.check_add_allocation),
            (r"([^. |\n][^.|\n]*) satisfies ([^.|\n]*)", orchestrator_requirement.check_add_allocation),
            (r"Condition for (.*?) is:([^.|\n]*)", orchestrator_functional.check_add_transition_condition),
            (r"The (source|destination) of (.*?) is ([^.|\n]*)", orchestrator_functional.check_add_src_dest),
            (r"show ([^.|\n]*)", self.matched_show),
            (r"(.*?)\?", self.matched_question_mark),
            (r"list (input|output|child|data|function|transition|interface) ([^.|\n]*)", CmdParser.matched_list),
            (r"The ((?!type|alias|source|destination).*) of (.*?) is ([^.|\n]*)",
             orchestrator_viewpoint.check_add_object_attribute)
        ]

        self.reverse_command_list = (r"([^. |\n][^.|\n]*) composes ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) compose ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) consumes ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) produces ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) is allocated to ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) are allocated to ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) is satisfied by ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) are satisfied by ([^.|\n]*)")

        self.question_list = [
            (r"What is (.*)", handler_question.question_object_info),
            (r"Is (.*) allocated", handler_question.question_object_allocation)
        ]

        self.generator = generator

    def lookup_table(self, string, **kwargs):
        """Lookup table with conditions depending on the match"""
        update_list = []
        for regex, method in self.command_list:
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
                if regex in self.reverse_command_list:
                    result = util.reverse_tuple_list(result)
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
            out.append(orchestrator_viewpoint.add_view(chain, **kwargs))
            self.lookup_table(rest, **kwargs)

        return 1 in out

    def matched_show(self, diagram_name_str, **kwargs):
        """Get "show" declaration"""
        out = diagram_generator.filter_show_command(diagram_name_str, **kwargs)

        if out:
            if Config.is_diagram_file:
                url = self.generator.get_diagram_url(out)
                # Generate and set unique identifier of length 10 integers
                identi = util.get_unique_id()

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

        return None

    def matched_question_mark(self, p_str_list, **kwargs):
        """@ingroup jarvis
        @anchor matched_question_mark
        Get question declaration for question answering

        @param[in] p_str_list : list of input strings
        @param[in] kwargs : jarvis data structure
        @return None (no xml update, no info displayed)
        """
        for regex, method in self.question_list:
            for elem in p_str_list:
                result = re.findall(regex, elem, re.MULTILINE)
                if result:
                    answer = method(result, **kwargs)
                    if answer:
                        display(answer)

        return None

    @staticmethod
    def matched_list(p_str_list, **kwargs):
        """@ingroup jarvis
        @anchor matched_list
        Get "list" declaration for listing objects

        @param[in] p_str_list : list of input strings
        @param[in] kwargs : jarvis data structure
        @return None (no xml update, no info displayed)
        """
        out = query_object_list.get_object_list(p_str_list, **kwargs)
        if out:
            for i in out:
                display(HTML(question_answer.get_pandas_table(i)))

        return None
