"""@defgroup test_issue_7
Tests about functional element decomposition related to https://github.com/rcasteran/jarvis4se/issues/7

@see test_issue_7_diagram

**Jarvis4se equivalent:**

    with test_issue_7
    F1 is a function
    F1a is a function
    F1b is a function
    F1c is a function
    F1 is composed of F1a
    F1 is composed of F1b
    F1 is composed of F1c

    F1c1 is a function
    F1c is composed of F1c1

    F2 is a function
    F2a is a function
    F2 is composed of F2a

    F3 is a function
    F3a is a function
    F3 is composed of F3a

    E1 is a functional element
    E1a is a functional element
    E1b is a functional element
    E1c is a functional element
    E1 is composed of E1a
    E1 is composed of E1b
    E1 is composed of E1c
    E1c1 is a functional element
    E1c2 is a functional element
    E1c is composed of E1c1
    E1c is composed of E1c2

    E1 allocates F1
    E1 allocates F2
    E1a allocates F1a
    E1a allocates F3a
    E1b allocates F1b
    E1c allocates F1c
    E1c1 allocates F1c1

    show decomposition E1
"""
# Libraries
import io

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_7_diagram(mocker, monkeypatch, input_test_issue_7):
    """@ingroup test_decomposition_diagrams
    @anchor test_issue_7_diagram
    Test decomposition diagram related to @ref test_issue_7

    @param[in] mocker : mocker fixture reference
    @param[in] monkeypatch : monkeypatch fixture reference
    @param[in] input_test_issue_7 : input fixture reference
    @return none
    """
    monkeypatch.setattr('sys.stdin', io.StringIO('y'))  # Say yes for adding F3 allocated to E1
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "test_issue_7"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_7}\n"
                         "show decomposition E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E1" as e1 <<Functional element>>{\n',
                'object "F2" as f2 <<Function>>\n',
                'component "E1b" as e1b <<Functional element>>{\n',
                'object "F1b" as f1b <<Function>>\n',
                '}\n',
                'component "E1a" as e1a <<Functional element>>{\n',
                'object "F1a" as f1a <<Function>>\n',
                'object "F3a" as f3a <<Function>>\n',
                '}\n',
                'component "E1c" as e1c <<Functional element>>{\n',
                'component "E1c1" as e1c1 <<Functional element>>{\n',
                'object "F1c1" as f1c1 <<Function>>\n',
                '}\n',
                'component "E1c2" as e1c2 <<Functional element>>{\n',
                '}\n',
                '}\n',
                '}\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 11 * len("\'id: xxxxxxxxxx\n")
