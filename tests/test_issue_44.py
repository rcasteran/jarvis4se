"""@defgroup test_issue_44
Tests about functional elements and their children related to https://github.com/rcasteran/jarvis4se/issues/44

@see test_issue_44_diagram

**Jarvis4se equivalent:**

    with test_issue_44
    F is a function
    F1 is a function
    a is a data
    F produces a
    F1 consumes a
    E is a functional element
    E1 is a functional element
    E allocates F
    E1 allocates F1
    I_E_E1 is a functional interface
    E exposes I_E_E1
    E1 exposes I_E_E1
    I_E_E1 allocates a

    E11 is a functional element
    E11 composes E
    E11 allocates F
    E11 exposes I_E_E1

    show context E
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_44_diagram(mocker, input_test_issue_44):
    """@ingroup test_context_diagrams
    @anchor test_issue_44_diagram
    Test context diagram display related to @ref test_issue_44

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_44 : input fixture reference
    @return none
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "test_issue_44"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_44}\n"
                         "show context E\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                'object "F" as f <<Function>>\n',
                '}\n',
                'component "E1" as e1 <<Functional element>>{\n',
                'object "F1" as f1 <<Function>>\n',
                '}\n',
                'e1', ' -- ', 'e ', ': i_e_e1\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4 * len("\'id: xxxxxxxxxx\n")
