"""Module that contains tests to check that xml file has been written"""
import os
from pathlib import Path

from conftest import get_jarvis4se, remove_xml_file
from xml_adapter import XmlParser3SE
from datamodel import BaseType

jarvis4se = get_jarvis4se()
xml_parser = XmlParser3SE()


def test_generate_xml_file_template():
    """Notebook equivalent:
     %%jarvis
     with generate_xml_file_template

     """
    file_name = "generate_xml_file_template"
    jarvis4se.jarvis("", f"with {file_name}\n")
    path = Path(os.path.join("./", file_name + ".xml"))
    with path as file:
        read_xml = file.read_text(encoding="utf-8")
        base_xml = "<?xml version='1.0' encoding='UTF-8'?>\n" \
                   "<systemAnalysis>\n" \
                   "  <funcArch>\n" \
                   "    <functionList/>\n" \
                   "    <dataList/>\n" \
                   "    <stateList/>\n" \
                   "    <transitionList/>\n" \
                   "    <functionalElementList/>\n" \
                   "    <functionalInterfaceList/>\n" \
                   "  </funcArch>\n" \
                   "  <phyArch>\n" \
                   "    <physicalElementList/>\n" \
                   "    <physicalInterfaceList/>\n" \
                   "  </phyArch>\n" \
                   "  <viewPoint>\n" \
                   "    <viewList/>\n" \
                   "    <attributeList/>\n" \
                   "    <typeList/>\n" \
                   "  </viewPoint>\n" \
                   "</systemAnalysis>\n"
        assert base_xml in read_xml
    remove_xml_file(file_name)


def test_simple_function_within_xml():
    """Notebook equivalent:
     %%jarvis
     with simple_function_within_xml
     F1 is a function

     """
    file_name = "simple_function_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n")

    function_list = xml_parser.parse_xml(file_name + ".xml")['xml_function_list']

    remove_xml_file(file_name)

    assert len(function_list) == 1
    assert [fun.name == "F1" for fun in function_list]


def test_described_attribute_within_xml(attribute_cell):
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
    file_name = "described_attribute_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n{attribute_cell[0]}")
    jarvis4se.jarvis("", f"with {file_name}\n{attribute_cell[1]}")
    jarvis4se.jarvis("", f"with {file_name}\n{attribute_cell[2]}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected = {('A', 'F1', '4,2'), ('B', 'Fun elem', '8,5'),
                ('C', 'F1', 'pink'), ('A', 'Fun elem', '100')}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result = set()
    assert len(obj_dict['xml_attribute_list']) == 3
    for attribute in obj_dict['xml_attribute_list']:
        for item in attribute.described_item_list:
            for function in obj_dict['xml_function_list']:
                if item[0] == function.id:
                    result.add((attribute.name, function.name, item[1]))
            for fun_elem in obj_dict['xml_fun_elem_list']:
                if item[0] == fun_elem.id:
                    result.add((attribute.name, fun_elem.name, item[1]))

    remove_xml_file(file_name)

    assert expected == result


def test_set_attribute_type_within_xml():
    """Tests that attribute types are written correctly within xml, notebook equivalent:
     %%jarvis
     with set_attribute_type_within_xml
     A is an attribute
     B is an attribute.
     attribute type A extends attribute
     attribute type B extends attribute
     The type of A is attribute type A.
     The type of B is attribute type B

     """
    file_name = "set_attribute_type_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "A is an attribute\n"
                         "B is an attribute.\n"
                         "attribute type A extends attribute\n"
                         "attribute type B extends attribute\n"
                         "The type of A is attribute type A.\n"
                         "The type of B is attribute type B\n")

    attribute_list = xml_parser.parse_xml(file_name + ".xml")['xml_attribute_list']
    expected = {('A', 'attribute type A'), ('B', 'attribute type B')}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result = set()
    assert len(attribute_list) == 2
    for attribute in attribute_list:
        result.add((attribute.name, attribute.type.name))

    remove_xml_file(file_name)

    assert expected == result


