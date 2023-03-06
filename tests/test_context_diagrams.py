"""Module that contains tests for context diagrams"""
from conftest import get_jarvis4se, remove_xml_file
import plantuml_adapter

jarvis4se = get_jarvis4se()


def test_simple_function_context(mocker):
    """Notebook equivalent:
     %%jarvis
     with simple_function_context
     F1 is a function
     show context F1

     """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "simple_function_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = 'object "F1" as f1 <<Function>>\n'

    remove_xml_file(file_name)

    assert expected in result
    assert len(result) - len(expected) == len("\'id: xxxxxxxxxx\n")


def test_simple_function_context_in_out(mocker):
    """Notebook equivalent:
     %%jarvis
     with simple_function_in_out
     F1 is a function
     a is a data
     b is a data
     =============================
     %%jarvis
     with simple_function_in_out
     F1 produces b
     =============================
     %%jarvis
     with simple_function_in_out
     F1 consumes a
     =============================
     %%jarvis
     with simple_function_in_out
     show context F1

     """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "simple_function_in_out"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "a is a data\n"
                         "b is a data\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 produces b\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 consumes a\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = 'object "F1" as f1 <<Function>>\n' \
               'circle f1_i\n' \
               'circle f1_o\n' \
               'f1_i --> f1 : a\n' \
               'f1 --> f1_o  : b\n'

    remove_xml_file(file_name)

    assert expected in result
    assert len(result) - len(expected) == len("\'id: xxxxxxxxxx\n")


def test_function_context_with_attribute(mocker):
    """Notebook equivalent:
     %%jarvis
     with test_function_with_attribute
     F1 is a function
     ========================================
     %%jarvis
     with test_function_with_attribute
     A is an attribute
     C is an attribute
     ========================================
     %%jarvis
     with test_function_with_attribute
     The A of F1 is 4,2
     The C of F1 is pink
     ========================================
     %%jarvis
     with test_function_with_attribute
     show context F1
     """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_with_attribute"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "A is an attribute\n"
                         "C is an attribute\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "The A of F1 is 4,2\n"
                         "The C of F1 is pink\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F1" as f1 <<Function>> {\n', 'A = 4,2\n', 'C = pink\n', '}\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")


def test_fun_elem_context_with_attribute(mocker):
    """Notebook equivalent:
     %%jarvis
     with fun_elem_context_with_attribute
     F1 is a function
     Fun elem is a functional element
     F1 is allocated to Fun elem
     ========================================
     %%jarvis
     with fun_elem_context_with_attribute
     A is an attribute
     B is an attribute. C is an attribute
     ========================================
     %%jarvis
     with fun_elem_context_with_attribute
     The A of F1 is 4,2
     The C of F1 is pink
     The B of Fun elem is 8,5.
     The A of Fun elem is 100
     """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "fun_elem_context_with_attribute"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "Fun elem is a functional element\n"
                         "F1 is allocated to Fun elem")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "A is an attribute\n"
                         "B is an attribute. C is an attribute\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "The A of F1 is 4,2\n"
                         "The C of F1 is pink\n"
                         "The B of Fun elem is 8,5.\n"
                         "The A of Fun elem is 100\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show context Fun elem\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "Fun elem" as fun_elem <<Functional element>>{\n',
                'object "F1" as f1 <<Function>> {\n',
                'A = 4,2\n',
                'C = pink\n',
                '}\n}\n',
                'note bottom of fun_elem\n',
                'A = 100\n',
                'B = 8,5\n',
                'end note\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2*len("\'id: xxxxxxxxxx\n")


def test_function_context_with_grandkids(mocker, function_grandkids_cell):
    """See Issue #31, Notebook equivalent:
    %%jarvis
    with function_context_with_grandkids
    F1 is a function
    F1a is a function
    F1a1 is a function
    F1 is composed of F1a
    F1a is composed of F1a1
    a is a data
    F1a produces a
    b is a data
    F1a consumes b
    c is a data
    F1a1 produces c
    d is a data
    F1a1 consumes d

    show context F1
     """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "function_context_with_grandkids"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{function_grandkids_cell}\n"
                         f"show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F1" as f1 <<Function>>\n',
                'circle f1_i\n',
                'circle f1_o\n',
                'f1_i --> f1 : ',
                'b', '\\n', 'd', '\n',
                'f1 --> f1_o  : ',
                'c', '\\n', 'a', '\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")


