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
                "Function F1 is allocated to chain test_chain\n",
                "Data a is allocated to chain test_chain\n",
                "FunctionalElement Fun_elem is allocated to chain test_chain\n",
                "Function F2 with a long name is allocated to chain test_chain\n",
                "Function F3 is allocated to chain test_chain\n",
                "Function F4 is allocated to chain test_chain\n",
                f"{file_name}.xml updated\n"]
    # Get las part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]
    assert all(i in last_out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_functional_interface_input(capsys):
    """Notebook equivalent:
    %%jarvis
    with functional_interface_input
    Color is an attribute
    A is a data
    Fun_inter is a functional interface.
    The type of Fun_inter is a_type
    The alias of Fun_inter is FI
    The Color of Fun_inter is pink
    Fun_inter allocates A.
    """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "functional_interface_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "Color is an attribute\n"
                    "A is a data\n"
                    "Fun_inter is a functional interface.\n"
                    "The type of Fun_inter is a_type\n"
                    "The alias of Fun_inter is FI\n"
                    "The Color of Fun_inter is pink\n"
                    "Fun_inter allocates A.\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "A is a data\n",
                "Fun_inter is a functional interface\n",
                "Color is an attribute\n",
                "The alias for Fun_inter is FI\n",
                "Data A has no producer(s) nor consumer(s), not added to Fun_inter\n",
                "The type of Fun_inter is a_type\n",
                "Attribute Color for Fun_inter with value pink\n",
                f"{file_name}.xml updated\n"]

    assert len(captured.out) == len("".join(expected))
    assert all(i in captured.out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_fun_elem_exposes_interface_input(capsys):
    """Notebook equivalent:
    %%jarvis
    with fun_elem_exposes_interface_input
    Fun_inter is a functional interface
    Fun_elem is a functional element
    Fun_elem_2 is a functional element
    Fun_elem_3 is a functional element
    Fun_elem_4 is a functional element
    Fun_elem_5 is a functional element
    Fun_elem_6 is a functional element
    Fun_elem_ext is a functional element
    Fun_elem_ext_2 is a functional element
    Fun_elem is composed of Fun_elem_2
    Fun_elem_2 is composed of Fun_elem_3
    Fun_elem_3 is composed of Fun_elem_4
    Fun_elem_4 is composed of Fun_elem_5
    Fun_elem_5 is composed of Fun_elem_6
    Fun_elem exposes Fun_inter
    Fun_elem_6 exposes Fun_inter
    Fun_elem_ext exposes Fun_inter
    Fun_elem_ext_2 exposes Fun_inter
    toto exposes Fun_inter
    tata exposes titi
    Fun_elem exposes coco
    """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "fun_elem_exposes_interface_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "Fun_inter is a functional interface\n"
                    "Fun_elem is a functional element\n"
                    "Fun_elem_2 is a functional element\n"
                    "Fun_elem_3 is a functional element\n"
                    "Fun_elem_4 is a functional element\n"
                    "Fun_elem_5 is a functional element\n"
                    "Fun_elem_6 is a functional element\n"
                    "Fun_elem_ext is a functional element\n"
                    "Fun_elem_ext_2 is a functional element\n"
                    "Fun_elem is composed of Fun_elem_2\n"
                    "Fun_elem_2 is composed of Fun_elem_3\n"
                    "Fun_elem_3 is composed of Fun_elem_4\n"
                    "Fun_elem_4 is composed of Fun_elem_5\n"
                    "Fun_elem_5 is composed of Fun_elem_6\n"
                    "Fun_elem exposes Fun_inter\n"
                    "Fun_elem_6 exposes Fun_inter\n"
                    "Fun_elem_ext exposes Fun_inter\n"
                    "Fun_elem_ext_2 exposes Fun_inter\n"
                    "toto exposes Fun_inter\n"
                    "tata exposes titi\n"
                    "Fun_elem exposes coco\n")

    captured = capsys.readouterr()
    expected = ["Fun_elem exposes Fun_inter\n",
                "Fun_elem_6 exposes Fun_inter\n",
                "Fun_elem_ext exposes Fun_inter\n",
                "toto does not exist, choose a valid name/alias for: "
                "'Functional Element' exposes Fun_inter\n",
                "tata and titi do not exist, choose valid names/aliases for: "
                "'Functional Element' exposes 'Functional Interface'\n",
                "coco does not exist, choose a valid name/alias for: "
                "Fun_elem exposes 'Functional Interface'\n",
                f"{file_name}.xml updated\n"]
    # Get last part from capsys
    last_out = captured.out[-len(''.join(expected)):len(captured.out)]
    assert all(i in last_out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)
