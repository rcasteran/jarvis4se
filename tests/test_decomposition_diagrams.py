import os
from pytest_mock import mocker
from IPython import get_ipython
from pathlib import Path

import jarvis
import plantuml_adapter


def test_function_with_childs_decomposition(mocker):
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
    spy = mocker.spy(plantuml_adapter, "plantuml_binder")
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "function_with_childs_decomposition"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "F1a is a function\n"
                    "F1b is a function\n"
                    "F1c is a function\n"
                    "F1d is a function\n"
                    "F1e is a function\n"
                    "F2 is a function\n"
                    "F3 is a function\n"
                    "\n"
                    "F1 is composed of F1a\n"
                    "F1 is composed of F1b\n"
                    "F1 is composed of F1c\n"
                    "F1 is composed of F1d\n"
                    "F1 is composed of F1e\n"
                    "\n"
                    "a is a data\n"
                    "F1 produces a\n"
                    "F2 consumes a\n"
                    "\n"
                    "F1a produces a\n"
                    "F1b consumes a\n"
                    "\n"
                    "b is a data\n"
                    "F1c produces b\n"
                    "F1d consumes b\n"
                    "\n"
                    "c is a data\n"
                    "F3 produces c\n"
                    "F1e consumes c\n"
                    "\n"
                    "show decomposition F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return[0]  # First element from returned values by plantuml_binder()
    expected = ['object "F3" as f3 <<unknown>>\n',
                'component "F1" as f1 <<unknown>>{\n',
                'object "F1c" as f1c <<unknown>>\n',
                'object "F1d" as f1d <<unknown>>\n',
                'object "F1e" as f1e <<unknown>>\n',
                'object "F1a" as f1a <<unknown>>\n',
                'object "F1b" as f1b <<unknown>>\n',
                '}\n',
                'object "F2" as f2 <<unknown>>\n',
                'f1a #--> f2 : a\n',
                'f1c #--> f1d : b\n',
                'f1a #--> f1b : a\n',
                'f3 #--> f1e : c\n']

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 8*len("\'id: xxxxxxxxxx\n")

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)
