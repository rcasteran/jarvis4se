import os
from IPython import get_ipython
from pathlib import Path

import jarvis


def test_attribute_declaration_input(capsys):
    """Notebook equivalent:
     %%jarvis
     with attribute_declaration_input
     A is an attribute
     B is an attribute. C is an attribute

     """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "attribute_declaration_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "A is an attribute\n"
                    "B is an attribute. C is an attribute\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "C is an attribute\n",
                "A is an attribute\n",
                "B is an attribute\n",
                f"{file_name}.xml updated"]

    assert all(i in captured.out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_described_attribute_input(capsys):
    """Notebook equivalent:
     %%jarvis
     with described_attribute_input
     F1 is a function
     Fun elem is a functional element
     ========================================
     %%jarvis
     with described_attribute_input
     A is an attribute
     B is an attribute. C is an attribute
     ========================================
     %%jarvis
     with described_attribute_input
     The A of F1 is 4,2
     The C of F1 is pink
     The B of Fun elem is 8,5.
     The A of Fun elem is 100

     """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "described_attribute_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "Fun elem is a functional element\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "A is an attribute\n"
                    "B is an attribute. C is an attribute\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "The A of F1 is 4,2\n"
                    "The C of F1 is pink\n"
                    "The B of Fun elem is 8,5.\n"
                    "The A of Fun elem is 100\n")

    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                "Attribute A for F1 with value 4,2\n",
                "Attribute C for F1 with value pink\n",
                "Attribute B for Fun elem with value 8,5\n",
                "Attribute A for Fun elem with value 100\n",
                f"{file_name}.xml updated\n"]
    # Get las part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]
    assert all(i in last_out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_set_object_type_alias_input(capsys):
    # TODO: Needs to be extend to test with source/destination
    """ In order to check Issue #21 causing bad regex match between type, alias and
    described attribute. Notebook equivalent:
    %%jarvis
    with set_object_type_alias_input
    F1 is a function. The type of F1 is high level function
    The alias of F1 is f1
    ========================================

    """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "set_object_type_alias_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function. The type of F1 is high level function\n"
                    "The alias of F1 is f1\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "F1 is a function\n",
                "The alias for F1 is f1\n",
                "The type of F1 is High level function\n",
                f"{file_name}.xml updated\n"]

    assert all(i in captured.out for i in expected)
    assert len(captured.out) == len(''.join(expected))

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_consider_object_input(capsys):
    """ Relative to Issue #9 to add new allocated item to a chain(i.e. filter). Notebook equivalent:
    %%jarvis
    with consider_object_input
    F1 is a function
    F2 with a long name is a function. The alias of F2 with a long name is F2.
    F3 is a function
    F4 is a function
    a is a data
    Fun_elem is a functional element
    ========================================
    %%jarvis
    with consider_object_input
    under toto
    consider F1. consider toto. consider a, Fun_elem
    consider tata.
    consider F1, F2, F3, F4
    """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "consider_object_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "F2 with a long name is a function. The alias of F2 with a long name is F2.\n"
                    "F3 is a function\n"
                    "F4 is a function\n"
                    "a is a data\n"
                    "Fun_elem is a functional element\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "under test_chain\n"
                    "consider F1. consider toto. consider a, Fun_elem\n"
                    "consider tata.\n"
                    "consider F1, F2, F3, F4\n")

    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                "test_chain is a chain\n",
                "Object toto does not exist, available object types are : "
                "Functional Element, Function and Data\n",
                "Object tata does not exist, available object types are : "
                "Functional Element, Function and Data\n",
                "Function F1 allocated to chain test_chain\n",
                "Data a allocated to chain test_chain\n",
                "FunctionalElement Fun_elem allocated to chain test_chain\n",
                "Function F2 with a long name allocated to chain test_chain\n",
                "Function F3 allocated to chain test_chain\n",
                "Function F4 allocated to chain test_chain\n",
                f"{file_name}.xml updated\n"]
    # Get las part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]
    assert all(i in last_out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)
