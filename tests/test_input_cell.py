"""Modules containing tests to check jarvis ouput i.e. jupyter notebook output messages"""
from conftest import get_jarvis4se, remove_xml_file

jarvis4se = get_jarvis4se()


def test_attribute_declaration_input(capsys):
    """Notebook equivalent:
     %%jarvis
     with attribute_declaration_input
     A is an attribute
     B is an attribute. C is an attribute

     """
    file_name = "attribute_declaration_input"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "A is an attribute\n"
                         "B is an attribute. C is an attribute\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "C is an attribute\n",
                "A is an attribute\n",
                "B is an attribute\n",
                f"{file_name}.xml updated"]

    remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_described_attribute_input(capsys, attribute_cell):
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
    file_name = "described_attribute_input"
    jarvis4se.jarvis("", f"with {file_name}\n{attribute_cell[0]}")
    jarvis4se.jarvis("", f"with {file_name}\n{attribute_cell[1]}")
    jarvis4se.jarvis("", f"with {file_name}\n{attribute_cell[2]}")

    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                "Attribute A for F1 with value 4,2\n",
                "Attribute C for F1 with value pink\n",
                "Attribute B for Fun elem with value 8,5\n",
                "Attribute A for Fun elem with value 100\n",
                f"{file_name}.xml updated\n"]
    # Get las part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]

    remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_set_object_type_alias_input(capsys):
    # Can be extend to test with source/destination
    """ In order to check Issue #21 causing bad regex match between type, alias and
    described attribute. Notebook equivalent:
    %%jarvis
    with set_object_type_alias_input
    F1 is a function.
    high level function extends function. The alias of F1 is f1. The type of f1 is high level function
    ========================================

    """
    file_name = "set_object_type_alias_input"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function.\n"
                         "high level function extends function. The alias of F1 is f1. "
                         "The type of f1 is high level function\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "high level function is a type extending Function\n"
                "F1 is a Function\n",
                "The alias for F1 is f1\n",
                "The type of F1 is high level function\n",
                f"{file_name}.xml updated\n"]

    remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)
    assert len(captured.out) == len(''.join(expected))


def test_consider_object_input(capsys, allocation_item_cell):
    """ Relative to Issue #9 to add new allocated item to a view(i.e. filter). Notebook equivalent:
    %%jarvis
    with consider_object_input
    F1 is a function
    F2 with a long name is a function. The alias of F2 with a long name is F2
    F3 is a function
    F4 is a function
    a is a data
    Fun_elem is a functional element
    ========================================
    %%jarvis
    with consider_object_input
    under test_view
    consider F1. consider toto. consider a, Fun_elem
    consider tata.
    consider F1, F2, F3, F4
    """
    file_name = "consider_object_input"
    jarvis4se.jarvis("", f"with {file_name}\n{allocation_item_cell[0]}")
    jarvis4se.jarvis("", f"with {file_name}\n{allocation_item_cell[1]}")

    captured = capsys.readouterr()

    expected = [f"{file_name}.xml parsed\n",
                "test_view is a view\n",
                "[WARNING] Object toto does not exist, available object types are : "
                "Functional Element, Function and Data\n",
                "[WARNING] Object tata does not exist, available object types are : "
                "Functional Element, Function and Data\n",
                "Function F1 is allocated to View test_view\n",
                "Data a is allocated to View test_view\n",
                "FunctionalElement Fun_elem is allocated to View test_view\n",
                "Function F2 with a long name is allocated to View test_view\n",
                "Function F3 is allocated to View test_view\n",
                "Function F4 is allocated to View test_view\n",
                f"{file_name}.xml updated\n"]

    # Get last part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]

    remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_functional_interface_input(capsys):
    """Notebook equivalent:
    %%jarvis
    with functional_interface_input
    Color is an attribute
    A is a data
    Fun_inter is a functional interface.
    The alias of Fun_inter is FI
    The Color of Fun_inter is pink
    Fun_inter allocates A.
    """
    file_name = "functional_interface_input"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "Color is an attribute\n"
                         "A is a data\n"
                         "Fun_inter is a functional interface.\n"
                         "The alias of Fun_inter is FI\n"
                         "The Color of Fun_inter is pink\n"
                         "Fun_inter allocates A.\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "A is a Data\n",
                "Fun_inter is a Functional interface\n",
                "Color is an attribute\n",
                "The alias for Fun_inter is FI\n",
                "[ERROR] Data A has no producer(s) nor consumer(s) allocated to functional "
                "elements exposing Fun_inter, A not allocated to Fun_inter\n",
                "Attribute Color for Fun_inter with value pink\n",
                f"{file_name}.xml updated\n"]

    remove_xml_file(file_name)

    assert len(captured.out) == len("".join(expected))
    assert all(i in captured.out for i in expected)


