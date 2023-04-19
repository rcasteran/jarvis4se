"""@defgroup test_input_cell
Tests about Jarvis outputs
"""
# Libraries


# Modules
import test_lib

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_attribute_declaration(capsys, input_test_fun_elem_context_with_attribute):
    """@ingroup test_input_cell
    @anchor test_attribute_declaration
    Test attribute declaration

    @param[in] capsys : capture fixture reference
    @param[in] input_test_fun_elem_context_with_attribute : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_context_with_attribute
    """
    file_name = "attribute_declaration"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_context_with_attribute[1]}\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "C is an attribute\n",
                "A is an attribute\n",
                "B is an attribute\n",
                f"{file_name}.xml updated"]

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_instantiated_attribute(capsys, input_test_fun_elem_context_with_attribute):
    """@ingroup test_input_cell
    @anchor test_instantiated_attribute
    Test attribute instantiation

    @param[in] capsys : capture fixture reference
    @param[in] input_test_fun_elem_context_with_attribute : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_context_with_attribute
    """
    file_name = "described_attribute_input"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_context_with_attribute[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_context_with_attribute[1]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_context_with_attribute[2]}\n")

    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                "Attribute A for F1 with value 4,2\n",
                "Attribute C for F1 with value pink\n",
                "Attribute B for Fun elem with value 8,5\n",
                "Attribute A for Fun elem with value 100\n",
                f"{file_name}.xml updated\n"]
    # Get las part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]

    test_lib.remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_functional_interface(capsys, input_test_functional_interface):
    """@ingroup test_input_cell
    @anchor test_functional_interface
    Test data allocation to functional interface

    @param[in] capsys : capture fixture reference
    @param[in] input_test_functional_interface : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_functional_interface
    """
    file_name = "test_functional_interface"
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


def test_fun_elem_exposes_interface(capsys, input_test_fun_elem_exposes_interface):
    """@ingroup test_input_cell
    @anchor test_fun_elem_exposes_interface
    Test functional interface allocation to functional element

    @param[in] capsys : capture fixture reference
    @param[in] input_test_fun_elem_exposes_interface : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_exposes_interface
    """
    file_name = "test_fun_elem_exposes_interface"
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
