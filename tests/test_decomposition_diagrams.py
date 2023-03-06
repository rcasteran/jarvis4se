"""Module to tests decomposition diagrams"""
import io

from conftest import get_jarvis4se, remove_xml_file
import plantuml_adapter

jarvis4se = get_jarvis4se()


def test_function_with_childs_decomposition(mocker, function_with_childs_cell):
    """See Issue #5, Notebook equivalent:
    %%jarvis
    with function_with_childs_decomposition
    F1 is a function
    F1a is a function
    F1b is a function
    F1c is a function
    F1d is a function
    F1e is a function
    F2 is a function
    F3 is a function

    F1 is composed of F1a
    F1 is composed of F1b
    F1 is composed of F1c
    F1 is composed of F1d
    F1 is composed of F1e

    a is a data
    F1 produces a
    F2 consumes a

    F1a produces a
    F1b consumes a

    b is a data
    F1c produces b
    F1d consumes b

    c is a data
    F3 produces c
    F1e consumes c

    show decomposition F1
     """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "function_with_childs_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{function_with_childs_cell}\n"
                         "show decomposition F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F3" as f3 <<Function>>\n',
                'component "F1" as f1 <<Function>>{\n',
                'object "F1c" as f1c <<Function>>\n',
                'object "F1d" as f1d <<Function>>\n',
                'object "F1e" as f1e <<Function>>\n',
                'object "F1a" as f1a <<Function>>\n',
                'object "F1b" as f1b <<Function>>\n',
                '}\n',
                'object "F2" as f2 <<Function>>\n',
                'f1a #--> f2 : a\n',
                'f1c #--> f1d : b\n',
                'f1a #--> f1b : a\n',
                'f3 #--> f1e : c\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 8*len("\'id: xxxxxxxxxx\n")


