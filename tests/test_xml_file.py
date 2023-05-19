"""@defgroup test_xml_file
Tests about xml file generation
"""
# Libraries
import os
from pathlib import Path

# Modules
import test_lib
from xml_adapter import XmlParser3SE
from datamodel import BaseType

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
xml_parser = XmlParser3SE()


def test_template_xml():
    """@ingroup test_xml_file
    @anchor test_template_xml
    Test the structure of the xml generated file against the xml template

    @return None
    """
    file_name = "test_template_xml"
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

    test_lib.remove_xml_file(file_name)


def test_simple_function_xml(input_test_simple_function):
    """@ingroup test_xml_file
    @anchor test_simple_function_xml
    Test xml file for a single function without input / output

    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_simple_function
    """
    file_name = "test_simple_function_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_simple_function}\n")

    function_list = xml_parser.parse_xml(file_name + ".xml")['xml_function_list']

    test_lib.remove_xml_file(file_name)

    assert len(function_list) == 1
    assert [fun.name == "F1" for fun in function_list]


def test_instantiated_attribute_xml(input_test_fun_elem_with_attribute):
    """@ingroup test_xml_file
    @anchor test_instantiated_attribute_xml
    Test attribute instantiation in xml file

    @param[in] input_test_fun_elem_with_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_attribute
    """
    file_name = "test_instantiated_attribute_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[1]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[2]}\n")

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

    test_lib.remove_xml_file(file_name)

    assert expected == result


def test_extended_attribute_xml(input_test_extended_attribute):
    """@ingroup test_xml_file
    @anchor test_extended_attribute_xml
    Test attribute extension in xml file

    @param[in] input_test_extended_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_extended_attribute
    """
    file_name = "test_extended_attribute_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_extended_attribute}\n")

    attribute_list = xml_parser.parse_xml(file_name + ".xml")['xml_attribute_list']
    expected = {('A', 'attribute type A'), ('B', 'attribute type B')}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result = set()
    assert len(attribute_list) == 2
    for attribute in attribute_list:
        result.add((attribute.name, attribute.type.name))

    test_lib.remove_xml_file(file_name)

    assert expected == result


def test_functional_interface_with_attribute_xml(input_test_functional_interface_with_attribute):
    """@ingroup test_xml_file
    @anchor test_functional_interface_with_attribute_xml
    Test functional interface with attribute in xml file

    @param[in] input_test_functional_interface_with_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_functional_interface_with_attribute
    """
    file_name = "test_functional_interface_with_attribute_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_functional_interface_with_attribute}\n")

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

    test_lib.remove_xml_file(file_name)


def test_fun_elem_exposes_interface_xml(input_test_fun_elem_exposes_interface):
    """@ingroup test_xml_file
    @anchor test_fun_elem_exposes_interface_xml
    Test functional interface allocation to functional element

    @param[in] input_test_fun_elem_exposes_interface : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_exposes_interface
    """
    file_name = "test_fun_elem_exposes_interface_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_exposes_interface}\n")

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

    test_lib.remove_xml_file(file_name)


def test_function_output_auto_xml(input_test_function_output_auto_decomposition):
    """@ingroup test_xml_file
    @anchor test_function_output_auto_xml
    Test function decomposition

    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    assert len(obj_dict['xml_function_list']) == 3

    expected_consumer_list = {('a', 'F2')}
    expected_producer_list = {('a', 'F1'), ('a', 'F')}

    result_consumer_list = set()
    result_producer_list = set()
    for flow_cons_list in obj_dict['xml_consumer_function_list']:
        result_consumer_list.add((flow_cons_list[0], flow_cons_list[1].name))

    for flow_prod_list in obj_dict['xml_producer_function_list']:
        result_producer_list.add((flow_prod_list[0], flow_prod_list[1].name))

    assert result_consumer_list == expected_consumer_list
    assert result_producer_list == expected_producer_list

    test_lib.remove_xml_file(file_name)


def test_function_output_auto_splitted_xml(input_test_function_output_auto_decomposition):
    """@ingroup test_xml_file
    @anchor test_function_output_auto_splitted_xml
    Test function decomposition done in multiple cells

    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    assert len(obj_dict['xml_function_list']) == 3

    expected_consumer_list = {('a', 'F2')}
    expected_producer_list = {('a', 'F1')}

    result_consumer_list = set()
    result_producer_list = set()
    for flow_cons_list in obj_dict['xml_consumer_function_list']:
        result_consumer_list.add((flow_cons_list[0], flow_cons_list[1].name))

    for flow_prod_list in obj_dict['xml_producer_function_list']:
        result_producer_list.add((flow_prod_list[0], flow_prod_list[1].name))

    assert result_consumer_list == expected_consumer_list
    assert result_producer_list == expected_producer_list

    test_lib.remove_xml_file(file_name)


def test_function_output_auto_external_xml(input_test_function_output_auto_decomposition):
    """@ingroup test_xml_file
    @anchor test_function_output_auto_external_xml
    Test function decomposition done in multiple cells and with external function

    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[2]}\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    assert len(obj_dict['xml_function_list']) == 4

    expected_consumer_list = {('a', 'F2'), ('a', 'FE')}
    expected_producer_list = {('a', 'F1'), ('a', 'F')}

    result_consumer_list = set()
    result_producer_list = set()
    for flow_cons_list in obj_dict['xml_consumer_function_list']:
        result_consumer_list.add((flow_cons_list[0], flow_cons_list[1].name))

    for flow_prod_list in obj_dict['xml_producer_function_list']:
        result_producer_list.add((flow_prod_list[0], flow_prod_list[1].name))

    assert result_consumer_list == expected_consumer_list
    assert result_producer_list == expected_producer_list

    test_lib.remove_xml_file(file_name)