"""@defgroup test_issue_13
Tests about functional element decomposition without children related to https://github.com/rcasteran/jarvis4se/issues/13

@see test_issue_13_plantuml_decomposition
"""
# Libraries


# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_13_plantuml_decomposition(mocker, input_test_issue_13):
    """@ingroup test_plantuml_decomposition
    @anchor test_issue_13_plantuml_decomposition
    Test decomposition diagram related to @ref test_issue_13

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_13 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_7
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "test_issue_13_plantuml_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_13}\n"                         
                         "show decomposition E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E1" as e1 <<Functional element>>{\n',
                '}\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")
