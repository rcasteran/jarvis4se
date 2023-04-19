"""@defgroup test_issue_7
Tests about functional element decomposition related to https://github.com/rcasteran/jarvis4se/issues/7

@see test_issue_7_plantuml_decomposition
"""
# Libraries
import io

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_7_plantuml_decomposition(mocker, monkeypatch, input_test_issue_7):
    """@ingroup test_plantuml_decomposition
    @anchor test_issue_7_plantuml_decomposition
    Test decomposition diagram related to @ref test_issue_7

    @param[in] mocker : mocker fixture reference
    @param[in] monkeypatch : monkeypatch fixture reference
    @param[in] input_test_issue_7 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_7
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
