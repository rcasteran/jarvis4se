"""@defgroup test_issue_82
Tests about functional chain related to https://github.com/rcasteran/jarvis4se/issues/82

@see test_issue_82_plantuml_chain
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_82_plantuml_chain(mocker, input_test_issue_82):
    """@ingroup test_plantuml_chain
    @anchor test_issue_82_plantuml_chain
    Test functional chain display related to @ref test_issue_82

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_82 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_82
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_issue_82_plantuml_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_82}\n"
                         "show chain F12, F13, F141, F142\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F1" as f1 <<Function>>{\n',
                'object "F13" as f13 <<Function>>\n',
                'object "F12" as f12 <<Function>>\n',
                'component "F14" as f14 <<Function>>{\n',
                'object "F142" as f142 <<Function>>\n',
                'object "F141" as f141 <<Function>>\n',
                '}\n',
                '}\n',
                'circle f12_i\n',
                'circle f142_o\n',
                'f12_i --> f12 : a\n',
                'f142 --> f142_o  : e\n',
                'f12 #--> f13 : b\n',
                'f13 #--> f141 : c\n',
                'f141 #--> f142 : d\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 6*len("\'id: xxxxxxxxxx\n")
