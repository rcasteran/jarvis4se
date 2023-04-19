""" @package test
Module for non regression testing

Defines the regression tests based on pytest fixtures
(https://docs.pytest.org/en/stable/reference/fixtures.html).

Uses the mocker fixture for spying methods (https://pytest-mock.readthedocs.io/en/latest/usage.html#).

Defines the following non regression tests:
- @ref test_context_diagrams : Tests about context diagrams
- @ref test_decomposition_diagrams : Tests about decomposition diagrams
- @ref test_input_cell : Tests about Jarvis outputs
- @ref test_magic_tools : Tests about Jarvis IPython magic tools
- @ref test_question_answer : Tests about Jarvis answer to user's question
"""

# Libraries
import pytest


@pytest.fixture
def input_test_issue_5():
    """@ingroup test_issue_5
    @anchor input_test_issue_5
    Defines input fixture for @ref test_issue_5_decomposition

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
    Defines input fixture for @ref test_issue_31_context

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
    """@ingroup test_context_diagrams
    @anchor input_test_fun_elem_with_interfaces
    Defines input fixture for @ref test_fun_elem_with_interfaces_context

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
    Defines input fixture for @ref test_issue_39_context

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
    Defines input fixture for @ref test_issue_38_context

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
    Defines input fixture for @ref test_issue_44_context

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
def input_test_issue_81():
    """@ingroup test_issue_81
    @anchor input_test_issue_81
    Defines input fixture for @ref test_issue_81_context

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
    Defines input fixture for @ref test_issue_7_decomposition

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
    Defines input fixture for @ref test_issue_13_decomposition

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
    """@ingroup test_decomposition_diagrams
    @anchor input_test_fun_elem_with_interfaces_2
    Defines input fixture for @ref test_fun_elem_with_interfaces_decomposition

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
    """@ingroup test_context_diagrams
    @anchor input_test_fun_elem_with_attribute
    Defines input fixture for @ref test_fun_elem_with_attribute_context, @ref test_attribute_declaration_in,
    @ref test_instantiated_attribute_in and @ref test_instantiated_attribute_xml

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
    """@ingroup test_sequence_diagrams
    @anchor input_test_fun_elem_with_interfaces_3
    Defines input fixture for @ref test_fun_elem_with_interfaces_sequence

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
