"""@defgroup test_context_diagrams
Tests about context diagrams
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_simple_function_context(mocker):
    """@ingroup test_context_diagrams
    @anchor test_context_diagram_1
    Test context diagram display with a single function without input / output

    @param[in] mocker : mocker fixture reference
    @return none

    **Jarvis4se equivalent:**\n
    with simple_function_context\n
    F1 is a function\n
    show context F1
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "simple_function_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = 'object "F1" as f1 <<Function>>\n'

    test_lib.remove_xml_file(file_name)

    assert expected in result
    assert len(result) - len(expected) == len("\'id: xxxxxxxxxx\n")


def test_simple_function_context_in_out(mocker):
    """@ingroup test_context_diagrams
    @anchor test_context_diagram_2
    Test context diagram display with a single function with one input and one output

    @param[in] mocker : mocker fixture reference
    @return none

    **Jarvis4se equivalent:**\n
    with simple_function_in_out\n
    F1 is a function\n
    a is a data\n
    b is a data\n
    =============================\n
    with simple_function_in_out\n
    F1 produces b\n
    =============================\n
    with simple_function_in_out\n
    F1 consumes a\n
    =============================\n
    with simple_function_in_out\n
    show context F1\n
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "simple_function_in_out"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "a is a data\n"
                         "b is a data\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 produces b\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 consumes a\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = 'object "F1" as f1 <<Function>>\n' \
               'circle f1_i\n' \
               'circle f1_o\n' \
               'f1_i --> f1 : a\n' \
               'f1 --> f1_o  : b\n'

    test_lib.remove_xml_file(file_name)

    assert expected in result
    assert len(result) - len(expected) == len("\'id: xxxxxxxxxx\n")


def test_function_context_with_attribute(mocker):
    """@ingroup test_context_diagrams
    @anchor test_context_diagram_3
    Test context diagram display with a single function with attributes and their value

    @param[in] mocker : mocker fixture reference
    @return none

    **Jarvis4se equivalent:**\n
    with test_function_with_attribute\n
    F1 is a function\n
    ========================================\n
    with test_function_with_attribute\n
    A is an attribute\n
    C is an attribute\n
    ========================================\n
    with test_function_with_attribute\n
    The A of F1 is 4,2\n
    The C of F1 is pink\n
    ========================================\n
    with test_function_with_attribute\n
    show context F1\n
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_with_attribute"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "A is an attribute\n"
                         "C is an attribute\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "The A of F1 is 4,2\n"
                         "The C of F1 is pink\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F1" as f1 <<Function>> {\n', 'A = 4,2\n', 'C = pink\n', '}\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")


def test_fun_elem_context_with_attribute(mocker):
    """@ingroup test_context_diagrams
    @anchor test_context_diagram_4
    Test context diagram display with a single function with attributes and their value, allocated to a functional
    element with same attributes and different values

    @param[in] mocker : mocker fixture reference
    @return none

    **Jarvis4se equivalent:**\n
    with fun_elem_context_with_attribute\n
    F1 is a function\n
    Fun elem is a functional element\n
    F1 is allocated to Fun elem\n
    ========================================\n
    with fun_elem_context_with_attribute\n
    A is an attribute\n
    B is an attribute. C is an attribute\n
    ========================================\n
    with fun_elem_context_with_attribute\n
    The A of F1 is 4,2\n
    The C of F1 is pink\n
    The B of Fun elem is 8,5.\n
    The A of Fun elem is 100\n
    show context Fun elem\n
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "fun_elem_context_with_attribute"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "F1 is a function\n"
                         "Fun elem is a functional element\n"
                         "F1 is allocated to Fun elem")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "A is an attribute\n"
                         "B is an attribute. C is an attribute\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "The A of F1 is 4,2\n"
                         "The C of F1 is pink\n"
                         "The B of Fun elem is 8,5.\n"
                         "The A of Fun elem is 100\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "show context Fun elem\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "Fun elem" as fun_elem <<Functional element>>{\n',
                'object "F1" as f1 <<Function>> {\n',
                'A = 4,2\n',
                'C = pink\n',
                '}\n}\n',
                'note bottom of fun_elem\n',
                'A = 100\n',
                'B = 8,5\n',
                'end note\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2 * len("\'id: xxxxxxxxxx\n")


def test_fun_elem_context_with_interfaces(mocker, input_test_fun_elem_context_with_interfaces):
    """@ingroup test_context_diagrams
    @anchor test_context_diagram_5
    Test context diagram display with functional elements, their allocated functions and their interfaces

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_fun_elem_context_with_interfaces : input fixture reference
    @return none

    **Jarvis4se equivalent:**\n
    %%jarvis
    with fun_elem_context_with_interfaces\n
    F1 is a function\n
    F2 is a function\n
    A is a data\n
    B is a data\n
    C is a data\n
    F1 produces A\n
    F2 consumes A\n
    F2 produces B\n
    F1 consumes B\n
    F1 produces C\n
    Fun_elem_1 is a functional element\n
    Fun_elem_2 is a functional element\n
    Fun_inter_1 is a functional interface\n
    Fun_inter_2 is a functional interface\n
    Fun_elem_1 allocates F1\n
    Fun_elem_2 allocates F2\n
    Fun_inter_1 allocates A\n
    Fun_inter_2 allocates C\n
    Fun_elem_1 exposes Fun_inter_1\n
    Fun_elem_1 exposes Fun_inter_2\n
    Fun_elem_2 exposes Fun_inter_1\n
    show context Fun_elem_1\n
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "fun_elem_context_with_interfaces"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_context_with_interfaces}\n"
                         f"show context Fun_elem_1")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "Fun_elem_2" as fun_elem_2 <<Functional element>>{\n',
                'object "F2" as f2 <<Function>>\n',
                '}\n',
                'component "Fun_elem_1" as fun_elem_1 <<Functional element>>{\n',
                'object "F1" as f1 <<Function>>\n',
                '}\n',
                'circle f1_o\n',
                'f1 --> f1_o  : C\n'
                'f2 #--> f1 : B\n',
                'fun_elem_1', ' -- ', 'fun_elem_2 ', ': fun_inter_1\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 4 * len("\'id: xxxxxxxxxx\n")
