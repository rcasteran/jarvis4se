"""@defgroup test_handler_question
Tests about Jarvis answer to user's question
"""
# Libraries

# Modules
import test_lib

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_simple_function_handler_question(capsys, input_test_simple_function):
    """@ingroup test_handler_question
    @anchor test_simple_function_handler_question
    Test user's question about simple function

    @param[in] capsys : capture fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_simple_function
    """
    file_name = "test_simple_function_handler_question"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_simple_function}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "what is F1 ?\n")

    # result is a text about F1 properties
    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                '"F1" is a Function with identifier ',
                '"F1" has no child.\n',
                '"F1" has no allocated requirement.\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_function_output_auto_handler_question(capsys, input_test_function_output_auto_decomposition):
    """@ingroup test_handler_question
    @anchor test_function_output_auto_handler_question
    Test user's question about function decomposition

    @param[in] capsys : capture fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_simple_function
    """
    file_name = "test_function_output_auto_handler_question"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_output_auto_decomposition[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         "what is F ?\n")

    # result is a text about F properties
    captured = capsys.readouterr()
    print(captured)
    expected = [f"{file_name}.xml parsed\n",
                '"F" is a Function with identifier ',
                '"F" has 2 children:\n',
                ' - "F1" with identifier ',
                ' - "F2" with identifier ',
                '"F" has no allocated requirement.\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)