def test_fun_elem_context_with_interfaces(mocker):
    """Notebook equivalent:
    %%jarvis
    with fun_elem_context_with_interfaces
    F1 is a function
    F2 is a function
    A is a data
    B is a data
    C is a data
    F1 produces A
    F2 consumes A
    F2 produces B
    F1 consumes B
    F1 produces C
    Fun_elem_1 is a functional element
    Fun_elem_2 is a functional element
    Fun_inter_1 is a functional interface
    Fun_inter_2 is a functional interface
    Fun_elem_1 allocates F1
    Fun_elem_2 allocates F2
    Fun_inter_1 allocates A
    Fun_inter_2 allocates C
    Fun_elem_1 exposes Fun_inter_1
    Fun_elem_1 exposes Fun_inter_2
    Fun_elem_2 exposes Fun_inter_1

    show context Fun_elem_1
     """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "fun_elem_context_with_interfaces"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "F2 is a function\n"
                         "A is a data\n"
                         "B is a data\n"
                         "C is a data\n"
                         "F1 produces A\n"
                         "F2 consumes A\n"
                         "F2 produces B\n"
                         "F1 consumes B\n"
                         "F1 produces C\n"
                         "Fun_elem_1 is a functional element\n"
                         "Fun_elem_2 is a functional element\n"
                         "Fun_inter_1 is a functional interface\n"
                         "Fun_inter_2 is a functional interface\n"
                         "Fun_elem_1 allocates F1\n"
                         "Fun_elem_2 allocates F2\n"
                         "Fun_inter_1 allocates A\n"
                         "Fun_inter_2 allocates C\n"
                         "Fun_elem_1 exposes Fun_inter_1\n"
                         "Fun_elem_1 exposes Fun_inter_2\n"
                         "Fun_elem_2 exposes Fun_inter_1\n"
                         "\n"
                         "show context Fun_elem_1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "Fun_elem_2" as fun_elem_2 <<Functional element>>{\n',
                'object "F2" as f2 <<Function>>\n',
                '}\n',
                'component "Fun_elem_1" as fun_elem_1 <<Functional element>>{\n',
                'object "F1" as f1 <<Function>>\n',
                '}\n',
                'circle f1_o\n',
                'f1 --> f1_o  : C\n'
                'f2 #--> f1 : B\n',
                'fun_elem_1', ' -- ', 'fun_elem_2 ', ': fun_inter_1\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")


def test_fun_elem_context_interface_with_no_flow(mocker):
    """ See issue #39, Notebook equivalent:
    %%jarvis
    with fun_elem_context_interface_with_no_flow
    E is a functional element
    E1 is a functional element
    I_E_E1 is a functional interface
    E exposes I_E_E1
    E1 exposes I_E_E1

    show context E1

    show context Fun_elem_1
     """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "fun_elem_context_interface_with_no_flow"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "E is a functional element\n"
                         "E1 is a functional element\n"
                         "I_E_E1 is a functional interface\n"
                         "E exposes I_E_E1\n"
                         "E1 exposes I_E_E1\n"
                         "\n"
                         "show context E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                '}\n',
                'component "E1" as e1 <<Functional element>>{\n',
                '}\n',
                'e1', ' -- ', 'e ', ': i_e_e1\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2*len("\'id: xxxxxxxxxx\n")


def test_fun_elem_context_interface_not_exposed(mocker):
    """ See issue #38, Notebook equivalent:
    %%jarvis
    with fun_elem_context_interface_not_exposed
    F is a function
    F1 is a function
    F2 is a function
    a is a data
    F produces a
    F1 consumes a
    F2 consumes a
    b is a data
    F produces b
    F2 consumes b

    E is a functional element
    E allocates F
    E1 is a functional element
    E1 allocates F1
    E2 is a functional element
    E2 allocates F2

    I_E_E1 is a functional interface
    I_E_E1 allocates a
    E exposes I_E_E1
    E1 exposes I_E_E1

    show context E2
     """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "fun_elem_context_interface_not_exposed"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F is a function\n"
                         "F1 is a function\n"
                         "F2 is a function\n"
                         "a is a data\n"
                         "F produces a\n"
                         "F1 consumes a\n"
                         "F2 consumes a\n"
                         "b is a data\n"
                         "F produces b\n"
                         "F2 consumes b\n"
                         "\n"
                         "E is a functional element\n"
                         "E allocates F\n"
                         "E1 is a functional element\n"
                         "E1 allocates F1\n"
                         "E2 is a functional element\n"
                         "E2 allocates F2\n"
                         "\n"
                         "I_E_E1 is a functional interface\n"
                         "I_E_E1 allocates a\n"
                         "E exposes I_E_E1\n"
                         "E1 exposes I_E_E1\n"
                         "\n"
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

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")


# Add childs to external fun_elem or create new test
def test_fun_elem_context_interface_with_child(mocker):
    """ See issue #44, Notebook equivalent:
    %%jarvis
    with fun_elem_context_interface_with_child
    F is a function
    F1 is a function
    a is a data
    F produces a
    F1 consumes a
    E is a functional element
    E1 is a functional element
    E allocates F
    E1 allocates F1
    I_E_E1 is a functional interface
    E exposes I_E_E1
    E1 exposes I_E_E1
    I_E_E1 allocates a

    E11 is a functional element
    E11 composes E
    E11 allocates F
    E11 exposes I_E_E1

    show context E
     """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "fun_elem_context_interface_with_child"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F is a function\n"
                         "F1 is a function\n"
                         "a is a data\n"
                         "F produces a\n"
                         "F1 consumes a\n"
                         "E is a functional element\n"
                         "E1 is a functional element\n"
                         "E allocates F\n"
                         "E1 allocates F1\n"
                         "I_E_E1 is a functional interface\n"
                         "E exposes I_E_E1\n"
                         "E1 exposes I_E_E1\n"
                         "I_E_E1 allocates a\n"
                         "\n"
                         "E11 is a functional element\n"
                         "E11 composes E\n"
                         "E11 allocates F\n"
                         "E11 exposes I_E_E1\n"
                         "\n"
                         "show context E\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                'object "F" as f <<Function>>\n',
                '}\n',
                'component "E1" as e1 <<Functional element>>{\n',
                'object "F1" as f1 <<Function>>\n',
                '}\n',
                'e1', ' -- ', 'e ', ': i_e_e1\n']

    remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")
