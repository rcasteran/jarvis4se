"""@defgroup test_plantuml_chain
Tests about Plantuml chain diagrams
"""
# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_function_plantuml_chain(mocker, input_test_function_plantuml_chain):
    """@ingroup test_plantuml_chain
    @anchor test_function_plantuml_chain
    Test chain diagram display with three functions: two externals and one with 3 levels of composition

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_function_plantuml_chain : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref test_function_plantuml_chain
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_plantuml_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_plantuml_chain}\n"
                         "show chain F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F1" as f1 <<Function>>\n',
                'circle f1_i\n',
                'circle f1_o\n',
                'f1_i --> f1 : a\n',
                'f1 --> f1_o  : d\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")


def test_function_with_context_plantuml_chain(mocker, input_test_function_plantuml_chain):
    """@ingroup test_plantuml_chain
    @anchor test_function_with_context_plantuml_chain
    Test chain diagram display with three functions: two externals and one with 3 levels of composition

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_function_plantuml_chain : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref test_function_plantuml_chain
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_with_context_plantuml_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_plantuml_chain}\n"
                         "show chain F1, FE1, FE2\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F1" as f1 <<Function>>\n',
                'object "FE2" as fe2 <<Function>>\n',
                'object "FE1" as fe1 <<Function>>\n',
                'fe1 #--> f1 : a\n',
                'f1 #--> fe2 : d\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 3*len("\'id: xxxxxxxxxx\n")


def test_function_child_with_context_plantuml_chain(mocker, input_test_function_plantuml_chain):
    """@ingroup test_plantuml_chain
    @anchor test_function_child_with_context_plantuml_chain
    Test chain diagram display with three functions: two externals and one with 3 levels of composition

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_function_plantuml_chain : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref test_function_plantuml_chain
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_child_with_context_plantuml_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_plantuml_chain}\n"
                         "show chain FE1, F2, F3, FE2\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F1" as f1 <<Function>>{\n',
                'object "F2" as f2 <<Function>>\n',
                'object "F3" as f3 <<Function>>\n',
                '}\n',
                'object "FE1" as fe1 <<Function>>\n',
                'object "FE2" as fe2 <<Function>>\n',
                'f3 #--> fe2 : d\n',
                'f2 #--> f3 : b\n',
                'fe1 #--> f2 : a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 5*len("\'id: xxxxxxxxxx\n")


def test_function_child_child_with_context_plantuml_chain(mocker, input_test_function_plantuml_chain):
    """@ingroup test_plantuml_chain
    @anchor test_function_child_child_with_context_plantuml_chain
    Test chain diagram display with three functions: two externals and one with 3 levels of composition

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_function_plantuml_chain : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref test_function_plantuml_chain
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_child_child_with_context_plantuml_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_plantuml_chain}\n"
                         "show chain FE1, F2, F4, F5, FE2\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F1" as f1 <<Function>>{\n',
                'object "F2" as f2 <<Function>>\n',
                'component "F3" as f3 <<Function>>{\n',
                'object "F4" as f4 <<Function>>\n',
                'object "F5" as f5 <<Function>>\n',
                '}\n',
                '}\n',
                'object "FE1" as fe1 <<Function>>\n',
                'object "FE2" as fe2 <<Function>>\n',
                'f4 #--> f5 : c\n',
                'f5 #--> fe2 : d\n',
                'f2 #--> f4 : b\n',
                'fe1 #--> f2 : a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 7*len("\'id: xxxxxxxxxx\n")
