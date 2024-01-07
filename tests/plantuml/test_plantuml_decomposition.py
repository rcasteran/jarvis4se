"""@defgroup test_plantuml_decomposition
Tests about Plantuml decomposition diagrams
"""
# Libraries


# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_fun_elem_simple_plantuml_decomposition(mocker, input_test_fun_elem_simple_decomposition):
    """@ingroup test_plantuml_decomposition
    @anchor test_fun_elem_simple_plantuml_decomposition
    Test decomposition diagram display with simple functional element decomposition

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_fun_elem_simple_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_simple_decomposition
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "test_fun_elem_simple_plantuml_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_simple_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_simple_decomposition[1]}\n"                         
                         "show decomposition E\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                'component "E2" as e2 <<Functional element>>{\n',
                'component "E1" as e1 <<Functional element>>{\n',
                '}\n',
                '}\n',
                '}\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 3*len("\'id: xxxxxxxxxx\n")


def test_fun_elem_with_interfaces_plantuml_decomposition(mocker, input_test_fun_elem_with_interfaces_2):
    """@ingroup test_plantuml_decomposition
    @anchor test_fun_elem_with_interfaces_plantuml_decomposition
    Test decomposition diagram display with functional element decomposition and interface allocation

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_fun_elem_with_interfaces_2 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_interfaces_2
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "test_fun_elem_with_interfaces_plantuml_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_interfaces_2}\n"                         
                         "show decomposition E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E1" as e1 <<Functional element>>{\n',
                'component "E1c" as e1c <<Functional element>>{\n',
                'component "E1c1" as e1c1 <<Functional element>>{\n',
                'object "F1c1" as f1c1 <<Function>>\n',
                '}\n',
                '}\n',
                'component "E1b" as e1b <<Functional element>>{\n',
                'object "F1b" as f1b <<Function>>\n',
                '}\n',
                '}\n',
                'component "Ext" as ext <<Functional element>>{\n',
                'object "F_ext" as f_ext <<Function>>\n',
                '}\n',
                'f_ext #--> f1c1 : B\n',
                'f1b #--> f_ext : C\n',
                'e1b', ' -- ', 'e1c1 ', ': fun_inter_a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 8*len("\'id: xxxxxxxxxx\n")


def test_function_output_auto_splitted_plantuml_decomposition(mocker, input_test_function_output_auto_decomposition):
    """@ingroup test_plantuml_decomposition
    @anchor test_function_output_auto_splitted_plantuml_decomposition
    Test decomposition diagram display with function decomposition done in multiple cells

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_output_auto_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show decomposition F\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F" as f <<Function>>{\n',
                'object "F2" as f2 <<Function>>\n',
                'object "F1" as f1 <<Function>>\n',
                '}\n',
                'f1 #--> f2 : a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 3*len("\'id: xxxxxxxxxx\n")


def test_function_output_auto_external_plantuml_decomposition(mocker, input_test_function_output_auto_decomposition):
    """@ingroup test_plantuml_decomposition
    @anchor test_function_output_auto_external_plantuml_decomposition
    Test decomposition diagram display with function decomposition done in multiple cells and with external function

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_output_auto_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[2]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show decomposition F\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F" as f <<Function>>{\n',
                'object "F2" as f2 <<Function>>\n',
                'object "F1" as f1 <<Function>>\n',
                '}\n',
                'object "FE" as fe <<Function>>\n',
                'f1 #--> f2 : a\n',
                'f1 #--> fe : a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")