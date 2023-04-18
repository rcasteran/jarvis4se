"""@defgroup test_issue_13
Tests about functional element decomposition without children related to https://github.com/rcasteran/jarvis4se/issues/13

@see test_issue_13_diagram

**Jarvis4se equivalent:**

    with test_issue_13
    F1 is a function
    F2 is a function
    F1 is composed of F2
    E1 is a functional element
    E1 allocates F1

    show decomposition E1
"""
# Libraries


# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_13_diagram(mocker, input_test_issue_13):
    """@ingroup test_decomposition_diagrams
    @anchor test_issue_13_diagram
    Test decomposition diagram related to @ref test_issue_13

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_13 : input fixture reference
    @return none
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "test_issue_13"
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
