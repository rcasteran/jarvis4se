"""@defgroup test_issue_38
Tests about functional elements related to https://github.com/rcasteran/jarvis4se/issues/38

@see test_issue_38_diagram

**Jarvis4se equivalent:**

    with test_issue_38
    F is a function
    F1 is a function
    F2 is a function
    a is a data
    F produces a
    F1 consumes a
    F2 consumes a
    b is a data
    F produces b
    F2 consumes b

    E is a functional element
    E allocates F
    E1 is a functional element
    E1 allocates F1
    E2 is a functional element
    E2 allocates F2

    I_E_E1 is a functional interface
    I_E_E1 allocates a
    E exposes I_E_E1
    E1 exposes I_E_E1

    show context E2

"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_38_diagram(mocker, input_test_issue_38):
    """@ingroup test_context_diagrams
    @anchor test_issue_38_diagram
    Test context diagram display related to @ref test_issue_38

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_38 : input fixture reference
    @return none
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

