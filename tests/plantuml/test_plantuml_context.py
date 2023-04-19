"""@defgroup test_plantuml_context
Tests about Plantuml context diagrams
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_simple_function_plantuml_context(mocker, input_test_simple_function):
    """@ingroup test_plantuml_context
    @anchor test_simple_function_plantuml_context
    Test context diagram display with a single function without input / output

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_simple_function
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_simple_function_plantuml_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_simple_function}\n"
                         "show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = 'object "F1" as f1 <<Function>>\n'

    test_lib.remove_xml_file(file_name)

    assert expected in result
    assert len(result) - len(expected) == len("\'id: xxxxxxxxxx\n")


def test_simple_function_in_out_plantuml_context(mocker):
    """@ingroup test_plantuml_context
    Test context diagram display with a single function with one input and one output

    @param[in] mocker : mocker fixture reference
    @return None

    **Jarvis4se equivalent:**

        with simple_function_in_out
        F1 is a function
        a is a data
        b is a data
        =============================
        with simple_function_in_out
        F1 produces b
        =============================
        with simple_function_in_out
        F1 consumes a
        =============================
        with simple_function_in_out
        show context F1
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_simple_function_in_out_plantuml_context"
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


def test_function_with_attribute_plantuml_context(mocker):
    """@ingroup test_plantuml_context
    Test context diagram display with a single function with attributes and their value

    @param[in] mocker : mocker fixture reference
    @return None

    **Jarvis4se equivalent:**

        with test_function_with_attribute
        F1 is a function
        ========================================
        with test_function_with_attribute
        A is an attribute
        C is an attribute
        ========================================
        with test_function_with_attribute
        The A of F1 is 4,2
        The C of F1 is pink
        ========================================
        with test_function_with_attribute
        show context F1
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_function_with_attribute_plantuml_context"
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


def test_fun_elem_with_attribute_plantuml_context(mocker, input_test_fun_elem_with_attribute):
    """@ingroup test_plantuml_context
    @anchor test_fun_elem_with_attribute_plantuml_context
    Test context diagram display with a single function with attributes and their value, allocated to a functional
    element with same attributes and different values

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_fun_elem_with_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_attribute
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "test_fun_elem_with_attribute_plantuml_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[1]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[2]}\n")
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


def test_fun_elem_with_interfaces_plantuml_context(mocker, input_test_fun_elem_with_interfaces):
    """@ingroup test_plantuml_context
    @anchor test_fun_elem_with_interfaces_plantuml_context
    Test context diagram display with functional elements, their allocated functions and their interfaces

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_fun_elem_with_interfaces : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_interfaces
   """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_context_diagram")
    file_name = "test_fun_elem_with_interfaces_plantuml_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_interfaces}\n"
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
