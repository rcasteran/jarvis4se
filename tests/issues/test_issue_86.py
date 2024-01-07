"""@defgroup test_issue_86
Tests about functional decomposition related to https://github.com/rcasteran/jarvis4se/issues/86

@see test_issue_86_plantuml_decomposition
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_86_plantuml_decomposition(mocker, input_test_issue_86):
    """@ingroup test_plantuml_decomposition
    @anchor test_issue_86_plantuml_decomposition
    Test decomposition diagram display related to @ref test_issue_86

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_86 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_86
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")

    file_name = "test_issue_86_plantuml_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_86}\n"
                         "show decomposition F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F1" as f1 <<Function>>{\n',
                'object "F11" as f11 <<Function>>\n',
                'object "F12" as f12 <<Function>>\n',
                '}\n',
                'circle f12_i\n',
                'circle f11_i\n',
                'circle f12_o\n',
                'circle f11_o\n',
                'f12_i --> f12 : a\n',
                'f11_i --> f11 : a\n',
                'f12 --> f12_o  : b\n',
                'f11 --> f11_o  : b\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 3*len("\'id: xxxxxxxxxx\n")