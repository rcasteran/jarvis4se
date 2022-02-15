#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
import re
import os
import shutil
import getpass
from datetime import datetime
from io import StringIO

from IPython.core.magic import (Magics, magics_class, cell_magic)
from IPython.display import display, HTML, Markdown

# Modules
import orchestrator
import xml_adapter
import question_answer


# The class MUST call this class decorator at creation time
@magics_class
class MyMagics(Magics):

    @cell_magic
    def jarvis(self, line, cell):
        # We create a string buffer containing the
        # contents of the cell.
        sio = StringIO(cell)
        # Take the value within the buffer
        input_str = sio.getvalue()
        # Delete the '"' from input string, to avoid xml to plantuml errors.
        input_str = input_str.replace('"', "")
        # Get model's declaration, need a space after "with" otherwise print a message
        xml_name_str = re.match(r"^with (.*)(?=.|\n)", input_str, re.MULTILINE)
        if xml_name_str:
            xml_name = xml_name_str.group(1)
            # If the model(i.e. file) already exists, parse it to extract lists
            if os.path.isfile(f"{xml_name}.xml"):
                print(f"{xml_name}.xml parsed")
                xml_lists = xml_adapter.parse_xml(f"{xml_name}.xml")
                xml_function_list = xml_lists[0]
                xml_consumer_function_list = xml_lists[1]
                xml_producer_function_list = xml_lists[2]
                xml_function_parent_dict = xml_lists[3]
                xml_data_list = xml_lists[4]
                xml_state_list = xml_lists[5]
                xml_state_parent_dict = xml_lists[6]
                xml_transition_list = xml_lists[7]
                xml_fun_elem_list = xml_lists[8]
                xml_fun_elem_parent_dict = xml_lists[9]
                xml_chain_list = xml_lists[10]
                output_xml = xml_adapter.generate_xml(f"{xml_name}.xml")
            # Else create an empty xml named by "xml_name"(and associated empty lists)
            # or will be named by default "Outpout"
            else:
                xml_function_list = set()
                xml_consumer_function_list = []
                xml_producer_function_list = []
                xml_function_parent_dict = {}
                xml_data_list = set()
                xml_state_list = set()
                xml_state_parent_dict = {}
                xml_transition_list = set()
                xml_fun_elem_list = set()
                xml_fun_elem_parent_dict = {}
                xml_chain_list = set()
                if len(xml_name) > 1:
                    print(f"Creating {xml_name}.xml !")
                    output_xml = xml_adapter.generate_xml(f"{xml_name}.xml")
                    output_xml.write()
                else:
                    print("Xml's file does not exists, creating it('output.xml' by default) !")
                    output_xml = xml_adapter.generate_xml("")
                    output_xml.write()

            xml_dict = {'xml_function_list': xml_function_list,
                        'xml_consumer_function_list': xml_consumer_function_list,
                        'xml_producer_function_list': xml_producer_function_list,
                        'xml_function_parent_dict': xml_function_parent_dict,
                        'xml_data_list': xml_data_list,
                        'xml_state_list': xml_state_list,
                        'xml_state_parent_dict': xml_state_parent_dict,
                        'xml_transition_list': xml_transition_list,
                        'xml_fun_elem_list': xml_fun_elem_list,
                        'xml_fun_elem_parent_dict': xml_fun_elem_parent_dict,
                        'xml_chain_list': xml_chain_list,
                        'output_xml': output_xml,
                        'xml_name': xml_name}

            update = lookup(input_str, LOOKUPS, **xml_dict)

            if not update:
                return
            else:
                if 1 in update:
                    self.show_model_update_msg(xml_name)
                else:
                    self.show_no_model_update_msg(xml_name)
        else:
            print(
                "Bad model's declaration, model's name should be written or add a ' '(blank space) "
                "after 'with' command to create default 'Output.xml'")

    @classmethod
    def show_model_update_msg(cls, xml_name):
        print(f"{xml_name}.xml updated")

    @classmethod
    def show_no_model_update_msg(cls, xml_name):
        print(f"No update for {xml_name}.xml")


# In order to actually use these magics, you must register them with a
# running IPython.
def load_ipython_extension(ipython):
    """
    Any module file that define a function named `load_ipython_extension`
    can be loaded via `%load_ext module.path` or be configured to be
    autoloaded by IPython at startup time.
    """
    # You can register the class itself without instantiating it.  IPython will
    # call the default constructor on it.
    ipython.register_magics(MyMagics)
    clean_diagram_folder()
    greet_user()


