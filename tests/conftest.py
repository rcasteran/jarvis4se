""" @package tests
Module for non regression testing using Pytest

Defines the regression tests based on pytest fixtures
(https://docs.pytest.org/en/stable/reference/fixtures.html).

Uses the mocker fixture for spying methods (https://pytest-mock.readthedocs.io/en/latest/usage.html#).

Defines the following non regression tests:
- @ref test_plantuml_chain : Tests about chain diagrams
- @ref test_plantuml_context : Tests about context diagrams
- @ref test_plantuml_decomposition : Tests about decomposition diagrams
- @ref test_plantuml_sequence : Tests about sequence diagrams
- @ref test_plantuml_state : Tests about state diagrams
- @ref test_input_cell : Tests about Jarvis outputs
- @ref test_magic_tools : Tests about Jarvis IPython magic tools
- @ref test_question_answer : Tests about Jarvis answer to user's question
- @ref test_xml_file : Tests about xml file generation
"""

# Libraries
import pytest


@pytest.fixture
def input_test_issue_5():
    """@ingroup test_issue_5
    @anchor input_test_issue_5
    Defines input fixture for @ref test_issue_5_plantuml_decomposition

    @return input fixture

    **Jarvis4se equivalent:**

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
    """
    return "\n".join(["F1 is a function",
                      "F1a is a function",
                      "F1b is a function",
                      "F1c is a function",
                      "F1d is a function",
                      "F1e is a function",
                      "F2 is a function",
                      "F3 is a function",
                      "",
                      "F1 is composed of F1a",
                      "F1 is composed of F1b",
                      "F1 is composed of F1c",
                      "F1 is composed of F1d",
                      "F1 is composed of F1e",
                      "",
                      "a is a data",
                      "F1 produces a",
                      "F2 consumes a",
                      "",
                      "F1a produces a",
                      "F1b consumes a",
                      "",
                      "b is a data",
                      "F1c produces b",
                      "F1d consumes b",
                      "",
                      "c is a data",
                      "F3 produces c",
                      "F1e consumes c",
                      ""])