def test_fun_elem_exposes_interface_input(capsys, fun_elem_exposing_cell):
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
    file_name = "fun_elem_exposes_interface_input"
    jarvis4se.jarvis("", f"with {file_name}\n{fun_elem_exposing_cell}")

    captured = capsys.readouterr()
    expected = ["Fun_elem exposes Fun_inter\n",
                "Fun_elem_6 exposes Fun_inter\n",
                "Fun_elem_ext exposes Fun_inter\n",
                "[ERROR] toto does not exist, choose a valid name/alias for: "
                "'Functional Element' exposes Fun_inter\n",
                "[ERROR] tata and titi do not exist, choose valid names/aliases for: "
                "'Functional Element' exposes 'Functional Interface'\n",
                "[ERROR] coco does not exist, choose a valid name/alias for: "
                "Fun_elem exposes 'Functional Interface'\n",
                f"{file_name}.xml updated\n"]
    # Get last part from capsys
    last_out = captured.out[-len(''.join(expected)):len(captured.out)]

    remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_extends_and_set_type_object_input(capsys, extends_and_set_type_cell):
    """ Issue #56 Notebook equivalent:
    %%jarvis
    with extends_and_set_type_object_input
    Safety interface extends functional interface
    The alias of Safety interface is sf
    ========================================
    %%jarvis
    with extends_and_set_type_object_input
    sf_a extends sf
    sf_a_b extends sf_a
    final one extends sf_a_b
    Fun_inter is a functional interface
    The type of Fun_inter is final one
    """
    file_name = "extends_and_set_type_object_input"
    jarvis4se.jarvis("", f"with {file_name}\n{extends_and_set_type_cell[0]}")
    jarvis4se.jarvis("", f"with {file_name}\n{extends_and_set_type_cell[1]}")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "Safety interface is a type extending Functional interface\n",
                "The alias for Safety interface is sf\n",
                f"{file_name}.xml updated\n"
                f"{file_name}.xml parsed\n",
                "Fun_inter is a Functional interface\n",
                "sf_a is a type extending Safety interface\n",
                "sf_a_b is a type extending sf_a\n",
                "final one is a type extending sf_a_b\n",
                "The type of Fun_inter is final one\n",
                f"{file_name}.xml updated\n"]

    remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_extends_and_create_object_input(capsys, extends_and_create_object_cell):
    """ Issue #62 Notebook equivalent:
    %%jarvis
    with extends_and_create_object_input
    "High level function" extends function
    "High high level function" extends "High level function"
    "High high high level function" extends "High high level function"
    3High is a "High high high level function"
    """
    file_name = "extends_and_create_object_input"
    jarvis4se.jarvis("", f"with {file_name}\n{extends_and_create_object_cell}")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "High level function is a type extending Function\n",
                "High high level function is a type extending High level function\n",
                "High high high level function is a type extending High high level function\n"
                "3High is a High high high level function\n",
                f"{file_name}.xml updated\n"]

    remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)
