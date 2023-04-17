""" @package test
@defgroup test
Module for non regression testing

Defines the regression tests based on pytest fixtures
(https://docs.pytest.org/en/stable/reference/fixtures.html).

Uses the mocker fixture for spying methods (https://pytest-mock.readthedocs.io/en/latest/usage.html#).

Non regression tests about context diagram:
- @ref test_context_diagram_1 : context diagram of a single function

"""

# Libraries
import pytest


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
    second_part = "\n".join(["under test_view", "consider F1. consider toto. consider a, Fun_elem",
                             "consider tata.", "consider F1, F2, F3, F4", ""])
    return first_part, second_part


@pytest.fixture
def input_test_issue_31():
    """Returns string see usage"""
    return "\n".join(["F1 is a function",
                      "F1a is a function",
                      "F1a1 is a function",
                      "F1 is composed of F1a",
                      "F1a is composed of F1a1",
                      "a is a data",
                      "F1a produces a",
                      "b is a data",
                      "F1a consumes b",
                      "c is a data",
                      "F1a1 produces c",
                      "d is a data",
                      "F1a1 consumes d",
                      ""])


@pytest.fixture
def input_test_fun_elem_context_with_interfaces():
    """Returns string see usage"""
    return "\n".join(["F1 is a function",
                      "F2 is a function",
                      "A is a data",
                      "B is a data",
                      "C is a data",
                      "F1 produces A",
                      "F2 consumes A",
                      "F2 produces B",
                      "F1 consumes B",
                      "F1 produces C",
                      "Fun_elem_1 is a functional element",
                      "Fun_elem_2 is a functional element",
                      "Fun_inter_1 is a functional interface",
                      "Fun_inter_2 is a functional interface",
                      "Fun_elem_1 allocates F1",
                      "Fun_elem_2 allocates F2",
                      "Fun_inter_1 allocates A",
                      "Fun_inter_2 allocates C",
                      "Fun_elem_1 exposes Fun_inter_1",
                      "Fun_elem_1 exposes Fun_inter_2",
                      "Fun_elem_2 exposes Fun_inter_1",
                      ""])


@pytest.fixture
def input_test_issue_39():
    """Returns string see usage"""
    return "\n".join(["E is a functional element",
                      "E1 is a functional element",
                      "I_E_E1 is a functional interface",
                      "E exposes I_E_E1",
                      "E1 exposes I_E_E1",
                      ""])


@pytest.fixture
def input_test_issue_38():
    """Returns string see usage"""
    return "\n".join(["F is a function",
                      "F1 is a function",
                      "F2 is a function",
                      "a is a data",
                      "F produces a",
                      "F1 consumes a",
                      "F2 consumes a",
                      "b is a data",
                      "F produces b",
                      "F2 consumes b",
                      "",
                      "E is a functional element",
                      "E allocates F",
                      "E1 is a functional element",
                      "E1 allocates F1",
                      "E2 is a functional element",
                      "E2 allocates F2",
                      "",
                      "I_E_E1 is a functional interface",
                      "I_E_E1 allocates a",
                      "E exposes I_E_E1",
                      "E1 exposes I_E_E1",
                      ""])


@pytest.fixture
def input_test_issue_44():
    """Returns string see usage"""
    return "\n".join(["F is a function",
                      "F1 is a function",
                      "a is a data",
                      "F produces a",
                      "F1 consumes a",
                      "E is a functional element",
                      "E1 is a functional element",
                      "E allocates F",
                      "E1 allocates F1",
                      "I_E_E1 is a functional interface",
                      "E exposes I_E_E1",
                      "E1 exposes I_E_E1",
                      "I_E_E1 allocates a",
                      "",
                      "E11 is a functional element",
                      "E11 composes E",
                      "E11 allocates F",
                      "E11 exposes I_E_E1",
                      ""])


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
def extends_and_set_type_cell():
    """Returns string see usage"""
    first_part = "\n".join(["Safety interface extends functional interface",
                            "The alias of Safety interface is sf", ""])
    second_part = "\n".join(["sf_a extends sf", "sf_a_b extends sf_a",
                             "final one extends sf_a_b", "Fun_inter is a functional interface",
                             "The type of Fun_inter is final one", ""])
    return first_part, second_part


@pytest.fixture
def extends_and_create_object_cell():
    """Returns string see usage"""
    return "\n".join(['"High level function" extends function',
                      '"High high level function" extends "High level function"',
                      '"High high high level function" extends "High high level function"',
                      '3High is a "High high high level function"', ""])


@pytest.fixture
def state_exit_entry_chain_output_diagram():
    """Returns string see usage"""
    return ('skinparam useBetaStyle true\n',
            'hide empty description\n',
            '<style>\n',
            '     .Entry{\n',
            '        FontColor white\n',
            '        BackgroundColor black\n',
            '     }\n',
            '     .Exit{\n',
            '        FontColor white\n',
            '        BackgroundColor black\n',
            '     }\n',
            '</style>\n',
            'state "S1" as s1 <<EXIT>>\n',
            'state "S2" as s2 <<ENTRY>>\n')


@pytest.fixture
def input_test_fun_decomposition_level():
    return "\n".join(["F1 is a function",
                      "F2 is a function",
                      "a is a data",
                      "F1 produces a",
                      "F2 consumes a",
                      "F21 is a function",
                      "F22 is a function",
                      "F21 composes F2",
                      "F22 composes F2",
                      "F211 is a function",
                      "F212 is a function",
                      "F211 composes F21",
                      "F212 composes F21",
                      "F211 consumes a",
                      "F212 produces b",
                      "c is a data",
                      "F211 produces c",
                      "F212 consumes c",
                      "F21 consumes a",
                      "b is a data",
                      "F21 produces b",
                      "F22 consumes b",
                      ""])
