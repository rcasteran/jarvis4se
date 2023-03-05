"""Test module with tests associated to question_answer.py"""
from conftest import get_jarvis4se, remove_xml_file
from jarvis import question_answer

jarvis4se = get_jarvis4se()


def test_list_data_functional_interface(mocker):
    """See issue #55 Notebook equivalent:
    %%jarvis
    with list_data_functional_interface
    F1 is a function
    F2 is a function
    F3 is a function

    a is a data
    F1 produces a
    F2 consumes a
    F3 consumes a

    E1 is a functional element
    E1 allocates F1

    E2 is a functional element
    E2 allocates F2

    E3 is a functional element
    E3 allocates F3

    I_E1_E2 is a functional interface
    I_E1_E2 allocates a
    E1 exposes I_E1_E2
    E2 exposes I_E1_E2

    list data I_E1_E2
     """
    spy = mocker.spy(question_answer, "switch_data")
    file_name = "list_data_functional_interface"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "F2 is a function\n"
                         "F3 is a function\n"
                         "\n"
                         "a is a data\n"
                         "F1 produces a\n"
                         "F2 consumes a\n"
                         "F3 consumes a\n"
                         "\n"
                         "E1 is a functional element\n"
                         "E1 allocates F1\n"
                         "\n"
                         "E2 is a functional element\n"
                         "E2 allocates F2\n"
                         "\n"
                         "E3 is a functional element\n"
                         "E3 allocates F3\n"
                         "\n"
                         "I_E1_E2 is a functional interface\n"
                         "I_E1_E2 allocates a\n"
                         "E1 exposes I_E1_E2\n"
                         "E2 exposes I_E1_E2\n"
                         "\n"
                         "list data I_E1_E2\n")

    result = spy.spy_return['data']
    expected = [{'Data': 'a',
                 'Last consumer Function(s)': ['F2'],
                 'Last consumer Functional element(s)': ['E2'],
                 'Last producer Function(s)': ['F1'],
                 'Last producer Functional element(s)': ['E1']}]

    remove_xml_file(file_name)

    assert expected == result