@pytest.fixture
def input_test_fun_elem_exposes_interface():
    """@ingroup test_input_cell
    @anchor input_test_fun_elem_exposes_interface
    Defines input fixture for @ref test_fun_elem_exposes_interface_in and @ref test_fun_elem_exposes_interface_xml

    @return input fixture

    **Jarvis4se equivalent:**

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
    return "\n".join(["Fun_inter is a functional interface",
                      "Fun_elem is a functional element",
                      "Fun_elem_2 is a functional element",
                      "Fun_elem_3 is a functional element",
                      "Fun_elem_4 is a functional element",
                      "Fun_elem_5 is a functional element",
                      "Fun_elem_6 is a functional element",
                      "Fun_elem_ext is a functional element",
                      "Fun_elem_ext_2 is a functional element",
                      "Fun_elem is composed of Fun_elem_2",
                      "Fun_elem_2 is composed of Fun_elem_3",
                      "Fun_elem_3 is composed of Fun_elem_4",
                      "Fun_elem_4 is composed of Fun_elem_5",
                      "Fun_elem_5 is composed of Fun_elem_6",
                      "Fun_elem exposes Fun_inter",
                      "Fun_elem_6 exposes Fun_inter",
                      "Fun_elem_ext exposes Fun_inter",
                      "Fun_elem_ext_2 exposes Fun_inter",
                      "toto exposes Fun_inter",
                      "tata exposes titi",
                      "Fun_elem exposes coco",
                      ""])


@pytest.fixture
def input_test_issue_31():
    """@ingroup test_issue_31
    @anchor input_test_issue_31
    Defines input fixture for @ref test_issue_31_plantuml_context and @ref test_issue_31_xml

    @return input fixture

    **Jarvis4se equivalent:**

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
    """
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
def input_test_fun_elem_with_interfaces():
    """@ingroup test_plantuml_context
    @anchor input_test_fun_elem_with_interfaces
    Defines input fixture for @ref test_fun_elem_with_interfaces_plantuml_context

    @return input fixture

    **Jarvis4se equivalent:**

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
    """
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
    """@ingroup test_issue_39
    @anchor input_test_issue_39
    Defines input fixture for @ref test_issue_39_plantuml_context

    @return input fixture

    **Jarvis4se equivalent:**

        E is a functional element
        E1 is a functional element
        I_E_E1 is a functional interface
        E exposes I_E_E1
        E1 exposes I_E_E1
    """
    return "\n".join(["E is a functional element",
                      "E1 is a functional element",
                      "I_E_E1 is a functional interface",
                      "E exposes I_E_E1",
                      "E1 exposes I_E_E1",
                      ""])


@pytest.fixture
def input_test_issue_38():
    """@ingroup test_issue_38
    @anchor input_test_issue_38
    Defines input fixture for @ref test_issue_38_plantuml_context

    @return input fixture

    **Jarvis4se equivalent:**

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
    """
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
    """@ingroup test_issue_44
    @anchor input_test_issue_44
    Defines input fixture for @ref test_issue_44_plantuml_context

    @return input fixture

    **Jarvis4se equivalent:**

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
    """
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
def input_test_issue_56():
    """@ingroup test_issue_56
    @anchor input_test_issue_56
    Defines input fixture for @ref test_issue_56_in and @ref test_issue_56_xml

    @return input fixture

    **Jarvis4se equivalent:**

        Safety interface extends functional interface
        The alias of Safety interface is sf
        ========================================
        sf_a extends sf
        sf_a_b extends sf_a
        final one extends sf_a_b
        Fun_inter is a functional interface
        The type of Fun_inter is final one
    """
    first_part = "\n".join(["Safety interface extends functional interface",
                            "The alias of Safety interface is sf",
                            ""])

    second_part = "\n".join(["sf_a extends sf",
                             "sf_a_b extends sf_a",
                             "final one extends sf_a_b",
                             "Fun_inter is a functional interface",
                             "The type of Fun_inter is final one",
                             ""])

    return first_part, second_part


@pytest.fixture
def input_test_issue_62():
    """@ingroup test_issue_62
    @anchor input_test_issue_62
    Defines input fixture for @ref test_issue_62_in and @ref test_issue_62_xml

    @return input fixture

    **Jarvis4se equivalent:**

        "High level function" extends function
        "High high level function" extends "High level function"
        "High high high level function" extends "High high level function"
        3High is a "High high high level function"
    """
    return "\n".join(['"High level function" extends function',
                      '"High high level function" extends "High level function"',
                      '"High high high level function" extends "High high level function"',
                      '3High is a "High high high level function"',
                      ""])


@pytest.fixture
def input_test_issue_81():
    """@ingroup test_issue_81
    @anchor input_test_issue_81
    Defines input fixture for @ref test_issue_81_plantuml_decomposition

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F2 is a function
        a is a data
        F1 produces a
        F2 consumes a
        F21 is a function
        F22 is a function
        F21 composes F2
        F22 composes F2
        F211 is a function
        F212 is a function
        F211 composes F21
        F212 composes F21
        F211 consumes a
        F212 produces b
        c is a data
        F211 produces c
        F212 consumes c
        F21 consumes a
        b is a data
        F21 produces b
        F22 consumes b
    """
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


@pytest.fixture
def input_test_issue_7():
    """@ingroup test_issue_7
    @anchor input_test_issue_7
    Defines input fixture for @ref test_issue_7_plantuml_decomposition

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F1a is a function
        F1b is a function
        F1c is a function
        F1 is composed of F1a
        F1 is composed of F1b
        F1 is composed of F1c

        F1c1 is a function
        F1c is composed of F1c1

        F2 is a function
        F2a is a function
        F2 is composed of F2a

        F3 is a function
        F3a is a function
        F3 is composed of F3a

        E1 is a functional element
        E1a is a functional element
        E1b is a functional element
        E1c is a functional element
        E1 is composed of E1a
        E1 is composed of E1b
        E1 is composed of E1c
        E1c1 is a functional element
        E1c2 is a functional element
        E1c is composed of E1c1
        E1c is composed of E1c2

        E1 allocates F1
        E1 allocates F2
        E1a allocates F1a
        E1a allocates F3a
        E1b allocates F1b
        E1c allocates F1c
        E1c1 allocates F1c1
    """
    return "\n".join(["F1 is a function",
                      "F1a is a function",
                      "F1b is a function",
                      "F1c is a function",
                      "F1 is composed of F1a",
                      "F1 is composed of F1b",
                      "F1 is composed of F1c",
                      "",
                      "F1c1 is a function",
                      "F1c is composed of F1c1",
                      "",
                      "F2 is a function",
                      "F2a is a function",
                      "F2 is composed of F2a",
                      "",
                      "F3 is a function",
                      "F3a is a function",
                      "F3 is composed of F3a",
                      "",
                      "E1 is a functional element",
                      "E1a is a functional element",
                      "E1b is a functional element",
                      "E1c is a functional element",
                      "E1 is composed of E1a",
                      "E1 is composed of E1b",
                      "E1 is composed of E1c",
                      "E1c1 is a functional element",
                      "E1c2 is a functional element",
                      "E1c is composed of E1c1",
                      "E1c is composed of E1c2",
                      "",
                      "E1 allocates F1",
                      "E1 allocates F2",
                      "E1a allocates F1a",
                      "E1a allocates F3a",
                      "E1b allocates F1b",
                      "E1c allocates F1c",
                      "E1c1 allocates F1c1",
                      ""])


@pytest.fixture
def input_test_issue_13():
    """@ingroup test_issue_13
    @anchor input_test_issue_13
    Defines input fixture for @ref test_issue_13_plantuml_decomposition

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F2 is a function
        F1 is composed of F2
        E1 is a functional element
        E1 allocates F1
    """
    return "\n".join(["F1 is a function",
                      "F2 is a function",
                      "F1 is composed of F2",
                      "E1 is a functional element",
                      "E1 allocates F1",
                      ""])


@pytest.fixture
def input_test_fun_elem_with_interfaces_2():
    """@ingroup test_plantuml_decomposition
    @anchor input_test_fun_elem_with_interfaces_2
    Defines input fixture for @ref test_fun_elem_with_interfaces_plantuml_decomposition

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F1b is a function
        F1c is a function
        F1 is composed of F1b
        F1 is composed of F1c

        F1c1 is a function
        F1c is composed of F1c1

        F_ext is a function

        E1 is a functional element
        E1b is a functional element
        E1c is a functional element
        Ext is a functional element
        E1 is composed of E1c
        E1 is composed of E1b
        E1c1 is a functional element
        E1c is composed of E1c1

        E1 allocates F1
        E1b allocates F1b
        E1c allocates F1c
        E1c1 allocates F1c1
        Ext allocates F_ext

        A is a data
        A_2 is a data
        B is a data
        C is a data

        Fun_inter_A is a functional interface
        Fun_inter_A allocates A
        Fun_inter_A allocates A_2
        Fun_inter_B is a functional interface
        Fun_inter_B allocates B

        F1c1 produces A
        F1c1 produces A_2
        F1b consumes A
        F1b consumes A_2

        F_ext produces B
        F1c1 consumes B

        F1b produces C
        F_ext consumes C

        E1c exposes Fun_inter_A
        E1c1 exposes Fun_inter_A
        E1b exposes Fun_inter_A
    """
    return "\n".join(["F1 is a function",
                      "F1b is a function",
                      "F1c is a function",
                      "F1 is composed of F1b",
                      "F1 is composed of F1c",
                      "",
                      "F1c1 is a function",
                      "F1c is composed of F1c1",
                      "",
                      "F_ext is a function",
                      "",
                      "E1 is a functional element",
                      "E1b is a functional element",
                      "E1c is a functional element",
                      "Ext is a functional element",
                      "E1 is composed of E1b",
                      "E1 is composed of E1c",
                      "E1c1 is a functional element",
                      "E1c is composed of E1c1",
                      "",
                      "E1 allocates F1",
                      "E1b allocates F1b",
                      "E1c allocates F1c",
                      "E1c1 allocates F1c1",
                      "Ext allocates F_ext",
                      "",
                      "A is a data",
                      "A_2 is a data",
                      "B is a data",
                      "C is a data",
                      "",
                      "Fun_inter_A is a functional interface",
                      "Fun_inter_A allocates A",
                      "Fun_inter_A allocates A_2",
                      "Fun_inter_B is a functional interface",
                      "Fun_inter_B allocates B",
                      "",
                      "F1c1 produces A",
                      "F1c1 produces A_2",
                      "F1b consumes A",
                      "F1b consumes A_2",
                      "",
                      "F_ext produces B",
                      "F1c1 consumes B",
                      "",
                      "F1b produces C",
                      "F_ext consumes C",
                      "",
                      "E1c exposes Fun_inter_A",
                      "E1c1 exposes Fun_inter_A",
                      "E1b exposes Fun_inter_A",
                      ""])


@pytest.fixture
def input_test_fun_elem_with_attribute():
    """@ingroup test_plantuml_context
    @anchor input_test_fun_elem_with_attribute
    Defines input fixture for:
    - @ref test_fun_elem_with_attribute_plantuml_context
    - @ref test_attribute_declaration_in
    - @ref test_instantiated_attribute_in
    - @ref test_instantiated_attribute_xml

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        Fun elem is a functional element
        F1 is allocated to Fun elem
        ========================================
        with fun_elem_context_with_attribute
        A is an attribute
        B is an attribute. C is an attribute
        ========================================
        with fun_elem_context_with_attribute
        The A of F1 is 4,2
        The C of F1 is pink
        The B of Fun elem is 8,5.
        The A of Fun elem is 100
        show context Fun elem
    """
    first_part = "\n".join(["F1 is a function",
                            "Fun elem is a functional element",
                            "F1 is allocated to Fun elem",
                            ""])
    second_part = "\n".join(["A is an attribute",
                             "B is an attribute. C is an attribute",
                             ""])
    third_part = "\n".join(["The A of F1 is 4,2",
                            "The C of F1 is pink",
                            "The B of Fun elem is 8,5.",
                            "The A of Fun elem is 100",
                            ""])

    return first_part, second_part, third_part


@pytest.fixture
def input_test_issue_21():
    """@ingroup test_issue_21
    @anchor input_test_issue_21
    Defines input fixture for @ref test_issue_21_in

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function.
        high level function extends function. The alias of F1 is f1.
        The type of f1 is high level function
    """
    return "\n".join(["F1 is a function.",
                      "high level function extends function. The alias of F1 is f1.",
                      "The type of f1 is high level function",
                      ""])


@pytest.fixture
def input_test_issue_9():
    """@ingroup test_issue_9
    @anchor input_test_issue_9
    Defines input fixture for @ref test_issue_9_in and @ref test_issue_9_xml

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F2 with a long name is a function. The alias of F2 with a long name is F2
        F3 is a function
        F4 is a function
        a is a data
        Fun_elem is a functional element
        ========================================
        under test_view
        consider F1. consider toto. consider a, Fun_elem
        consider tata.
        consider F1, F2, F3, F4
    """
    first_part = "\n".join(["F1 is a function",
                            "F2 with a long name is a function. The alias of F2 with a "
                            "long name is F2",
                            "F3 is a function",
                            "F4 is a function",
                            "a is a data",
                            "Fun_elem is a functional element",
                            ""])

    second_part = "\n".join(["under test_view",
                             "consider F1. consider toto. consider a, Fun_elem",
                             "consider tata.",
                             "consider F1, F2, F3, F4",
                             ""])

    return first_part, second_part


@pytest.fixture
def input_test_functional_interface():
    """@ingroup test_input_cell
    @anchor input_test_functional_interface
    Defines input fixture for @ref test_functional_interface_in

    @return input fixture

    **Jarvis4se equivalent:**

        Color is an attribute
        A is a data
        Fun_inter is a functional interface.
        The alias of Fun_inter is FI
        The Color of Fun_inter is pink
        Fun_inter allocates A.
    """
    return "\n".join(["Color is an attribute",
                      "A is a data",
                      "Fun_inter is a functional interface.",
                      "The alias of Fun_inter is FI",
                      "The Color of Fun_inter is pink",
                      "Fun_inter allocates A."])


@pytest.fixture
def input_test_issue_55():
    """@ingroup test_issue_55
    @anchor input_test_issue_55
    Defines input fixture for @ref test_issue_55

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F2 is a function
        F3 is a function

        a is a data
        F1 produces a
        F2 consumes a
        F3 consumes a

        E1 is a functional element
        E1 allocates F1

        E2 is a functional element
        E2 allocates F2

        E3 is a functional element
        E3 allocates F3

        I_E1_E2 is a functional interface
        I_E1_E2 allocates a
        E1 exposes I_E1_E2
        E2 exposes I_E1_E2
    """
    return "\n".join(["F1 is a function",
                      "F2 is a function",
                      "F3 is a function",
                      "",
                      "a is a data",
                      "F1 produces a",
                      "F2 consumes a",
                      "F3 consumes a",
                      "",
                      "E1 is a functional element",
                      "E1 allocates F1",
                      "",
                      "E2 is a functional element",
                      "E2 allocates F2",
                      "",
                      "E3 is a functional element",
                      "E3 allocates F3",
                      "",
                      "I_E1_E2 is a functional interface",
                      "I_E1_E2 allocates a",
                      "E1 exposes I_E1_E2",
                      "E2 exposes I_E1_E2",
                      ""])


@pytest.fixture
def input_test_fun_elem_with_interfaces_3():
    """@ingroup test_plantuml_sequence
    @anchor input_test_fun_elem_with_interfaces_3
    Defines input fixture for @ref test_fun_elem_with_interfaces_plantuml_sequence

    @return input fixture

    **Jarvis4se equivalent:**

        Fun_inter is a functional interface
        Fun_elem_1 is a functional element
        Fun_elem_2 is a functional element
        A is a data
        B is a data
        C is a data
        F1 is a function
        F2 is a function
        F1 produces A
        F1 produces C
        F2 consumes C
        F2 produces B
        F1 consumes B
        F2 consumes A
        C implies B
        B implies A
        Fun_elem_1 allocates F1
        Fun_elem_2 allocates F2
        Fun_elem_1 exposes Fun_inter
        Fun_elem_2 exposes Fun_inter
        Fun_inter allocates A
        Fun_inter allocates B
        Fun_inter allocates C
    """
    return "\n".join(["Fun_inter is a functional interface",
                      "Fun_elem_1 is a functional element",
                      "Fun_elem_2 is a functional element",
                      "A is a data",
                      "B is a data",
                      "C is a data",
                      "F1 is a function",
                      "F2 is a function",
                      "F1 produces A",
                      "F1 produces C",
                      "F2 consumes C",
                      "F2 produces B",
                      "F1 consumes B",
                      "F2 consumes A",
                      "C implies B",
                      "B implies A",
                      "Fun_elem_1 allocates F1",
                      "Fun_elem_2 allocates F2",
                      "Fun_elem_1 exposes Fun_inter",
                      "Fun_elem_2 exposes Fun_inter",
                      "Fun_inter allocates A",
                      "Fun_inter allocates B",
                      "Fun_inter allocates C",
                      ""])


@pytest.fixture
def input_test_entry_exit():
    """@ingroup test_plantuml_state
    @anchor input_test_entry_exit
    Defines input fixture for @ref test_entry_exit_plantuml_state

    @return input fixture

    **Jarvis4se equivalent:**

        EXIT_TOTO extends state
        ENTRY state extends state
        S1 is a EXIT_TOTO
        S2 is a ENTRY state
    """
    return "\n".join(["EXIT_TOTO extends state",
                      "ENTRY state extends state",
                      "S1 is a EXIT_TOTO",
                      "S2 is a ENTRY state"])


@pytest.fixture
def input_test_simple_function():
    """@ingroup test_plantuml_context
    @anchor input_test_simple_function
    Defines input fixture for:
    - @ref test_simple_function_plantuml_context
    - @ref test_simple_function_xml
    - @ref test_simple_function_handler_question

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
    """
    return "\n".join(["F1 is a function",
                      ""])


@pytest.fixture
def input_test_extended_attribute():
    """@ingroup test_xml_file
    @anchor input_test_extended_attribute
    Defines input fixture for @ref test_extended_attribute_xml

    @return input fixture

    **Jarvis4se equivalent:**

         A is an attribute
         B is an attribute.
         attribute type A extends attribute.
         attribute type B extends attribute
         The type of A is attribute type A.
         The type of B is attribute type B
    """
    return "\n".join(["A is an attribute",
                      "B is an attribute.",
                      "attribute type A extends attribute.",
                      "attribute type B extends attribute",
                      "The type of A is attribute type A.",
                      "The type of B is attribute type B"])


@pytest.fixture
def input_test_functional_interface_with_attribute():
    """@ingroup test_xml_file
    @anchor input_test_functional_interface_with_attribute
    Defines input fixture for @ref test_functional_interface_with_attribute_xml

    @return input fixture

    **Jarvis4se equivalent:**

        Color is an attribute
        A is a data
        F1 is a function
        F2 is a function
        Fun_elem_1 is a functional element
        Fun_elem_2 is a functional element
        F1 produces A
        F2 consumes A
        Fun_elem_1 allocates F1
        Fun_elem_2 allocates F2
        Fun_inter is a functional interface.
        The alias of Fun_inter is FI
        The Color of Fun_inter is pink
        Fun_elem_1 exposes Fun_inter
        Fun_elem_2 exposes Fun_inter
        Fun_inter allocates A.
    """
    return "\n".join(["Color is an attribute",
                      "A is a data",
                      "F1 is a function",
                      "F2 is a function",
                      "Fun_elem_1 is a functional element",
                      "Fun_elem_2 is a functional element",
                      "F1 produces A",
                      "F2 consumes A",
                      "Fun_elem_1 allocates F1",
                      "Fun_elem_2 allocates F2",
                      "Fun_inter is a functional interface.",
                      "The alias of Fun_inter is FI",
                      "The Color of Fun_inter is pink",
                      "Fun_elem_1 exposes Fun_inter",
                      "Fun_elem_2 exposes Fun_inter",
                      "Fun_inter allocates A."])


@pytest.fixture
def input_test_function_output_auto_decomposition():
    """@ingroup test_plantuml_decomposition
    @anchor input_test_function_output_auto_decomposition
    Defines input fixture for :
    - @ref test_function_output_auto_external_plantuml_decomposition
    - @ref test_function_output_auto_splitted_plantuml_decomposition
    - @ref test_function_output_auto_xml
    - @ref test_function_output_auto_splitted_xml
    - @ref test_function_output_auto_external_xml
    - @ref test_function_output_auto_splitted_in
    - @ref test_function_output_auto_in
    - @ref test_function_output_auto_external_in
    - @ref test_function_output_auto_handler_question

    @return input fixture

    **Jarvis4se equivalent:**

        F is a function
        a is a data
        F produces a
        F1 is a function
        F1 composes F
        F1 produces a
        ================
        F2 is a function
        F2 composes F
        F2 consumes a
        ================
        FE is a function
        FE consumes a
    """
    first_part = "\n".join(["F is a function",
                            "a is a data",
                            "F produces a",
                            "F1 is a function",
                            "F1 composes F",
                            "F1 produces a"])

    second_part = "\n".join(["F2 is a function",
                             "F2 composes F",
                             "F2 consumes a"])

    third_part = "\n".join(["FE is a function",
                            "FE consumes a"])

    return first_part, second_part, third_part


@pytest.fixture
def input_test_issue_75():
    """@ingroup test_issue_75
    @anchor input_test_issue_75
    Defines input fixture for @ref test_issue_75

    @return input fixture

    **Jarvis4se equivalent:**

        F is a function
        F1 is a function
        F2 is a function
        F3 is a function
        a is a data
        F2 produces a
        F3 consumes a
        F is composed of F1
        F1 is composed of F2
        F1 is composed of F3
    """
    return "\n".join(["F is a function",
                      "F1 is a function",
                      "F2 is a function",
                      "F3 is a function",
                      "a is a data",
                      "F2 produces a",
                      "F3 consumes a",
                      "F is composed of F1",
                      "F1 is composed of F2",
                      "F1 is composed of F3"])


@pytest.fixture
def input_test_function_plantuml_chain():
    """@ingroup test_plantuml_chain
    @anchor input_test_function_plantuml_chain
    Defines input fixture for:
    - @ref test_function_plantuml_chain
    - @ref test_function_with_context_plantuml_chain
    - @ref test_function_child_with_context_plantuml_chain
    - @ref test_function_child_child_with_context_plantuml_chain

    @return input fixture

    **Jarvis4se equivalent:**

        FE1 is a function
        FE2 is a function
        F1 is a function
        F2 is a function
        F3 is a function
        F4 is a function
        F5 is a function
        F4, F5 composes F3
        F2, F3 composes F1
        a is a data
        FE1 produces a
        F2 consumes a
        b is a data
        F2 produces b
        F4 consumes b
        c is a data
        F4 produces c
        F5 consumes c
        d is a data
        F5 produces d
        FE2 consumes d
    """
    return "\n".join(["FE1 is a function",
                      "FE2 is a function",
                      "F1 is a function",
                      "F2 is a function",
                      "F3 is a function",
                      "F4 is a function",
                      "F5 is a function",
                      "F4, F5 composes F3",
                      "F2, F3 composes F1",
                      "a is a data",
                      "FE1 produces a",
                      "F2 consumes a",
                      "b is a data",
                      "F2 produces b",
                      "F4 consumes b",
                      "c is a data",
                      "F4 produces c",
                      "F5 consumes c",
                      "d is a data",
                      "F5 produces d",
                      "FE2 consumes d"])

@pytest.fixture
def input_test_issue_82():
    """@ingroup test_plantuml_chain
    @anchor input_test_issue_82
    Defines input fixture for @ref test_issue_82_plantuml_chain

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F12 is a function
        F12 composes F1
        F13 is a function
        F13 composes F1
        F14 is a function
        F14 composes F1
        F141 is a function
        F141 composes F14
        F142 is a function
        F142 composes F14
        a is a data
        F1 consumes a
        F12 consumes a
        b is a data
        F12 produces b
        F13 consumes b
        c is a data
        F13 produces c
        F14 consumes c
        F141 consumes c
        d is a data
        F141 produces d
        F142 consumes d
        e is a data
        F142 produces e
        F14 produces e
        F1 produces e
    """
    return "\n".join(["F1 is a function",
                      "F12 is a function",
                      "F12 composes F1",
                      "F13 is a function",
                      "F13 composes F1",
                      "F14 is a function",
                      "F14 composes F1",
                      "F141 is a function",
                      "F141 composes F14",
                      "F142 is a function",
                      "F142 composes F14",
                      "a is a data",
                      "F1 consumes a",
                      "F12 consumes a",
                      "b is a data",
                      "F12 produces b",
                      "F13 consumes b",
                      "c is a data",
                      "F13 produces c",
                      "F14 consumes c",
                      "F141 consumes c",
                      "d is a data",
                      "F141 produces d",
                      "F142 consumes d",
                      "e is a data",
                      "F142 produces e",
                      "F14 produces e",
                      "F1 produces e"])


@pytest.fixture
def input_test_issue_86():
    """@ingroup test_issue_86
    @anchor input_test_issue_86
    Defines input fixture for @ref test_issue_86_plantuml_decomposition

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        F11 is a function
        F12 is a function
        F11, F12 compose F1
        a is a data
        F1 consumes a
        F11 consumes a
        F12 consumes a
        b is a data
        F1 produces b
        F11 produces b
        F12 produces b
    """
    return "\n".join(["F1 is a function",
                      "F11 is a function",
                      "F12 is a function",
                      "F11, F12 compose F1",
                      "a is a data",
                      "F1 consumes a",
                      "F11 consumes a",
                      "F12 consumes a",
                      "b is a data",
                      "F1 produces b",
                      "F11 produces b",
                      "F12 produces b",
                      ""])

@pytest.fixture
def input_single_requirement():
    """@ingroup test_requirement
    @anchor input_single_requirement
    Defines input fixture for:
    - @ref test_simple_requirement_function
    - @ref test_simple_function_allocation_requirement_function
    - @ref test_simple_function_allocation_manual_requirement_function

    @return input fixture

    **Jarvis4se equivalent:**
        F1 is a function

        The function F1 shall compute the ambient temperature value based on the acquired temperature value as specified
        in the following formula: AMBIENT_TEMPERATURE_VALUE = ACQUIRED_TEMPERATURE_VALUE * 56 / 100

        F1 satisfies F1 behavior
    """
    first_req = "\n".join(["F1 is a function"])

    second_req = "\n".join(["The function F1 shall compute the ambient temperature value based on the acquired "
                            "temperature value as specified in the following formula: "
                            "AMBIENT_TEMPERATURE_VALUE = ACQUIRED_TEMPERATURE_VALUE * 56 / 100"])

    third_req = "\n".join(["F1 satisfies F1 behavior"])

    return first_req, second_req, third_req


def input_requirement_decomposition():
    """@ingroup test_requirement
    @anchor input_single_requirement
    Defines input fixture for test_function_decomposition_requirement_allocation

    @return input fixture

    **Jarvis4se equivalent:**
        F1 is a function
        F11 is a function
        F12 is a function

        F11, F12 compose F1

        The function F1 shall store permanently the vehicle mileage received from the CAN message MSG_VEHICLE_DATA
        The function F11 shall store in a non-volatile memory the received vehicle mileage RECEIVED_VEHICLE_MILEAGE
        The function F12 shall compute the received vehicle mileage RECEIVED_VEHICLE_MILEAGE based on the CAN message
        MSG_VEHICLE_DATA as specified in the following formula : RECEIVED_VEHICLE_MILEAGE = MSG_VEHICLE_DATA[4][0]

        F1 satisfies F1 behavior
        F11 satisfies F11 behavior
        F12 satisfies F12 behavior
    """
    first_req = "\n".join(["F1 is a function",
                           "F11 is a function",
                           "F12 is a function",
                           "F11, F12 compose F1"])

    second_req = "\n".join(["The function F1 shall store permanently the vehicle mileage received from the CAN message "
                            "MSG_VEHICLE_DATA",
                            "The function F11 shall store in a non-volatile memory the received vehicle mileage "
                            "RECEIVED_VEHICLE_MILEAGE",
                            "The function F12 shall compute the received vehicle mileage RECEIVED_VEHICLE_MILEAGE "
                            "based on the CAN message MSG_VEHICLE_DATA as specified in the following formula:"
                            "RECEIVED_VEHICLE_MILEAGE = MSG_VEHICLE_DATA[4][0]"])

    third_req = "\n".join(["F11 behavior, F12 behavior derives from F1 behavior"])

    return first_req, second_req, third_req


@pytest.fixture
def input_test_issue_87():
    """@ingroup test_issue_87
    @anchor input_test_issue_87
    Defines input fixture for @ref test_issue_87_plantuml_context

    @return input fixture

    **Jarvis4se equivalent:**

        F1 is a function
        A is a data
        B is a data
        F1 consumes A
        F1 produces B

        F is a function
        F1 composes F
    """
    first_part = "\n".join(["F1 is a function",
                            "A is a data",
                            "B is a data",
                            "F1 consumes A",
                            "F1 produces B",
                            ""])

    second_part = "\n".join(["F is a function",
                             "F1 composes F",
                             ""])

    return first_part, second_part


@pytest.fixture
def input_test_fun_elem_simple_decomposition():
    """@ingroup test_plantuml_decomposition
    @anchor input_test_fun_elem_simple_decomposition
    Defines input fixture for @ref test_fun_elem_simple_plantuml_decomposition

    @return input fixture

    **Jarvis4se equivalent:**

        E is a functional element
        I is a functional interface
        E exposes I

        E1 is a functional element
        I1 is a functional interface
        E1 exposes I
        E1 exposes I1
        E2 is a functional element
        E2 exposes I1
        E is composed of E1, E2
    """
    first_part = "\n".join(["E is a functional element",
                            "I is a functional interface",
                            "E exposes I",
                            ""])

    second_part = "\n".join(["E1 is a functional element",
                             "I1 is a functional interface",
                             "E1 exposes I",
                             "E1 exposes I1",
                             "E2 is a functional element",
                             "E2 exposes I1",
                             "E is composed of E1, E2"])

    return first_part, second_part


@pytest.fixture
def input_test_simple_state_in_out():
    """@ingroup test_plantuml_context
    @anchor input_test_simple_state_in_out
    Defines input fixture for @ref test_simple_state_in_out_plantuml_context

    @return input fixture

    **Jarvis4se equivalent:**
        S0 is a state
        S1 is a state
        S2 is a state
        T_S0_S1 is a transition
        Condition for T_S0_S1 is: VOLTAGE > 7V
        The source of T_S0_S1 is S0
        The destination of T_S0_S1 is S1
        T_S1_S2 is a transition
        The source of T_S1_S2 is S1
        The destination of T_S1_S2 is S2
        Condition for T_S1_S2 is: BUS_COMMUNICATION_STATUS == BUS_COMMUNICATION_ON
    """
    return "\n".join(["S0 is a state",
                      "S1 is a state",
                      "S2 is a state",
                      "T_S0_S1 is a transition",
                      "Condition for T_S0_S1 is: VOLTAGE > 7V",
                      "The source of T_S0_S1 is S0",
                      "The destination of T_S0_S1 is S1",
                      "T_S1_S2 is a transition",
                      "The source of T_S1_S2 is S1",
                      "The destination of T_S1_S2 is S2",
                      "Condition for T_S1_S2 is: BUS_COMMUNICATION_STATUS == BUS_COMMUNICATION_ON",
                      ""])

