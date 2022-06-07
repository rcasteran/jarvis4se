"""Module containing pytest fixtures and shared methods for tests"""
import os
from pathlib import Path
import pytest
from IPython import get_ipython

import jarvis


def get_jarvis4se():
    """Start an ipython session, init parser and jarvis4se(MagicJarvis), returns jarvi4se"""
    ip = get_ipython()
    parser = jarvis.command_parser.CmdParser()
    my_magic = jarvis.MagicJarvis(ip, parser)
    return my_magic


@pytest.fixture
def function_with_childs_cell():
    """Returns string see usage"""
    return "\n".join(["F1 is a function", "F1a is a function", "F1b is a function",
                      "F1c is a function", "F1d is a function", "F1e is a function",
                      "F2 is a function", "F3 is a function", "", "F1 is composed of F1a",
                      "F1 is composed of F1b", "F1 is composed of F1c", "F1 is composed of F1d",
                      "F1 is composed of F1e", "", "a is a data", "F1 produces a",
                      "F2 consumes a",
                      "", "F1a produces a", "F1b consumes a", "", "b is a data",
                      "F1c produces b", "F1d consumes b", "", "c is a data",
                      "F3 produces c", "F1e consumes c", ""])


@pytest.fixture
def fun_elem_exposing_cell():
    """Returns string see usage"""
    return "\n".join(["Fun_inter is a functional interface", "Fun_elem is a functional element",
                      "Fun_elem_2 is a functional element", "Fun_elem_3 is a functional element",
                      "Fun_elem_4 is a functional element", "Fun_elem_5 is a functional element",
                      "Fun_elem_6 is a functional element", "Fun_elem_ext is a functional element",
                      "Fun_elem_ext_2 is a functional element",
                      "Fun_elem is composed of Fun_elem_2",
                      "Fun_elem_2 is composed of Fun_elem_3",
                      "Fun_elem_3 is composed of Fun_elem_4",
                      "Fun_elem_4 is composed of Fun_elem_5",
                      "Fun_elem_5 is composed of Fun_elem_6", "Fun_elem exposes Fun_inter",
                      "Fun_elem_6 exposes Fun_inter", "Fun_elem_ext exposes Fun_inter",
                      "Fun_elem_ext_2 exposes Fun_inter", "toto exposes Fun_inter",
                      "tata exposes titi", "Fun_elem exposes coco", ""])


@pytest.fixture
def allocation_item_cell():
    """Returns string see usage"""
    first_part = "\n".join(["F1 is a function",
                            "F2 with a long name is a function. The alias of F2 with a "
                            "long name is F2",
                            "F3 is a function", "F4 is a function", "a is a data",
                            "Fun_elem is a functional element", ""])
    second_part = "\n".join(["under test_chain", "consider F1. consider toto. consider a, Fun_elem",
                             "consider tata.", "consider F1, F2, F3, F4", ""])
    return first_part, second_part


@pytest.fixture
def function_grandkids_cell():
    """Returns string see usage"""
    return "\n".join(["F1 is a function", "F1a is a function", "F1a1 is a function",
                      "F1 is composed of F1a", "F1a is composed of F1a1", "a is a data",
                      "F1a produces a", "b is a data", "F1a consumes b", "c is a data",
                      "F1a1 produces c", "d is a data", "F1a1 consumes d", ""])


@pytest.fixture
def attribute_cell():
    """Returns string see usage"""
    first_part = "\n".join(["F1 is a function",
                            "Fun elem is a functional element", ""])
    second_part = "\n".join(["A is an attribute", "B is an attribute. C is an attribute", ""])
    third_part = "\n".join(["The A of F1 is 4,2", "The C of F1 is pink",
                            "The B of Fun elem is 8,5.", "The A of Fun elem is 100", ""])
    return first_part, second_part, third_part


@pytest.fixture
def extends_cell():
    """Returns string see usage"""
    first_part = "\n".join(["Safety interface extends functional interface",
                            "The alias of Safety interface is sf", ""])
    second_part = "\n".join(["sf_a extends sf", "sf_a_b extends sf_a",
                            "final one extends sf_a_b", "Fun_inter is a functional interface",
                             "The type of Fun_inter is final one", ""])
    return first_part, second_part


def remove_xml_file(file_name):
    """Remove xml file"""
    fname = os.path.join("./", f"{file_name}.xml")
    path = Path(fname)
    if path:
        os.remove(path)
