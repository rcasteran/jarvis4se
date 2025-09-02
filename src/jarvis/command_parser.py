"""@defgroup jarvis
Jarvis module
"""
# Libraries
import re
import os
import requests
from IPython.display import display, HTML, Markdown

# Modules
import datamodel
from csv_adapter import CsvWriter3SE, CsvParser3SE
from jarvis.orchestrator import orchestrator_functional, orchestrator_shared, orchestrator_viewpoint, \
    orchestrator_viewpoint_attribute, orchestrator_viewpoint_requirement, orchestrator_object, \
    orchestrator_object_allocation, orchestrator_viewpoint_type, orchestrator_dictionary , \
    orchestrator_viewpoint_goal
from jarvis.diagram import diagram_generator
from jarvis.simulation import simulation_generator
from jarvis.handler import handler_question, handler_list
from jarvis import util
from tools import get_hyperlink
from tools import Config
from tools import Logger


class CmdParser:
    def __init__(self, generator, simulator):
        self.command_list = [
            (r"^under ([^.|\n]*)", self.matched_under),
            (r"([^. |\n][^.|\n]*) extends ([^.|\n]*)", orchestrator_viewpoint_type.check_add_type_extension),
            (r"([^. |\n][^.|\n]*) is a ((?!attribute)[^.|\n]*)", orchestrator_object.check_add_specific_obj_by_type),
            (r"([^. |\n][^.|\n]*) is an ((?!attribute)[^.|\n]*)", orchestrator_object.check_add_specific_obj_by_type),
            (r"([^. |\n][^.|\n]*) is an attribute", orchestrator_viewpoint_attribute.add_attribute),
            (r"([^. |\n][^.|\n]*) inherits from ([^.|\n]*)", orchestrator_shared.check_add_inheritance),
            (r"The alias of (.*?) is ([^.|\n]*)", orchestrator_shared.check_set_object_alias),
            (r"^consider ([^.|\n]*)", orchestrator_viewpoint.check_get_consider),
            (r"([^. |\n][^.|\n]*) is composed of ([^.|\n]*)", orchestrator_shared.check_add_child),
            (r"([^. |\n][^.|\n]*) composes ([^.|\n]*)", orchestrator_shared.check_add_child),
            (r"([^. |\n][^.|\n]*) compose ([^.|\n]*)", orchestrator_shared.check_add_child),
            (r"([^. |\n][^.|\n]*) consumes ([^.|\n]*)", orchestrator_functional.check_add_consumer_elem),
            (r"([^. |\n][^.|\n]*) is an input of ([^.|\n]*)", orchestrator_functional.check_add_consumer_elem),
            (r"([^. |\n][^.|\n]*) produces ([^.|\n]*)", orchestrator_functional.check_add_producer_elem),
            (r"([^. |\n][^.|\n]*) is an output of ([^.|\n]*)", orchestrator_functional.check_add_producer_elem),
            (r"([^. |\n][^.|\n]*) exposes ([^.|\n]*)", orchestrator_functional.check_add_exposes),
            (r"([^. |\n][^.|\n]*) expose ([^.|\n]*)", orchestrator_functional.check_add_exposes),
            (r"([^. |\n][^.|\n]*) is allocated to ([^.|\n]*)", orchestrator_object_allocation.check_add_allocation),
            (r"([^. |\n][^.|\n]*) are allocated to ([^.|\n]*)", orchestrator_object_allocation.check_add_allocation),
            (r"([^. |\n][^.|\n]*) allocates ([^.|\n]*)", orchestrator_object_allocation.check_add_allocation),
            (r"^delete ([^.|\n]*)", orchestrator_shared.check_and_delete_object),
            (r"The type of (.*?) is ([^.|\n]*)", orchestrator_shared.check_set_object_type),
            (r"([^. |\n][^.|\n]*) implies ([^.|\n]*)", orchestrator_functional.check_add_predecessor),
            (r"([^. |\n][^.|\n]*) imply ([^.|\n]*)", orchestrator_functional.check_add_predecessor),
            (r"Condition for (.*?) is:([^.|\n]*)", orchestrator_functional.check_add_transition_condition),
            (r"The (source|destination) of (.*?) is ([^.|\n]*)", orchestrator_functional.check_add_src_dest),
            (r"The " + datamodel.ObjectTextPropertyLabel + " of (.*?) is ([^.|\n]*)",
             orchestrator_viewpoint_requirement.check_add_text),
            (datamodel.REQUIREMENT_PATTERN, orchestrator_viewpoint_requirement.check_add_requirement),
            (r"([^. |\n][^.|\n]*) is satisfied by ([^.|\n]*)", orchestrator_object_allocation.check_add_allocation),
            (r"([^. |\n][^.|\n]*) are satisfied by ([^.|\n]*)",
             orchestrator_object_allocation.check_add_allocation),
            (r"([^. |\n][^.|\n]*) satisfies ([^.|\n]*)", orchestrator_object_allocation.check_add_allocation),
            (datamodel.GOAL_PATTERN, orchestrator_viewpoint_goal.check_add_goal),
            (r"([^. |\n][^.|\n]*) derives from ([^.|\n]*)", orchestrator_viewpoint_requirement.check_add_derived),
            (r"([^. |\n][^.|\n]*) derive from ([^.|\n]*)", orchestrator_viewpoint_requirement.check_add_derived),
            (r"([^. |\n][^.|\n]*) is derived into ([^.|\n]*)", orchestrator_viewpoint_requirement.check_add_derived),
            (r"^show ([^.|\n]*)", self.matched_show),
            (r"^(.*?)\?", self.matched_question_mark),
            (r"^list (input|output|child|data|function|transition|interface|activity|information|requirement|goal) "
             r"([^.|\n]*)", CmdParser.matched_list),
            (r"^import requirement from ([^.|\n]*) in column ([^.|\n]*)", CmdParser.matched_import),
            (r"^import ((?!requirement from)[^.|\n]*)", CmdParser.matched_import),
            (r"^export ([^.|\n]*)", CmdParser.matched_export),
            (r"^analyze ([^.|\n]*)", CmdParser.matched_analyze),
            (r"^simulate ([^.|\n]*) between ([^.|\n]*) and ([^.|\n]*)", self.matched_simulate),
            (r"^plot ([^.|\n]*)", self.matched_plot)
        ]

        self.attribute_command_list = [
            (r'The ((?!' + datamodel.ObjectTypePropertyLabel + '|'
             + datamodel.ObjectAliasPropertyLabel + '|'
             + datamodel.ObjectSourcePropertyLabel + '|'
             + datamodel.ObjectDestinationPropertyLabel + '|'
             + datamodel.ObjectTextPropertyLabel
             + ').*) of (.*?) is "((.|\n)*?)"',
             orchestrator_viewpoint_attribute.check_add_object_attribute),
            (r'The ((?!' + datamodel.ObjectTypePropertyLabel + '|'
             + datamodel.ObjectAliasPropertyLabel + '|'
             + datamodel.ObjectSourcePropertyLabel + '|'
             + datamodel.ObjectDestinationPropertyLabel + '|'
             + datamodel.ObjectTextPropertyLabel
             + ').*) of (.*?) is ([^.|\n]*)',
             orchestrator_viewpoint_attribute.check_add_object_attribute)
        ]

        self.reverse_command_list = (r"([^. |\n][^.|\n]*) composes ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) compose ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) consumes ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) produces ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) is allocated to ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) are allocated to ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) is satisfied by ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) are satisfied by ([^.|\n]*)",
                                     r"([^. |\n][^.|\n]*) is derived into ([^.|\n]*)")

        self.question_list = [
            (r"What is (.*)", handler_question.question_object_info),
            (r"Is (.*) allocated", handler_question.question_object_allocation)
        ]

        self.generator = generator

        self.simulator = simulator

    def lookup_table(self, string, **kwargs):
        """Lookup table with conditions depending on the match"""
        update_list = []
        update = None

        # Case of non-attribute command
        for regex, method in self.command_list:
            result_command = None
            result_command_chain = None

            if regex == r"under ([^.|\n]*)":
                result_command_chain = re.split(regex, string)
                del result_command_chain[0]
            # Only one diagram per cell can be output
            elif regex == r"show ([^.|\n]*)":
                result_command = re.search(regex, string, flags=re.MULTILINE | re.IGNORECASE)
            else:
                # Transform to avoid duplicated function's declaration within cells input
                result_command = []
                [result_command.append(x) for x in re.findall(regex, string, flags=re.MULTILINE | re.IGNORECASE)
                 if x not in result_command]

            if result_command and not result_command_chain:
                # self.reverse
                if regex in self.reverse_command_list:
                    result_command = util.reverse_tuple_list(result_command)
                update = method(result_command, **kwargs)
            elif result_command_chain:
                string = ''
                update = self.matched_under(result_command_chain, **kwargs)

            if update is not None:
                if isinstance(update, int):
                    update_list.append(update)

        # Case of attribute command
        result_attr_command = re.findall(self.attribute_command_list[0][0], string, flags=re.MULTILINE | re.IGNORECASE)
        if result_attr_command:
            update = self.attribute_command_list[0][1](result_attr_command, **kwargs)
            if update is not None:
                if isinstance(update, int):
                    update_list.append(update)
        else:
            result_attr_command = re.findall(self.attribute_command_list[1][0], string, flags=re.MULTILINE | re.IGNORECASE)
            if result_attr_command:
                update = self.attribute_command_list[1][1](result_attr_command, **kwargs)
                if update is not None:
                    if isinstance(update, int):
                        update_list.append(update)
            # Else do nothing

        if update is None:
            Logger.set_error(__name__, f"Unable to understand this request")
        # Else do nothing

        return update_list

    @staticmethod
    def matched_under(p_str_list, **kwargs):
        """Get "under" declaration"""
        update = orchestrator_viewpoint.add_view(p_str_list, **kwargs)

        return update

    def matched_show(self, diagram_name_str, **kwargs):
        update = 0

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

        return update

    def matched_simulate(self, simulation_str_list, **kwargs):
        update = 0

        if Config.is_open_modelica:
            if len(simulation_str_list[0]) == 3:
                wanted_simulation_str = simulation_str_list[0][0].replace('"', "").strip()
                regex = r"(state|function)\s(.*)"
                specific_simulation_str = re.search(regex, wanted_simulation_str, re.MULTILINE)

                if specific_simulation_str:
                    out = simulation_generator.filter_simulate_command(specific_simulation_str.group(1),
                                                                       specific_simulation_str.group(2),
                                                                       **kwargs)

                    if out:
                        if not os.path.isdir("simulations"):
                            os.makedirs("simulations")
                        # Else do nothing

                        current_file_path = str(os.getcwd().replace('\\', '/') + '/simulations')
                        current_file_name = str(specific_simulation_str.group(2) + '.mo')
                        try:
                            with open(current_file_path + '/' + current_file_name, "wb") as file_writer:
                                file_writer.write(out.encode("utf-8"))

                            start_time = int(simulation_str_list[0][1])
                            stop_time = int(simulation_str_list[0][2])
                            self.simulator.simulate(specific_simulation_str.group(2), current_file_path,
                                                    current_file_name,
                                                    start_time, stop_time)
                        except EnvironmentError as ex:
                            Logger.set_error(__name__,
                                             f"Unable to write the simulation file {current_file_name}: {str(ex)}")
                        except ValueError:
                            Logger.set_error(__name__,
                                             f'{simulation_str_list[0][1]} and/or {simulation_str_list[0][2]} '
                                             f'are/is not an integer')
                else:
                    Logger.set_error(__name__, f"Jarvis does not understand the command with the "
                                               f"following parameters {simulation_str_list}")
            else:
                Logger.set_error(__name__, f"Jarvis does not understand the command with the "
                                           f"following parameters {simulation_str_list}")
        else:
            Logger.set_error(__name__,
                             "Open modelica simulation is not activated")

        return update

    def matched_plot(self, plot_name_str, **kwargs):
        update = 0

        if Config.is_open_modelica:
            self.simulator.plot(plot_name_str[0].replace('"', "").strip())
        else:
            Logger.set_error(__name__,
                             "Open modelica simulation is not activated")

        return update

    def matched_question_mark(self, p_str_list, **kwargs):
        """@ingroup jarvis
        @anchor matched_question_mark
        Get question declaration for question answering

        @param[in] p_str_list : list of input strings
        @param[in] kwargs : jarvis data structure
        @return None (no xml update, no info displayed)
        """
        update = 0

        for regex, method in self.question_list:
            for elem in p_str_list:
                elem = elem.replace('"', "").strip()
                result = re.findall(regex, elem, flags=re.MULTILINE | re.IGNORECASE)
                if result:
                    answer, answer_format = method(result, **kwargs)
                    if answer:
                        if answer_format == handler_question.ANSWER_FORMAT_STRING:
                            # Single display (not related to logging)
                            print(answer)
                        elif answer_format == handler_question.ANSWER_FORMAT_DICT:
                            display(HTML(util.get_pandas_table(answer)))
                        # Else do nothing
                    # Else do nothing
                # Else do nothing

        return update

    @staticmethod
    def matched_list(p_str_list, **kwargs):
        """@ingroup jarvis
        @anchor matched_list
        Get "list" declaration for listing objects

        @param[in] p_str_list : list of input strings
        @param[in] kwargs : jarvis data structure
        @return None (no xml update, no info displayed)
        """
        update = 0

        out = handler_list.list_object(p_str_list, **kwargs)
        if out:
            for i in out:
                display(HTML(util.get_pandas_table(i)))

        return update

    @staticmethod
    def matched_import(p_str_list, **kwargs):
        """@ingroup jarvis
        @anchor matched_import
        Get "import" declaration for importing objects from a csv filename

        @param[in] p_str_list : list of input strings
        @param[in] kwargs : jarvis data structure
        @return xml updated (1) or not (0)
        """
        update = 0

        if '(' in str(p_str_list):
            csv_name = p_str_list[0][0].replace('"', "").strip()
        else:
            csv_name = p_str_list[0].replace('"', "").strip()

        if os.path.isfile(f"{csv_name}.csv"):
            csv_parser = CsvParser3SE()
            if '(' in str(p_str_list):
                data_column = int(p_str_list[0][1])
                csv_dict = csv_parser.parse_csv(f"{csv_name}.csv",
                                                data_column)
            else:
                csv_dict = csv_parser.parse_csv(f"{csv_name}.csv")

            Logger.set_info(__name__, f"{csv_name}.csv parsed")
            update = orchestrator_dictionary.update_dictionaries(csv_dict, **kwargs)
        else:
            Logger.set_error(__name__,
                             f"File {csv_name}.csv does not exist")

        return update

    @staticmethod
    def matched_export(p_str_list, **kwargs):
        """@ingroup jarvis
        @anchor matched_export
        Get "export" declaration for exporting objects to a csv filename

        @param[in] p_str_list : list of input strings
        @param[in] kwargs : jarvis data structure
        @return None (no xml update, no info displayed)
        """
        update = 0

        csv_name = p_str_list[0].replace('"', "").strip()
        csv_writer = CsvWriter3SE(f"{csv_name}.csv")
        csv_writer.write_file(**kwargs)

        return update

    @staticmethod
    def matched_analyze(p_str_list, **kwargs):
        """@ingroup jarvis
        @anchor matched_analyze
        Get "export" declaration for exporting objects to a csv filename

        @param[in] p_str_list : list of input strings
        @param[in] kwargs : jarvis data structure
        @return None (no xml update, no info displayed)
        """
        update = 0

        if p_str_list[0].replace('"', "").strip() == "requirements":
            update = orchestrator_viewpoint_requirement.analyze_requirement(**kwargs)
        else:
            Logger.set_error(__name__,
                             f"Analysis of {p_str_list[0]} is not supported")

        return update
