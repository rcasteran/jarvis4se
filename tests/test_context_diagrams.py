import os
from pytest_mock import mocker
from IPython import get_ipython
from pathlib import Path

import jarvis
import plantuml_adapter


def test_simple_function_context(mocker):
    """Notebook equivalent:
     %%jarvis
     with simple_function_context
     F1 is a function
     show context F1

     """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "simple_function_context"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by get_function_diagrams()
    expected = 'object "F1" as f1 <<unknown>>\n'
    assert expected in result
    assert len(result) - len(expected) == len("\'id: xxxxxxxxxx\n")
    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "simple_function_in_out"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "a is a data\n"
                    "b is a data\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 produces b\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 consumes a\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by get_function_diagrams()
    expected = 'object "F1" as f1 <<unknown>>\n' \
               'circle f1_i\n' \
               'circle f1_o\n' \
               'f1_i --> f1 : a\n' \
               'f1 --> f1_o  : b\n'
    assert expected in result
    assert len(result) - len(expected) == len("\'id: xxxxxxxxxx\n")
    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "test_function_with_attribute"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "A is an attribute\n"
                    "C is an attribute\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "The A of F1 is 4,2\n"
                    "The C of F1 is pink\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by get_function_diagrams()
    expected = ['object "F1" as f1 <<unknown>> {\n', 'A = 4,2\n', 'C = pink\n', '}\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "fun_elem_context_with_attribute"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "Fun elem is a functional element\n"
                    "F1 is allocated to Fun elem")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "A is an attribute\n"
                    "B is an attribute. C is an attribute\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "The A of F1 is 4,2\n"
                    "The C of F1 is pink\n"
                    "The B of Fun elem is 8,5.\n"
                    "The A of Fun elem is 100\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "show context Fun elem\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by get_function_diagrams()
    expected = ['component "Fun elem" as fun_elem <<unknown>>{\n',
                'object "F1" as f1 <<unknown>> {\n',
                'A = 4,2\n',
                'C = pink\n',
                '}\n}\n',
                'note bottom of fun_elem\n',
                'A = 100\n',
                'B = 8,5\n',
                'end note\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2*len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_function_context_with_grandkids(mocker):
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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "function_context_with_grandkids"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "F1a is a function\n"
                    "F1a1 is a function\n"
                    "F1 is composed of F1a\n"
                    "F1a is composed of F1a1\n"
                    "a is a data\n"
                    "F1a produces a\n"
                    "b is a data\n"
                    "F1a consumes b\n"
                    "c is a data\n"
                    "F1a1 produces c\n"
                    "d is a data\n"
                    "F1a1 consumes d\n"
                    "\n"
                    "show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by get_function_diagrams()
    expected = ['object "F1" as f1 <<unknown>>\n',
                'circle f1_i\n',
                'circle f1_o\n',
                'f1_i --> f1 : ',
                'b', '\\n', 'd', '\n',
                'f1 --> f1_o  : ',
                'c', '\\n', 'a', '\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "fun_elem_context_with_interfaces"
    my_magic.jarvis("", "with %s\n" % file_name +
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
    result = spy.spy_return[0]  # First element from get_fun_elem_context_diagram()
    expected = ['component "Fun_elem_2" as fun_elem_2 <<unknown>>{\n',
                'object "F2" as f2 <<unknown>>\n',
                '}\n',
                'component "Fun_elem_1" as fun_elem_1 <<unknown>>{\n',
                'object "F1" as f1 <<unknown>>\n',
                '}\n',
                'circle f1_o\n',
                'f1 --> f1_o  : C\n'
                'f2 #--> f1 : B\n',
                'fun_elem_1', ' -- ', 'fun_elem_2 ', ': fun_inter_1\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "fun_elem_context_interface_with_no_flow"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "E is a functional element\n"
                    "E1 is a functional element\n"
                    "I_E_E1 is a functional interface\n"
                    "E exposes I_E_E1\n"
                    "E1 exposes I_E_E1\n"
                    "\n"
                    "show context E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from get_fun_elem_context_diagram()
    expected = ['component "E" as e <<unknown>>{\n',
                '}\n',
                'component "E1" as e1 <<unknown>>{\n',
                '}\n',
                'e1', ' -- ', 'e ', ': i_e_e1\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2*len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "fun_elem_context_interface_not_exposed"
    my_magic.jarvis("", "with %s\n" % file_name +
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
    result = spy.spy_return[0]  # First element from get_fun_elem_context_diagram()
    expected = ['component "E" as e <<unknown>>{\n',
                'object "F" as f <<unknown>>\n',
                '}\n',
                'component "E2" as e2 <<unknown>>{\n',
                'object "F2" as f2 <<unknown>>\n',
                '}\n',
                'f #--> f2 : ',
                'a', '\\n', 'b', '\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


# TODO: Add childs to external fun_elem or create new test
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
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "fun_elem_context_interface_with_child"
    my_magic.jarvis("", "with %s\n" % file_name +
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
    result = spy.spy_return[0]  # First element from get_fun_elem_context_diagram()
    expected = ['component "E" as e <<unknown>>{\n',
                'object "F" as f <<unknown>>\n',
                '}\n',
                'component "E1" as e1 <<unknown>>{\n',
                'object "F1" as f1 <<unknown>>\n',
                '}\n',
                'e1', ' -- ', 'e ', ': i_e_e1\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4*len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)
