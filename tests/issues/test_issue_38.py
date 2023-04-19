"""@defgroup test_issue_38
Tests about functional elements related to https://github.com/rcasteran/jarvis4se/issues/38

@see test_issue_38_plantuml_context
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_38_plantuml_context(mocker, input_test_issue_38):
    """@ingroup test_plantuml_context
    @anchor test_issue_38_plantuml_context
    Test context diagram display related to @ref test_issue_38

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_38 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_38
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "test_issue_38"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_38}\n"                         
                         "show context E2\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                'object "F" as f <<Function>>\n',
                '}\n',
                'component "E2" as e2 <<Functional element>>{\n',
                'object "F2" as f2 <<Function>>\n',
                '}\n',
                'f #--> f2 : ',
                'a', '\\n', 'b', '\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4 * len("\'id: xxxxxxxxxx\n")

