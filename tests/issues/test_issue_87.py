"""@defgroup test_issue_87
Tests about function parent relationship related to https://github.com/rcasteran/jarvis4se/issues/87

@see test_issue_87_plantuml_context
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_87_plantuml_context(mocker, input_test_issue_87):
    """@ingroup test_plantuml_context
    @anchor test_issue_87_plantuml_context
    Test context diagram display with a parent function inputs / outputs based on child function inputs / outputs

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_87 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_87
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_issue_87_plantuml_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_87[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_87[1]}\n"
                         "show context F\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F" as f <<Function>>\n',
                'circle f_i\n',
                'circle f_o\n',
                'f_i --> f : A\n',
                'f --> f_o  : B\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")

