"""@defgroup test_input_cell
Tests about Jarvis outputs
"""
# Libraries


# Modules
import test_lib

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_attribute_declaration_in(capsys, input_test_fun_elem_with_attribute):
    """@ingroup test_input_cell
    @anchor test_attribute_declaration_in
    Test attribute declaration

    @param[in] capsys : capture fixture reference
    @param[in] input_test_fun_elem_with_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_attribute
    """
    file_name = "test_attribute_declaration_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[1]}\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "C is an attribute\n",
                "A is an attribute\n",
                "B is an attribute\n",
                f"{file_name}.xml updated"]

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_instantiated_attribute_in(capsys, input_test_fun_elem_with_attribute):
    """@ingroup test_input_cell
    @anchor test_instantiated_attribute_in
    Test attribute instantiation

    @param[in] capsys : capture fixture reference
    @param[in] input_test_fun_elem_with_attribute : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_attribute
    """
    file_name = "test_instantiated_attribute_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[1]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_attribute[2]}\n")

    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                "Attribute A for F1 with value 4,2\n",
                "Attribute C for F1 with value pink\n",
                "Attribute B for Fun elem with value 8,5\n",
                "Attribute A for Fun elem with value 100\n",
                f"{file_name}.xml updated\n"]
    # Get las part from capsys
    last_out = captured.out[-len(''.join(expected)) - 1:len(captured.out)]

    test_lib.remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_functional_interface_in(capsys, input_test_functional_interface):
    """@ingroup test_input_cell
    @anchor test_functional_interface_in
    Test data allocation to functional interface

    @param[in] capsys : capture fixture reference
    @param[in] input_test_functional_interface : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_functional_interface
    """
    file_name = "test_functional_interface_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_functional_interface}\n")

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

    test_lib.remove_xml_file(file_name)

    assert len(captured.out) == len("".join(expected))
    assert all(i in captured.out for i in expected)


def test_fun_elem_exposes_interface_in(capsys, input_test_fun_elem_exposes_interface):
    """@ingroup test_input_cell
    @anchor test_fun_elem_exposes_interface_in
    Test functional interface allocation to functional element

    @param[in] capsys : capture fixture reference
    @param[in] input_test_fun_elem_exposes_interface : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_exposes_interface
    """
    file_name = "test_fun_elem_exposes_interface_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_exposes_interface}\n")

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

    test_lib.remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_function_output_auto_in(capsys, input_test_function_output_auto_decomposition):
    """@ingroup test_input_cell
    @anchor test_function_output_auto_in
    Test function decomposition

    @param[in] capsys : capture fixture reference
    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    captured = capsys.readouterr()
    expected = ["F is a Function\n",
                "a is a Data\n",
                "F1 is a Function\n",
                "F2 is a Function\n",
                "F is composed of F1\n",
                "F is composed of F2\n",
                "[WARNING] No producer found for a\n",
                "[WARNING] No producer found for a\n"
                "F2 consumes a\n",
                "F consumes a\n",
                "F does not consume a anymore\n",
                "F produces a\n",
                "F1 produces a\n",
                f"{file_name}.xml updated\n"]

    # Get last part from capsys
    last_out = captured.out[-len(''.join(expected)):len(captured.out)]

    test_lib.remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_function_output_auto_splitted_in(capsys, input_test_function_output_auto_decomposition):
    """@ingroup test_input_cell
    @anchor test_function_output_auto_splitted_in
    Test function decomposition done in multiple cells

    @param[in] capsys : capture fixture reference
    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    captured = capsys.readouterr()
    expected = ["F2 is a Function\n",
                "F is composed of F2\n",
                "F does not produce a anymore\n",
                "F2 consumes a\n",
                f"{file_name}.xml updated\n"]

    # Get last part from capsys
    last_out = captured.out[-len(''.join(expected)):len(captured.out)]

    test_lib.remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_function_output_auto_external_in(capsys, input_test_function_output_auto_decomposition):
    """@ingroup test_input_cell
    @anchor test_function_output_auto_external_in
    Test function decomposition done in multiple cells and with external function

    @param[in] capsys : capture fixture reference
    @param[in] input_test_function_output_auto_decomposition : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_output_auto_decomposition
    """
    file_name = "test_function_output_auto_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[2]}\n")

    captured = capsys.readouterr()
    expected = ["FE is a Function\n",
                "F produces a due to one of its children\n",
                "FE consumes a\n",
                f"{file_name}.xml updated\n"]

    # Get last part from capsys
    last_out = captured.out[-len(''.join(expected)):len(captured.out)]

    test_lib.remove_xml_file(file_name)

    assert all(i in last_out for i in expected)
