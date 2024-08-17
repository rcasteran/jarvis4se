"""@defgroup test_issue_55
Tests about interface data list to https://github.com/rcasteran/jarvis4se/issues/55

@see test_issue_55_question
"""
# Libraries

# Modules
import test_lib
from jarvis.query import question_answer

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_55_question(mocker, input_test_issue_55):
    """@ingroup test_question_answer
    @anchor test_issue_55_question
    Test about interface data list to @ref test_issue_55

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_55 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_55
    """
    spy = mocker.spy(question_answer, "get_fun_intf_data")
    file_name = "test_issue_55_question"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_55}\n"                         
                         "list data I_E1_E2\n")

    result = spy.spy_return['data']
    expected = [{'Data': 'a',
                 'Last consumer Function(s)': ['F2'],
                 'Last consumer Functional element(s)': ['E2'],
                 'Last producer Function(s)': ['F1'],
                 'Last producer Functional element(s)': ['E1']}]

    test_lib.remove_xml_file(file_name)

    assert expected == result
