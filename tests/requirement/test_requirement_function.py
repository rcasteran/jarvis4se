"""@defgroup test_requirement_function
Tests about requirements allocated to function
"""
# Libraries
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Modules
import test_lib

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_simple_requirement_function(capsys, monkeypatch, input_single_requirement):
    """@ingroup test_requirement
    @anchor test_simple_requirement_function
    Test single requirement input

    @param[in] capsys : capsys fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_single_requirement
    """
    req_name = "F1 behavior"
    monkeypatch.setattr('builtins.input', lambda _: req_name)
    file_name = "test_simple_requirement_function"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_single_requirement[1]}\n")

    # result is a text about requirement creation
    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                'Requirement identified: The function F1 shall compute the ambient temperature value based '
                'on the acquired temperature value as specified in the following formula: '
                'AMBIENT_TEMPERATURE_VALUE = ACQUIRED_TEMPERATURE_VALUE * 56 / 100\n',
                f'{req_name} is a requirement\n',
                f'{file_name}.xml updated\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_simple_function_allocation_requirement_function(capsys, monkeypatch, input_single_requirement):
    """@ingroup test_requirement
    @anchor test_simple_function_allocation_requirement_function
    Test single requirement input and allocation to an already existing function

    @param[in] capsys : capsys fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_single_requirement
    """
    req_name = "F1 behavior"
    monkeypatch.setattr('builtins.input', lambda _: req_name)
    file_name = "test_simple_function_allocation_requirement_function"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_single_requirement[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_single_requirement[1]}\n")

    # result is a text about requirement creation
    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                'Requirement identified about F1: The function F1 shall compute the ambient temperature value based on '
                'the acquired temperature value as specified in the following formula: '
                'AMBIENT_TEMPERATURE_VALUE = ACQUIRED_TEMPERATURE_VALUE * 56 / 100\n',
                f'{req_name} is a requirement\n',
                f'Requirement {req_name} is satisfied by Function F1\n',
                f'{file_name}.xml updated']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_simple_function_allocation_manual_requirement_function(capsys, monkeypatch, input_single_requirement):
    """@ingroup test_requirement
    @anchor test_simple_function_allocation_manual_requirement_function
    Test single requirement input and allocation to an already existing function

    @param[in] capsys : capsys fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_single_requirement
    """
    req_name = "F1 behavior"
    monkeypatch.setattr('builtins.input', lambda _: req_name)
    file_name = "test_simple_function_allocation_manual_requirement_function"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_single_requirement[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_single_requirement[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_single_requirement[2]}\n")

    # result is a text about requirement allocation
    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                f'Requirement {req_name} already satisfied by Function F1\n',
                f'No update for {file_name}.xml']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)
