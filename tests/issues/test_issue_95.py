"""@defgroup test_issue_95
Tests about function parent relationship related to https://github.com/rcasteran/jarvis4se/issues/95

@see test_issue_95_plantuml_context
@see test_issue_95_plantuml_chain
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_95_plantuml_context(mocker, input_test_issue_95):
    """@ingroup test_plantuml_context
    @anchor test_issue_95_plantuml_context
    Test context diagram display with a child function inputs / outputs

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_95 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_95
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_issue_95_plantuml_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_95}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         'show context "2 - C"\n')

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "2 - C" as 2__c <<Function>>\n',
                'object "4 - E" as 4__e <<Function>>\n',
                '2__c #--> 4__e : 1:A\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2 * len("\'id: xxxxxxxxxx\n")


def test_issue_95_plantuml_chain(mocker, input_test_issue_95):
    """@ingroup test_plantuml_chain
    @anchor test_issue_95_plantuml_chain
    Test chain diagram display with a child function inputs / outputs

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_95 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_95
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_issue_95_plantuml_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_95}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         'show chain "2 - C", "4 - E"\n')

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "0 - A" as 0__a <<Function>>{\n',
                'component "3 - D" as 3__d <<Function>>{\n',
                'object "4 - E" as 4__e <<Function>>\n',
                '}\n',
                'component "1 - B" as 1__b <<Function>>{\n',
                'object "2 - C" as 2__c <<Function>>\n',
                '}\n',
                '}\n'
                '2__c #--> 4__e : A\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 5 * len("\'id: xxxxxxxxxx\n")