def test_set_allocated_item_to_view_within_xml(allocation_item_cell):
    """Relative to Issue #9 to add new allocated item to a view(i.e. filter) by verifying than
    it's written within xml. Notebook equivalent:
    %%jarvis
    with set_allocated_item_to_view_within_xml
    F1 is a function
    F2 with a long name is a function. The alias of F2 with a long name is F2.
    F3 is a function
    F4 is a function
    a is a data
    Fun_elem is a functional element
    ========================================
    %%jarvis
    with set_allocated_item_to_view_within_xml
    under toto
    consider F1. consider toto. consider a, Fun_elem
    consider tata.
    consider F1, F2, F3, F4
    """
    file_name = "set_allocated_item_to_view_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n{allocation_item_cell[0]}")
    jarvis4se.jarvis("", f"with {file_name}\n{allocation_item_cell[1]}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected = {'F1', 'F2 with a long name', 'F3', 'F4', 'a', 'Fun_elem'}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result = set()
    assert len(obj_dict['xml_view_list']) == 1
    assert "test_view" in {i.name for i in obj_dict['xml_view_list']}
    for item in next(iter(obj_dict['xml_view_list'])).allocated_item_list:
        for fun in obj_dict['xml_function_list']:
            if item == fun.id:
                result.add(fun.name)

        for fun_elem in obj_dict['xml_fun_elem_list']:
            if item == fun_elem.id:
                result.add(fun_elem.name)

        for data in obj_dict['xml_data_list']:
            if item == data.id:
                result.add(data.name)

    remove_xml_file(file_name)

    assert expected == result


def test_function_with_grandkids_within_xml(function_grandkids_cell):
    """See Issue #31, Notebook equivalent:
    %%jarvis
    with function_with_grandkids_within_xml
    F1 is a function
    F1a is a function
    F1a1 is a function
    F1 is composed of F1a
    F1a is composed of F1a1
    a is a data
    F1a produces a
    b is a data
    F1a consumes b
    c is a data
    F1a1 produces c
    d is a data
    F1a1 consumes d
    """
    file_name = "function_with_grandkids_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n{function_grandkids_cell}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected_cons = {('b', 'F1a'), ('d', 'F1'), ('b', 'F1'), ('d', 'F1a'), ('d', 'F1a1')}
    expected_prod = {('c', 'F1a1'), ('a', 'F1'), ('c', 'F1'), ('c', 'F1a'), ('a', 'F1a')}
    expected_child = {('F1', 'F1a'), ('F1a', 'F1a1')}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result_cons = set()
    result_prod = set()
    result_child = set()
    assert len(obj_dict['xml_data_list']) == 4 and len(obj_dict['xml_function_list']) == 3
    assert (len(obj_dict['xml_consumer_function_list']) and
            len(obj_dict['xml_producer_function_list'])) == 5

    for cons in obj_dict['xml_consumer_function_list']:
        result_cons.add((cons[0], cons[1].name))
    for prod in obj_dict['xml_producer_function_list']:
        result_prod.add((prod[0], prod[1].name))
    for fun in obj_dict['xml_function_list']:
        if fun.child_list:
            for child in fun.child_list:
                result_child.add((fun.name, child.name))

    remove_xml_file(file_name)

    assert expected_cons == result_cons
    assert expected_prod == result_prod
    assert expected_child == result_child


def test_function_childs_cons_prod_within_xml(function_with_childs_cell):
    """See Issue #5, Notebook equivalent:
    %%jarvis
    with function_childs_cons_prod_within_xml
    F1 is a function
    F1a is a function
    F1b is a function
    F1c is a function
    F1d is a function
    F1e is a function
    F2 is a function
    F3 is a function

    F1 is composed of F1a
    F1 is composed of F1b
    F1 is composed of F1c
    F1 is composed of F1d
    F1 is composed of F1e

    a is a data
    F1 produces a
    F2 consumes a

    F1a produces a
    F1b consumes a

    b is a data
    F1c produces b
    F1d consumes b

    c is a data
    F3 produces c
    F1e consumes c
    """
    file_name = "function_childs_cons_prod_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{function_with_childs_cell}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected_cons = {('a', 'F1b'), ('b', 'F1d'), ('a', 'F2'), ('c', 'F1e'), ('c', 'F1')}
    expected_prod = {('b', 'F1c'), ('c', 'F3'), ('a', 'F1a'), ('a', 'F1')}
    expected_child = {('F1', 'F1e'), ('F1', 'F1d'), ('F1', 'F1c'), ('F1', 'F1b'), ('F1', 'F1a')}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result_cons = set()
    result_prod = set()
    result_child = set()
    assert len(obj_dict['xml_data_list']) == 3 and len(obj_dict['xml_function_list']) == 8
    assert len(obj_dict['xml_consumer_function_list']) == 5 and \
           len(obj_dict['xml_producer_function_list']) == 4

    for cons in obj_dict['xml_consumer_function_list']:
        result_cons.add((cons[0], cons[1].name))
    for prod in obj_dict['xml_producer_function_list']:
        result_prod.add((prod[0], prod[1].name))
    for fun in obj_dict['xml_function_list']:
        if fun.child_list:
            for child in fun.child_list:
                result_child.add((fun.name, child.name))

    remove_xml_file(file_name)

    assert expected_cons == result_cons
    assert expected_prod == result_prod
    assert expected_child == result_child


def test_functional_interface_within_xml():
    """Notebook equivalent:
    %%jarvis
    with functional_interface_within_xml
    Color is an attribute
    A is a data
    F1 is a function
    F2 is a function
    Fun_elem_1 is a functional element
    Fun_elem_2 is a functional element
    F1 produces A
    F2 consumes A
    Fun_elem_1 allocates F1
    Fun_elem_2 allocates F2
    Fun_inter is a functional interface.
    The type of Fun_inter is a_type
    The alias of Fun_inter is FI
    The Color of Fun_inter is pink
    Fun_elem_1 exposes Fun_inter
    Fun_elem_2 exposes Fun_inter
    Fun_inter allocates A.
    """
    file_name = "functional_interface_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "Color is an attribute\n"
                         "A is a data\n"
                         "F1 is a function\n"
                         "F2 is a function\n"
                         "Fun_elem_1 is a functional element\n"
                         "Fun_elem_2 is a functional element\n"
                         "F1 produces A\n"
                         "F2 consumes A\n"
                         "Fun_elem_1 allocates F1\n"
                         "Fun_elem_2 allocates F2\n"
                         "Fun_inter is a functional interface.\n"
                         "The type of Fun_inter is functional interface\n"
                         "The alias of Fun_inter is FI\n"
                         "The Color of Fun_inter is pink\n"
                         "Fun_elem_1 exposes Fun_inter\n"
                         "Fun_elem_2 exposes Fun_inter\n"
                         "Fun_inter allocates A.\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    assert (len(obj_dict['xml_data_list']) == len(obj_dict['xml_attribute_list']) ==
            len(obj_dict['xml_fun_inter_list'])) == 1
    data = obj_dict['xml_data_list'].pop()
    fun_inter = obj_dict['xml_fun_inter_list'].pop()
    attribute = obj_dict['xml_attribute_list'].pop()
    assert data.name == 'A'
    assert fun_inter.name == 'Fun_inter'
    assert fun_inter.alias == 'FI'
    assert fun_inter.type == BaseType['FUNCTIONAL_INTERFACE']
    assert attribute.name == 'Color'
    described_item = attribute.described_item_list.pop()
    assert described_item[0] == fun_inter.id and described_item[1] == 'pink'
    assert fun_inter.allocated_data_list.pop() == data.id

    remove_xml_file(file_name)


