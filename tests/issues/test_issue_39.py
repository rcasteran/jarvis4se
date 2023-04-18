"""@defgroup test_issue_39
Tests about function children production and consumption related to https://github.com/rcasteran/jarvis4se/issues/39

@see test_issue_39_diagram

**Jarvis4se equivalent:**

    with test_issue_39
    E is a functional element
    E1 is a functional element
    I_E_E1 is a functional interface
    E exposes I_E_E1
    E1 exposes I_E_E1
    show context E1
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_39_diagram(mocker, input_test_issue_39):
    """@ingroup test_context_diagrams
    @anchor test_issue_39_diagram
    Test context diagram display related to @ref test_issue_39

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_39 : input fixture reference
    @return none
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "test_issue_39"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_39}\n"
                         f"show context E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                '}\n',
                'component "E1" as e1 <<Functional element>>{\n',
                '}\n',
                'e1', ' -- ', 'e ', ': i_e_e1\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2 * len("\'id: xxxxxxxxxx\n")