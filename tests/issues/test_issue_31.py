"""@defgroup test_issue_31
Tests about function children production and consumption related to https://github.com/rcasteran/jarvis4se/issues/31

@see test_issue_31_context
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_31_context(mocker, input_test_issue_31):
    """@ingroup test_context_diagrams
    @anchor test_issue_31_context
    Test context diagram display related to @ref test_issue_31

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_31 : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_issue_31
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_issue_31"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_31}\n"
                         f"show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F1" as f1 <<Function>>\n',
                'circle f1_i\n',
                'circle f1_o\n',
                'f1_i --> f1 : ',
                'b', '\\n', 'd', '\n',
                'f1 --> f1_o  : ',
                'c', '\\n', 'a', '\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")