def test_fun_elem_exposes_interface_within_xml(fun_elem_exposing_cell):
    """Notebook equivalent:
    %%jarvis
    with fun_elem_exposes_interface_within_xml
    Fun_inter is a functional interface
    Fun_elem is a functional element
    Fun_elem_2 is a functional element
    Fun_elem_3 is a functional element
    Fun_elem_4 is a functional element
    Fun_elem_5 is a functional element
    Fun_elem_6 is a functional element
    Fun_elem_ext is a functional element
    Fun_elem is composed of Fun_elem_2
    Fun_elem_2 is composed of Fun_elem_3
    Fun_elem_3 is composed of Fun_elem_4
    Fun_elem_4 is composed of Fun_elem_5
    Fun_elem_5 is composed of Fun_elem_6
    Fun_elem exposes Fun_inter
    Fun_elem_6 exposes Fun_inter
    Fun_elem_ext exposes Fun_inter
    toto exposes Fun_inter
    tata exposes titi
    Fun_elem exposes coco
    """
    file_name = "fun_elem_exposes_interface_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n{fun_elem_exposing_cell}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected_child = {('Fun_elem', 'Fun_elem_2'), ('Fun_elem_2', 'Fun_elem_3'),
                      ('Fun_elem_3', 'Fun_elem_4'), ('Fun_elem_4', 'Fun_elem_5'),
                      ('Fun_elem_5', 'Fun_elem_6')}
    expected_exposed = {('Fun_elem', 'Fun_inter'), ('Fun_elem_6', 'Fun_inter'),
                        ('Fun_elem_ext', 'Fun_inter')}

    assert len(obj_dict['xml_fun_inter_list']) == 1 and len(obj_dict['xml_fun_elem_list']) == 8
    fun_inter = obj_dict['xml_fun_inter_list'].pop()
    assert fun_inter.name == 'Fun_inter'

    result_exposed = set()
    result_child = set()
    for fun_elem in obj_dict['xml_fun_elem_list']:
        for child in fun_elem.child_list:
            result_child.add((fun_elem.name, child.name))
        if fun_inter.id in fun_elem.exposed_interface_list:
            result_exposed.add((fun_elem.name, fun_inter.name))

    assert expected_child == result_child
    assert expected_exposed == result_exposed

    remove_xml_file(file_name)


