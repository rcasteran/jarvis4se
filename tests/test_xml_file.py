import os
from IPython import get_ipython
from pathlib import Path
import xml_adapter
import jarvis


def test_generate_xml_file_template():
    """Notebook equivalent:
     %%jarvis
     with generate_xml_file_template

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
                   "  <attributeList/>\n" \
                   "</funcArch>\n"
        assert base_xml in s
    if path:
        os.remove(Path(fname))


def test_simple_function_within_xml():
    """Notebook equivalent:
     %%jarvis
     with simple_function_within_xml
     F1 is a function

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



