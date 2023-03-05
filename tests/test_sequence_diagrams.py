"""Module to test sequece diagrams"""
from conftest import get_jarvis4se, remove_xml_file
import plantuml_adapter

jarvis4se = get_jarvis4se()


def test_fun_inter_simple_sequence(mocker):
    """Notebook equivalent:
    %%jarvis
    with fun_inter_simple_sequence
    Fun_inter is a functional interface
    Fun_elem_1 is a functional element
    Fun_elem_2 is a functional element
    A is a data
    B is a data
    C is a data
    F1 is a function
    F2 is a function
    F1 produces A
    F1 produces C
    F2 consumes C
    F2 produces B
    F1 consumes B
    F2 consumes A
    C implies B
    B implies A
    Fun_elem_1 allocates F1
    Fun_elem_2 allocates F2
    Fun_elem_1 exposes Fun_inter
    Fun_elem_2 exposes Fun_inter
    Fun_inter allocates A
    Fun_inter allocates B
    Fun_inter allocates C

    show sequence Fun_inter
     """
    spy = mocker.spy(plantuml_adapter, "get_sequence_diagram")
    file_name = "fun_inter_simple_sequence"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "Fun_inter is a functional interface\n"
                         "Fun_elem_1 is a functional element\n"
                         "Fun_elem_2 is a functional element\n"
                         "A is a data\n"
                         "B is a data\n"
                         "C is a data\n"
                         "F1 is a function\n"
                         "F2 is a function\n"
                         "F1 produces A\n"
                         "F1 produces C\n"
                         "F2 consumes C\n"
                         "F2 produces B\n"
                         "F1 consumes B\n"
                         "F2 consumes A\n"
                         "C implies B\n"
                         "B implies A\n"
                         "Fun_elem_1 allocates F1\n"
                         "Fun_elem_2 allocates F2\n"
                         "Fun_elem_1 exposes Fun_inter\n"
                         "Fun_elem_2 exposes Fun_inter\n"
                         "Fun_inter allocates A\n"
                         "Fun_inter allocates B\n"
                         "Fun_inter allocates C\n"
                         "\n"
                         "show sequence Fun_inter\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['!pragma teoz true\n',
                'participant fun_elem_1 <<Functional element>>\n',
                'participant fun_elem_2 <<Functional element>>\n',
                'activate fun_elem_1\n',
                'activate fun_elem_2\n',
                'fun_elem_1 -> fun_elem_2 : 1- A\n',
                'fun_elem_2 -> fun_elem_1 : 2- B\n',
                'fun_elem_1 -> fun_elem_2 : 3- C\n',
                'deactivate fun_elem_1\n',
                'deactivate fun_elem_2\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) == len(''.join(expected))