def test_fun_elem_decompo_with_no_flow(mocker, monkeypatch):
    """Notebook equivalent (see Issue_#7):
    %%jarvis
    with fun_elem_decompo_with_no_flow
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
    monkeypatch.setattr('sys.stdin', io.StringIO('y'))  # Say yes for adding F3 alloacted to E1
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "fun_elem_decompo_with_no_flow"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "F1a is a function\n"
                         "F1b is a function\n"
                         "F1c is a function\n"
                         "F1 is composed of F1a\n"
                         "F1 is composed of F1b\n"
                         "F1 is composed of F1c\n"
                         "\n"
                         "F1c1 is a function\n"
                         "F1c is composed of F1c1\n"
                         "\n"
                         "F2 is a function\n"
                         "F2a is a function\n"
                         "F2 is composed of F2a\n"
                         "\n"
                         "F3 is a function\n"
                         "F3a is a function\n"
                         "F3 is composed of F3a\n"
                         "\n"
                         "E1 is a functional element\n"
                         "E1a is a functional element\n"
                         "E1b is a functional element\n"
                         "E1c is a functional element\n"
                         "E1 is composed of E1a\n"
                         "E1 is composed of E1b\n"
                         "E1 is composed of E1c\n"
                         "E1c1 is a functional element\n"
                         "E1c2 is a functional element\n"
                         "E1c is composed of E1c1\n"
                         "E1c is composed of E1c2\n"
                         "\n"
                         "E1 allocates F1\n"
                         "E1 allocates F2\n"
                         "E1a allocates F1a\n"
                         "E1a allocates F3a\n"
                         "E1b allocates F1b\n"
                         "E1c allocates F1c\n"
                         "E1c1 allocates F1c1\n"
                         "\n"
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

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 11*len("\'id: xxxxxxxxxx\n")


def test_fun_elem_decompo_with_no_childs(mocker):
    """See Issue #13, Notebook equivalent:
    %%jarvis
    with fun_elem_decompo_with_no_childs
    F1 is a function
    F2 is a function
    F1 is composed of F2
    E1 is a functional element
    E1 allocates F1

    show decomposition E1
     """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "fun_elem_decompo_with_no_childs"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "F2 is a function\n"
                         "F1 is composed of F2\n"
                         "E1 is a functional element\n"
                         "E1 allocates F1\n"
                         "\n"
                         "show decomposition E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E1" as e1 <<Functional element>>{\n',
                '}\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")


def test_fun_elem_decompo_with_interface(mocker):
    """Notebook equivalent:
    %%jarvis
    with fun_elem_decompo_with_interface
    F1 is a function
    F1b is a function
    F1c is a function
    F1 is composed of F1b
    F1 is composed of F1c

    F1c1 is a function
    F1c is composed of F1c1

    F_ext is a function

    E1 is a functional element
    E1b is a functional element
    E1c is a functional element
    Ext is a functional element
    E1 is composed of E1c
    E1 is composed of E1b
    E1c1 is a functional element
    E1c is composed of E1c1

    E1 allocates F1
    E1b allocates F1b
    E1c allocates F1c
    E1c1 allocates F1c1
    Ext allocates F_ext

    A is a data
    A_2 is a data
    B is a data
    C is a data

    Fun_inter_A is a functional interface
    Fun_inter_A allocates A
    Fun_inter_A allocates A_2
    Fun_inter_B is a functional interface
    Fun_inter_B allocates B

    F1c1 produces A
    F1c1 produces A_2
    F1b consumes A
    F1b consumes A_2

    F_ext produces B
    F1c1 consumes B

    F1b produces C
    F_ext consumes C

    E1c exposes Fun_inter_A
    E1c1 exposes Fun_inter_A
    E1b exposes Fun_inter_A

    show decomposition E1
     """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "fun_elem_decompo_with_interface"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "F1b is a function\n"
                         "F1c is a function\n"
                         "F1 is composed of F1b\n"
                         "F1 is composed of F1c\n"
                         "\n"
                         "F1c1 is a function\n"
                         "F1c is composed of F1c1\n"
                         "\n"
                         "F_ext is a function\n"
                         "\n"
                         "E1 is a functional element\n"
                         "E1b is a functional element\n"
                         "E1c is a functional element\n"
                         "Ext is a functional element\n"
                         "E1 is composed of E1b\n"
                         "E1 is composed of E1c\n"
                         "E1c1 is a functional element\n"
                         "E1c is composed of E1c1\n"
                         "\n"
                         "E1 allocates F1\n"
                         "E1b allocates F1b\n"
                         "E1c allocates F1c\n"
                         "E1c1 allocates F1c1\n"
                         "Ext allocates F_ext\n"
                         "\n"
                         "A is a data\n"
                         "A_2 is a data\n"
                         "B is a data\n"
                         "C is a data\n"
                         "\n"
                         "Fun_inter_A is a functional interface\n"
                         "Fun_inter_A allocates A\n"
                         "Fun_inter_A allocates A_2\n"
                         "Fun_inter_B is a functional interface\n"
                         "Fun_inter_B allocates B\n"
                         "\n"
                         "F1c1 produces A\n"
                         "F1c1 produces A_2\n"
                         "F1b consumes A\n"
                         "F1b consumes A_2\n"
                         "\n"
                         "F_ext produces B\n"
                         "F1c1 consumes B\n"
                         "\n"
                         "F1b produces C\n"
                         "F_ext consumes C\n"
                         "\n"
                         "E1c exposes Fun_inter_A\n"
                         "E1c1 exposes Fun_inter_A\n"
                         "E1b exposes Fun_inter_A\n"
                         "\n"
                         "show decomposition E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E1" as e1 <<Functional element>>{\n',
                'component "E1c" as e1c <<Functional element>>{\n',
                'component "E1c1" as e1c1 <<Functional element>>{\n',
                'object "F1c1" as f1c1 <<Function>>\n',
                '}\n',
                '}\n',
                'component "E1b" as e1b <<Functional element>>{\n',
                'object "F1b" as f1b <<Function>>\n',
                '}\n',
                '}\n',
                'component "Ext" as ext <<Functional element>>{\n',
                'object "F_ext" as f_ext <<Function>>\n',
                '}\n',
                'f_ext #--> f1c1 : B\n',
                'f1b #--> f_ext : C\n',
                'e1b', ' -- ', 'e1c1 ', ': fun_inter_a\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 8*len("\'id: xxxxxxxxxx\n")