def test_type_within_xml(extends_and_set_type_cell):
    """ Issue #56 Notebook equivalent:
    %%jarvis
    with type_within_xml
    Safety interface extends functional interface
    The alias of Safety interface is sf
    ========================================
    %%jarvis
    sf_a extends sf
    sf_a_b extends sf_a
    final one extends sf_a_b
    Fun_inter is a functional interface
    The type of Fun_inter is final one
    """
    file_name = "type_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n{extends_and_set_type_cell[0]}")
    jarvis4se.jarvis("", f"with {file_name}\n{extends_and_set_type_cell[1]}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    assert len([x for x in obj_dict.values() if x]) == 2
    assert len(obj_dict['xml_type_list']) == 4
    assert len(obj_dict['xml_fun_inter_list']) == 1

    expected_type = {('sf_a', 'Safety interface'), ('sf_a_b', 'sf_a'),
                     ('Safety interface', 'Functional interface'), ('final one', 'sf_a_b')}
    captured_type = set()
    for type_elem in obj_dict['xml_type_list']:
        if type_elem.name == 'Safety interface':
            assert type_elem.alias == 'sf'
        if isinstance(type_elem.base, BaseType):
            base_type = str(type_elem.base)
        else:
            base_type = type_elem.base.name
        captured_type.add((type_elem.name, base_type))

    assert expected_type == captured_type
    assert obj_dict['xml_fun_inter_list'].pop().type.name == "final one"

    remove_xml_file(file_name)


def test_extends_and_create_object_within_xml(capsys, extends_and_create_object_cell):
    """ Issue #62 Notebook equivalent:
    %%jarvis
    with extends_and_create_object_within_xml
    "High level function" extends function
    "High high level function" extends "High level function"
    "High high high level function" extends "High high level function"
    3High is a "High high high level function"
    """
    file_name = "extends_and_create_object_within_xml"
    jarvis4se.jarvis("", f"with {file_name}\n{extends_and_create_object_cell}")
    
    obj_dict = xml_parser.parse_xml(file_name + ".xml")
    
    assert len([x for x in obj_dict.values() if x]) == 2
    assert len(obj_dict['xml_type_list']) == 3
    assert len(obj_dict['xml_function_list']) == 1

    expected_type = {('High level function', 'Function'),
                     ('High high level function', 'High level function'),
                     ('High high high level function', 'High high level function')}
    captured_type = set()
    for type_elem in obj_dict['xml_type_list']:
        print(type_elem, type_elem.base)
        if isinstance(type_elem.base, BaseType):
            base_type = str(type_elem.base)
        else:
            base_type = type_elem.base.name
        captured_type.add((type_elem.name, base_type))

    assert expected_type == captured_type
    assert obj_dict['xml_function_list'].pop().type.name == "High high high level function"

    remove_xml_file(file_name)
