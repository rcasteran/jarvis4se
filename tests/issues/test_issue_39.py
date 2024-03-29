"""@defgroup test_issue_39
Tests about function children production and consumption related to https://github.com/rcasteran/jarvis4se/issues/39

@see test_issue_39_plantuml_context
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_39_plantuml_context(mocker, input_test_issue_39):
    """@ingroup test_plantuml_context
    @anchor test_issue_39_plantuml_context
    Test context diagram display related to @ref test_issue_39

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_39 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_39
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "test_issue_39_plantuml_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_39}\n"
                         f"show context E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                '}\n',
                'component "E1" as e1 <<Functional element>>{\n',
                '}\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2 * len("\'id: xxxxxxxxxx\n")


def test_issue_39_input_cell(capsys, input_test_issue_39):
    """@ingroup test_input_cell
    @anchor test_issue_39_input_cell
    Test context diagram display related to @ref test_issue_39

    @param[in] capsys : capture fixture reference
    @param[in] input_test_issue_39 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_39
    """
    file_name = "test_issue_39_input_cell"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_39}\n"
                         f"show context E1\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "E is a Functional element\n",
                "E1 is a Functional element\n",
                "I_E_E1 is a Functional interface\n",
                "E exposes I_E_E1\n",
                "E1 exposes I_E_E1\n",
                "I_E_E1 does not have any allocated data (no display)\n"]

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)