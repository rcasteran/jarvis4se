"""@defgroup test_issue_81
Tests about functional decomposition related to https://github.com/rcasteran/jarvis4se/issues/81

@see test_issue_81_plantuml_context
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_81_plantuml_context(mocker, input_test_issue_81):
    """@ingroup test_plantuml_decomposition
    @anchor test_issue_81_plantuml_context
    Test context diagram display related to @ref test_issue_81

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_81 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_81
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")

    file_name = "fun_elem_decomposition_level"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_81}\n"
                         "show decomposition F2 at level 1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F2" as f2 <<Function>>{\n',
                'object "F21" as f21 <<Function>>\n',
                'object "F22" as f22 <<Function>>\n',
                '}\n',
                'object "F1" as f1 <<Function>>\n',
                'f1 #--> f21 : a\n',
                'f21 #--> f22 : b\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")