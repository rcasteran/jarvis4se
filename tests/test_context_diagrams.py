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
    spy = mocker.spy(plantuml_adapter, "plantuml_binder")
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "simple_function_context"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "show context F1\n")
    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by plantuml_binder()
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
    spy = mocker.spy(plantuml_adapter, "plantuml_binder")
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
    result = spy.spy_return[0]  # First element from returned values by plantuml_binder()
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
    spy = mocker.spy(plantuml_adapter, "plantuml_binder")
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
    result = spy.spy_return[0]  # First element from returned values by plantuml_binder()
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
     with fun_elem_with_attribute
     F1 is a function
     Fun elem is a functional element
     F1 is allocated to Fun elem
     ========================================
     %%jarvis
     with fun_elem_with_attribute
     A is an attribute
     B is an attribute. C is an attribute
     ========================================
     %%jarvis
     with fun_elem_with_attribute
     The A of F1 is 4,2
     The C of F1 is pink
     The B of Fun elem is 8,5.
     The A of Fun elem is 100
     """
    spy = mocker.spy(plantuml_adapter, "plantuml_binder")
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "fun_elem_with_attribute"
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
    result = spy.spy_return[0]  # First element from returned values by plantuml_binder()
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
    spy = mocker.spy(plantuml_adapter, "plantuml_binder")
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
    result = spy.spy_return[0]  # First element from returned values by plantuml_binder()
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
