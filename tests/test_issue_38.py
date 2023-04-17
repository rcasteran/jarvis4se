"""@defgroup test_context_diagrams
Tests about context diagrams
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_38(mocker, input_test_issue_38):
    """@ingroup test_context_diagrams
    @anchor test_issue_38
    Test context diagram display with functional elements related to
    https://github.com/rcasteran/jarvis4se/issues/38

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_38 : input fixture reference
    @return none

    **Jarvis4se equivalent:**\n
    with test_issue_38\n
    F is a function\n
    F1 is a function\n
    F2 is a function\n
    a is a data\n
    F produces a\n
    F1 consumes a\n
    F2 consumes a\n
    b is a data\n
    F produces b\n
    F2 consumes b\n

    E is a functional element\n
    E allocates F\n
    E1 is a functional element\n
    E1 allocates F1\n
    E2 is a functional element\n
    E2 allocates F2\n

    I_E_E1 is a functional interface\n
    I_E_E1 allocates a\n
    E exposes I_E_E1\n
    E1 exposes I_E_E1\n

    show context E2\n
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

