"""@defgroup test_issue_75
Tests about decomposition diagram level related to https://github.com/rcasteran/jarvis4se/issues/75

@see test_issue_75_no_level_plantuml_decomposition
@see test_issue_75_level_1_plantuml_decomposition
@see test_issue_75_level_2_plantuml_decomposition
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_75_no_level_plantuml_decomposition(mocker, input_test_issue_75):
    """@ingroup test_plantuml_decomposition
    @anchor test_issue_75_no_level_plantuml_decomposition
    Test decomposition diagram display related to @ref test_issue_75

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_75 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_75
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")

    file_name = "fun_elem_decomposition_level"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_75}\n"
                         "show decomposition F\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F" as f <<Function>>{\n',
                'component "F1" as f1 <<Function>>{\n',
                'object "F2" as f2 <<Function>>\n',
                'object "F3" as f3 <<Function>>\n',
                '}\n',
                '}\n',
                'f2 #--> f3 : a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")


def test_issue_75_level_1_plantuml_decomposition(mocker, input_test_issue_75):
    """@ingroup test_plantuml_decomposition
    @anchor test_issue_75_level_1_plantuml_decomposition
    Test decomposition diagram display related to @ref test_issue_75

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_75 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_75
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")

    file_name = "fun_elem_decomposition_level"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_75}\n"
                         "show decomposition F at level 1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F" as f <<Function>>{\n',
                'object "F1" as f1 <<Function>>\n',
                '}\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2*len("\'id: xxxxxxxxxx\n")


def test_issue_75_level_2_plantuml_decomposition(mocker, input_test_issue_75):
    """@ingroup test_plantuml_decomposition
    @anchor test_issue_75_level_2_plantuml_decomposition
    Test decomposition diagram display related to @ref test_issue_75

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_75 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_75
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")

    file_name = "fun_elem_decomposition_level"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_75}\n"
                         "show decomposition F at level 2\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F" as f <<Function>>{\n',
                'component "F1" as f1 <<Function>>{\n',
                'object "F2" as f2 <<Function>>\n',
                'object "F3" as f3 <<Function>>\n',
                '}\n',
                '}\n',
                'f2 #--> f3 : a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")
