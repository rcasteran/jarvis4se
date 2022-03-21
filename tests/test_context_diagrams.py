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


def test_simple_function_in_out(mocker):
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
