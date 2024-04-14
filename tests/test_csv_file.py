"""@defgroup test_csv_file
Tests about csv file generation
"""
# Libraries


# Modules
import test_lib
from csv_adapter import CsvParser3SE
from datamodel import BaseType

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
csv_parser = CsvParser3SE()


def test_simple_function_csv(input_test_simple_function):
    """@ingroup test_csv_file
    @anchor test_simple_function_csv
    Test csv file for a single function without input / output

    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_simple_function
    """
    file_name = "test_simple_function_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_simple_function}\n"
                         f"export {file_name}")

    function_list = csv_parser.parse_csv(file_name + ".csv")['csv_function_list']

    test_lib.remove_xml_file(file_name)
    test_lib.remove_csv_file(file_name)

    assert len(function_list) == 1
    assert [fun.name == "F1" for fun in function_list]


def test_instantiated_attribute_csv(input_test_fun_elem_with_attribute):
    """@ingroup test_csv_file
    @anchor test_instantiated_attribute_csv
    Test attribute instantiation in csv file

    @param[in] input_test_fun_elem_with_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_attribute
    """
    file_name = "test_instantiated_attribute_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[1]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[2]}\n"
                         f"export {file_name}\n")

    obj_dict = csv_parser.parse_csv(file_name + ".csv")

    expected = {('A', 'F1', '4,2'), ('B', 'Fun elem', '8,5'),
                ('C', 'F1', 'pink'), ('A', 'Fun elem', '100')}
    # xml_adapter.parse_csv() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result = set()
    assert len(obj_dict['csv_attribute_list']) == 3
    for attribute in obj_dict['csv_attribute_list']:
        for item in attribute.described_item_list:
            for function in obj_dict['csv_function_list']:
                if item[0] == function.id:
                    result.add((attribute.name, function.name, item[1]))
            for fun_elem in obj_dict['csv_fun_elem_list']:
                if item[0] == fun_elem.id:
                    result.add((attribute.name, fun_elem.name, item[1]))

    test_lib.remove_xml_file(file_name)
    test_lib.remove_csv_file(file_name)

    assert expected == result


def test_extended_attribute_csv(input_test_extended_attribute):
    """@ingroup test_csv_file
    @anchor test_extended_attribute_csv
    Test attribute extension in csv file

    @param[in] input_test_extended_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_extended_attribute
    """
    file_name = "test_extended_attribute_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_extended_attribute}\n"
                         f"export {file_name}\n")

    attribute_list = csv_parser.parse_csv(file_name + ".csv")['csv_attribute_list']
    expected = {('A', 'attribute type A'), ('B', 'attribute type B')}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result = set()
    assert len(attribute_list) == 2
    for attribute in attribute_list:
        result.add((attribute.name, attribute.type.name))

    test_lib.remove_xml_file(file_name)
    test_lib.remove_csv_file(file_name)

    assert expected == result


def test_functional_interface_with_attribute_csv(input_test_functional_interface_with_attribute):
    """@ingroup test_csv_file
    @anchor test_functional_interface_with_attribute_csv
    Test functional interface with attribute in csv file

    @param[in] input_test_functional_interface_with_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_functional_interface_with_attribute
    """
    file_name = "test_functional_interface_with_attribute_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_functional_interface_with_attribute}\n"
                         f"export {file_name}")

    obj_dict = csv_parser.parse_csv(file_name + ".csv")

    assert (len(obj_dict['csv_data_list']) == len(obj_dict['csv_attribute_list']) ==
            len(obj_dict['csv_fun_inter_list'])) == 1
    data = obj_dict['csv_data_list'].pop()
    fun_inter = obj_dict['csv_fun_inter_list'].pop()
    attribute = obj_dict['csv_attribute_list'].pop()
    assert data.name == 'A'
    assert fun_inter.name == 'Fun_inter'
    assert fun_inter.alias == 'FI'
    assert fun_inter.type == BaseType['FUNCTIONAL_INTERFACE']
    assert attribute.name == 'Color'
    described_item = attribute.described_item_list.pop()
    assert described_item[0] == fun_inter.id and described_item[1] == 'pink'
    assert fun_inter.allocated_data_list.pop() == data.id

    test_lib.remove_xml_file(file_name)
    test_lib.remove_csv_file(file_name)