LOOKUPS = [
    (r"(under.*)",
     lambda matched_str, **kwargs: matched_under(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) is a function\b(?=.|\n)",
     lambda matched_str, **kwargs: matched_function(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) is a data(?=. |\n)",
     lambda matched_str, **kwargs: matched_data(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) is a state(?=.|\n)",
     lambda matched_str, **kwargs: matched_state(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) is a transition(?=.|\n)",
     lambda matched_str, **kwargs: matched_transition(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) is a functional element(?=.|\n)",
     lambda matched_str, **kwargs: matched_functional_element(matched_str, **kwargs)),

    (r"The alias of (.*?) is ([^\.\n]*)",
     lambda matched_str, **kwargs: matched_alias(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) is composed of ([^\.\n]*)",
     lambda matched_str, **kwargs: matched_composition(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) composes (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_composition(reverse(matched_str), **kwargs)),

    (r"(?<= |\n)(.*?) consumes (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_consumer(reverse(matched_str), **kwargs)),

    (r"(?<= |\n)(.*?) is an input of (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_consumer(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) produces (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_producer(reverse(matched_str), **kwargs)),

    (r"(?<= |\n)(.*?) is an output of (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_producer(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) is allocated to (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_allocation(reverse(matched_str), **kwargs)),

    (r"(?<= |\n)(.*?) allocates (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_allocation(matched_str, **kwargs)),
    (r"(?<= |\n)delete (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_delete(matched_str, **kwargs)),

    (r"The type of (.*?) is ([^\.\n]*)",
     lambda matched_str, **kwargs: matched_type(matched_str, **kwargs)),

    (r"(?<= |\n)(.*?) implies ([^\.\n]*)",
     lambda matched_str, **kwargs: matched_implies(matched_str, **kwargs)),

    (r"Condition for (.*?) is:([^\.\n]*)",
     lambda matched_str, **kwargs: matched_condition(matched_str, **kwargs)),

    (r"The (source|destination) of (.*?) is (.*?)(?=. |\n)",
     lambda matched_str, **kwargs: matched_src_dest(matched_str, **kwargs)),

    (r"(?<= |\n)show (.*?)\n",
     lambda matched_str, **kwargs: matched_show(matched_str, **kwargs)),

    (r"\s([A-Za-z\s].*\?)",
     lambda matched_str, **kwargs: matched_question_mark(matched_str, **kwargs)),
]


def lookup(string, lookups, **kwargs):
    update_list = []
    for regex, values in lookups:
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
            # Transform to set : to avoid duplicated function's declaration within jarvis command
            result = set(re.findall(regex, string, re.MULTILINE))

        if result and not result_chain:
            update = values(result, **kwargs)
        elif result_chain:
            string = ''
            update = matched_under(result_chain, **kwargs)

        if update and isinstance(update, list):
            update_list.append(*update)

    return update_list


def matched_under(chain_name_str, **kwargs):
    out = []
    for a, b in zip(chain_name_str[::2], chain_name_str[1::2]):
        a = a.replace("under ", "")
        out += orchestrator.add_chain(a,
                                      kwargs['xml_chain_list'],
                                      kwargs['output_xml'])
        lookup(b, LOOKUPS, **kwargs)
    if 1 in out:
        return [1]
    else:
        return [0]


# Get function's declaration (does not match if "function" is not at the end)
def matched_function(function_name_str_list, **kwargs):
    out = orchestrator.add_function_by_name(function_name_str_list,
                                            kwargs['xml_function_list'],
                                            kwargs['output_xml'])
    return out


# Get data declaration
def matched_data(data_str_list, **kwargs):
    out = orchestrator.add_data(data_str_list, kwargs['xml_data_list'],
                                kwargs['output_xml'])
    return out


# Get state's declaration
def matched_state(state_name_str_list, **kwargs):
    out = orchestrator.add_state_by_name(state_name_str_list,
                                         kwargs['xml_state_list'],
                                         kwargs['output_xml'])
    return out


# Get transition's declaration
def matched_transition(transition_name_str_list, **kwargs):
    out = orchestrator.add_transition_by_name(transition_name_str_list,
                                              kwargs['xml_transition_list'],
                                              kwargs['output_xml'])
    return out


# Get Functional element's declaration
def matched_functional_element(functional_elem_name_str_list, **kwargs):
    out = orchestrator.add_fun_elem_by_name(functional_elem_name_str_list,
                                            kwargs['xml_fun_elem_list'],
                                            kwargs['output_xml'])
    return out


# Get set_alias declaration
def matched_alias(alias_str_list, **kwargs):
    out = orchestrator.check_set_object_alias(alias_str_list,
                                              kwargs['xml_function_list'],
                                              kwargs['xml_state_list'],
                                              kwargs['xml_transition_list'],
                                              kwargs['xml_fun_elem_list'],
                                              kwargs['output_xml'])
    return out


# Get composition relationship command (match for "is composed by' or "composes")
def matched_composition(parent_child_name_str_list, **kwargs):
    out = orchestrator.check_add_child(parent_child_name_str_list,
                                       kwargs['xml_function_list'],
                                       kwargs['xml_function_parent_dict'],
                                       kwargs['xml_state_list'],
                                       kwargs['xml_state_parent_dict'],
                                       kwargs['xml_fun_elem_list'],
                                       kwargs['xml_fun_elem_parent_dict'],
                                       kwargs['output_xml'])
    return out


# Get consumer declaration
def matched_consumer(consumer_str_list, **kwargs):
    out = orchestrator.check_add_consumer_function(consumer_str_list,
                                                   kwargs['xml_consumer_function_list'],
                                                   kwargs['xml_producer_function_list'],
                                                   kwargs['xml_function_list'],
                                                   kwargs['xml_data_list'],
                                                   kwargs['output_xml'])
    return out


# Get producer declaration
def matched_producer(producer_str_list, **kwargs):
    out = orchestrator.check_add_producer_function(producer_str_list,
                                                   kwargs['xml_consumer_function_list'],
                                                   kwargs['xml_producer_function_list'],
                                                   kwargs['xml_function_list'],
                                                   kwargs['xml_data_list'],
                                                   kwargs['output_xml'])
    return out


# Get allocation declaration
def matched_allocation(allocation_str_list, **kwargs):
    out = orchestrator.check_add_allocation(allocation_str_list,
                                            kwargs['xml_fun_elem_list'],
                                            kwargs['xml_state_list'],
                                            kwargs['xml_function_list'],
                                            kwargs['output_xml'])
    return out


# Get delete declaration
def matched_delete(delete_str_list, **kwargs):
    out = orchestrator.check_and_delete(delete_str_list,
                                        kwargs['xml_function_list'],
                                        kwargs['xml_producer_function_list'],
                                        kwargs['xml_consumer_function_list'],
                                        kwargs['xml_data_list'],
                                        kwargs['xml_state_list'],
                                        kwargs['xml_transition_list'],
                                        kwargs['xml_fun_elem_list'],
                                        kwargs['output_xml'])
    return out


# Get set_type declaration
def matched_type(type_str_list, **kwargs):
    out = orchestrator.check_set_object_type(type_str_list,
                                             kwargs['xml_function_list'],
                                             kwargs['xml_data_list'],
                                             kwargs['xml_state_list'],
                                             kwargs['xml_transition_list'],
                                             kwargs['xml_fun_elem_list'],
                                             kwargs['output_xml'])
    return out


# Get predecessor declaration
def matched_implies(data_predecessor_str_set, **kwargs):
    out = orchestrator.check_add_predecessor(data_predecessor_str_set,
                                             kwargs['xml_data_list'],
                                             kwargs['xml_chain_list'],
                                             kwargs['output_xml'])
    return out


# Get set_condition declaration
def matched_condition(condition_str_list, **kwargs):
    out = orchestrator.check_add_transition_condition(condition_str_list,
                                                      kwargs['xml_transition_list'],
                                                      kwargs['output_xml'])
    return out


# Get source/destination declaration for transition
def matched_src_dest(src_dest_str, **kwargs):
    # xml_transition_list, xml_state_list, output_xml
    out = orchestrator.check_add_src_dest(src_dest_str,
                                          kwargs['xml_transition_list'],
                                          kwargs['xml_state_list'],
                                          kwargs['output_xml'])
    return out


# Get "show" declaration
def matched_show(diagram_name_str, **kwargs):
    out = orchestrator.filter_show_command(diagram_name_str, **kwargs)
    if out:
        print("Click on the link to open in new tab : ")
        if out[:4] == 'http':
            print(out)
        else:
            hyper = get_hyperlink_from_file(out)
            display(HTML(hyper))
        print("Overview :")
        return display(Markdown(f'![figure]({out})'))


def matched_question_mark(question_str, **kwargs):
    """Gets "?" declaration"""
    out = question_answer.find_question(question_str, **kwargs)
    if out:
        for elem in out:
            if isinstance(elem, str):
                print(elem)
            else:
                display(elem)


def reverse(inverted_list):
    """Reverses input tuple strings"""
    sorted_list = []
    for tuples in inverted_list:
        new_tup = ()
        for k in reversed(tuples):
            new_tup = new_tup + (k,)
        sorted_list.append(new_tup)
    return sorted_list


def greet_user():
    """Greets the user according to the time"""
    hour = datetime.now().hour
    # Use getpass() because available on Unix/Windows
    user_name = getpass.getuser()
    if 6 <= hour < 12:
        print(f"Good Morning {user_name}")
    elif 12 <= hour < 16:
        print(f"Good afternoon {user_name}")
    elif 16 <= hour < 19:
        print(f"Good Evening {user_name}")
    print("I am Jarvis. How may I assist you?")


def clean_diagram_folder():
    """Clean/erase all files within Diagram's folder"""
    folder = './Diagrams'
    if not os.path.exists(folder):
        os.mkdir(folder)
    else:
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


def get_hyperlink_from_file(path):
    """Convert file path into clickable form."""
    # returns the final component of a url
    f_url = os.path.basename(path)
    # convert the url into link
    return '<a href="{}" target="_blank">{}</a>'.format(path, f_url)
