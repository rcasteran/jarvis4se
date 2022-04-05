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


def test_described_attribute_within_xml():
    """Same as test_described_attribute_input() within test_input_cell.py, but here we are
    verifying that attributes are written correctly within xml:
     %%jarvis
     with described_attribute_within_xml
     F1 is a function
     Fun elem is a functional element
     ========================================
     %%jarvis
     with described_attribute_within_xml
     A is an attribute
     B is an attribute. C is an attribute
     ========================================
     %%jarvis
     with described_attribute_within_xml
     The A of F1 is 4,2
     The C of F1 is pink
     The B of Fun elem is 8,5.
     The A of Fun elem is 100

     """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "described_attribute_within_xml"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "Fun elem is a functional element\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "A is an attribute\n"
                    "B is an attribute. C is an attribute\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "The A of F1 is 4,2\n"
                    "The C of F1 is pink\n"
                    "The B of Fun elem is 8,5.\n"
                    "The A of Fun elem is 100\n")

    function_list = xml_adapter.parse_xml(file_name + ".xml")[0]
    fun_elem_list = xml_adapter.parse_xml(file_name + ".xml")[8]
    attribute_list = xml_adapter.parse_xml(file_name + ".xml")[11]

    expected = {('A', 'F1', '4,2'), ('B', 'Fun elem', '8,5'),
                ('C', 'F1', 'pink'), ('A', 'Fun elem', '100')}
    result = set()
    assert len(attribute_list) == 3
    for attribute in attribute_list:
        for item in attribute.described_item_list:
            for function in function_list:
                if item[0] == function.id:
                    result.add((attribute.name, function.name, item[1]))
            for fun_elem in fun_elem_list:
                if item[0] == fun_elem.id:
                    result.add((attribute.name, fun_elem.name, item[1]))

    assert expected == result

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)