def test_fun_elem_exposes_interface_csv(input_test_fun_elem_exposes_interface):
    """@ingroup test_csv_file
    @anchor test_fun_elem_exposes_interface_csv
    Test functional interface allocation to functional element

    @param[in] input_test_fun_elem_exposes_interface : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_exposes_interface
    """
    file_name = "test_fun_elem_exposes_interface_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_exposes_interface}\n"
                         f"export {file_name}\n")

    obj_dict = csv_parser.parse_csv(file_name + ".csv")

    expected_child = {('Fun_elem', 'Fun_elem_2'), ('Fun_elem_2', 'Fun_elem_3'),
                      ('Fun_elem_3', 'Fun_elem_4'), ('Fun_elem_4', 'Fun_elem_5'),
                      ('Fun_elem_5', 'Fun_elem_6')}
    expected_exposed = {('Fun_elem', 'Fun_inter'), ('Fun_elem_6', 'Fun_inter'),
                        ('Fun_elem_ext', 'Fun_inter')}

    assert len(obj_dict['csv_fun_inter_list']) == 1 and len(obj_dict['csv_fun_elem_list']) == 8
    fun_inter = obj_dict['csv_fun_inter_list'].pop()
    assert fun_inter.name == 'Fun_inter'

    result_exposed = set()
    result_child = set()
    for fun_elem in obj_dict['csv_fun_elem_list']:
        for child in fun_elem.child_list:
            result_child.add((fun_elem.name, child.name))
        if fun_inter.id in fun_elem.exposed_interface_list:
            result_exposed.add((fun_elem.name, fun_inter.name))

    assert expected_child == result_child
    assert expected_exposed == result_exposed

    test_lib.remove_xml_file(file_name)
    test_lib.remove_csv_file(file_name)


def test_function_output_auto_csv(input_test_function_output_auto_decomposition):
    """@ingroup test_csv_file
    @anchor test_function_output_auto_csv
    Test function decomposition

    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n"
                         f"export {file_name}\n")

    obj_dict = csv_parser.parse_csv(file_name + ".csv")

    assert len(obj_dict['csv_function_list']) == 3

    expected_consumer_list = {('a', 'F2')}
    expected_producer_list = {('a', 'F1'), ('a', 'F')}

    result_consumer_list = set()
    result_producer_list = set()
    for flow_cons_list in obj_dict['csv_consumer_function_list']:
        result_consumer_list.add((flow_cons_list[0], flow_cons_list[1].name))

    for flow_prod_list in obj_dict['csv_producer_function_list']:
        result_producer_list.add((flow_prod_list[0], flow_prod_list[1].name))

    assert result_consumer_list == expected_consumer_list
    assert result_producer_list == expected_producer_list

    test_lib.remove_xml_file(file_name)


def test_function_output_auto_splitted_csv(input_test_function_output_auto_decomposition):
    """@ingroup test_csv_file
    @anchor test_function_output_auto_splitted_csv
    Test function decomposition done in multiple cells

    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n"
                         f"export {file_name}\n")

    obj_dict = csv_parser.parse_csv(file_name + ".csv")

    assert len(obj_dict['csv_function_list']) == 3

    expected_consumer_list = {('a', 'F2')}
    expected_producer_list = {('a', 'F1')}

    result_consumer_list = set()
    result_producer_list = set()
    for flow_cons_list in obj_dict['csv_consumer_function_list']:
        result_consumer_list.add((flow_cons_list[0], flow_cons_list[1].name))

    for flow_prod_list in obj_dict['csv_producer_function_list']:
        result_producer_list.add((flow_prod_list[0], flow_prod_list[1].name))

    assert result_consumer_list == expected_consumer_list
    assert result_producer_list == expected_producer_list

    test_lib.remove_xml_file(file_name)
    test_lib.remove_csv_file(file_name)


def test_function_output_auto_external_csv(input_test_function_output_auto_decomposition):
    """@ingroup test_csv_file
    @anchor test_function_output_auto_external_csv
    Test function decomposition done in multiple cells and with external function

    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_csv"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[2]}\n"
                         f"export {file_name}\n")

    obj_dict = csv_parser.parse_csv(file_name + ".csv")

    assert len(obj_dict['csv_function_list']) == 4

    expected_consumer_list = {('a', 'F2'), ('a', 'FE')}
    expected_producer_list = {('a', 'F1'), ('a', 'F')}

    result_consumer_list = set()
    result_producer_list = set()
    for flow_cons_list in obj_dict['csv_consumer_function_list']:
        result_consumer_list.add((flow_cons_list[0], flow_cons_list[1].name))

    for flow_prod_list in obj_dict['csv_producer_function_list']:
        result_producer_list.add((flow_prod_list[0], flow_prod_list[1].name))

    assert result_consumer_list == expected_consumer_list
    assert result_producer_list == expected_producer_list

    test_lib.remove_xml_file(file_name)
    test_lib.remove_csv_file(file_name)
