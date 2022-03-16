import pytest
import os
from IPython import get_ipython
from pathlib import Path
from src import xml_adapter
from src import jarvis
from src import plantuml_adapter


def test_generate_xml_file_template():
    """Notebook equivalent:
     %%jarvis
     with xml_file

     """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "generate_xml_file_template"
    my_magic.jarvis("", "with %s\n" % file_name)
    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    with path as f:
        s = f.read_text(encoding="utf-8")
        base_xml = "<?xml version='1.0' encoding='UTF-8'?>\n" \
                   "<funcArch>\n" \
                   "  <functionList/>\n" \
                   "  <dataList/>\n" \
                   "  <stateList/>\n" \
                   "  <transitionList/>\n" \
                   "  <functionalElementList/>\n" \
                   "  <chainList/>\n" \
                   "</funcArch>\n"
        assert base_xml in s
    if path:
        os.remove(Path(fname))


def test_simple_function_within_xml():
    """Notebook equivalent:
     %%jarvis
     with simple_function
     F1 is a function

     NB: Id for functions are changing everytime so comparing directly strings can not be done.
     Is it possible to put id's attribute to not assert ?
     Or keep it this way by testing also the parse_xml()
     """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "simple_function_within_xml"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n")

    function_list = xml_adapter.parse_xml(file_name + ".xml")[0]
    assert len(function_list) == 1
    for fun in function_list:
        assert fun.name == "F1"
    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_simple_function_context(mocker):
    """Notebook equivalent:
     %%jarvis
     with output_string
     F1 is a function
     show context F1

     """
    spy = mocker.spy(plantuml_adapter, "plantuml_binder")
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "simple_function_context"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by plantuml_binder()
    expected = 'object "F1" as f1 <<unknown>>'
    assert expected in result
    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)

    # TODO: This test isn't well covered since i'm only checking that result contains what i want,
    #       but it can also contains other char and this should not be the case.
    #       Can use difflib or other conditions on result to fully covered the test case.
