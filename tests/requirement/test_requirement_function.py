"""@defgroup test_requirement_function
Tests about requirements allocated to function
"""
# Libraries
import nltk
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')

# Modules
import test_lib

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_simple_requirement_function(capsys, monkeypatch, input_test_single_requirement):
    """@ingroup test_requirement
    @anchor test_simple_requirement_function
    Test single requirement input

    @param[in] capsys : capsys fixture reference
    @param[in] monkeypatch : monkeypatch fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_single_requirement
    """
    req_name = "F1 behavior"
    monkeypatch.setattr('builtins.input', lambda _: req_name)
    file_name = "test_simple_requirement_function"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_single_requirement[1]}\n")

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


def test_simple_function_allocation_requirement_function(capsys, monkeypatch, input_test_single_requirement):
    """@ingroup test_requirement
    @anchor test_simple_function_allocation_requirement_function
    Test single requirement input and allocation to an already existing function

    @param[in] capsys : capsys fixture reference
    @param[in] monkeypatch : monkeypatch fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_single_requirement
    """
    req_name = "F1 behavior"
    monkeypatch.setattr('builtins.input', lambda _: req_name)
    file_name = "test_simple_function_allocation_requirement_function"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_single_requirement[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_single_requirement[1]}\n")

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


def test_simple_function_allocation_manual_requirement_function(capsys, monkeypatch, input_test_single_requirement):
    """@ingroup test_requirement
    @anchor test_simple_function_allocation_manual_requirement_function
    Test single requirement input and allocation to an already existing function

    @param[in] capsys : capsys fixture reference
    @param[in] monkeypatch : monkeypatch fixture reference
    @param[in] input_test_simple_function : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_single_requirement
    """
    req_name = "F1 behavior"
    monkeypatch.setattr('builtins.input', lambda _: req_name)
    file_name = "test_simple_function_allocation_manual_requirement_function"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_single_requirement[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_single_requirement[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_single_requirement[2]}\n")

    # result is a text about requirement allocation
    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                f'Requirement {req_name} already satisfied by Function F1\n',
                f'No update for {file_name}.xml']

    test_lib.remove_xml_file(file_name)

    print(captured.out)
    assert all(i in captured.out for i in expected)


def test_function_requirement(capsys, monkeypatch, input_test_function_requirement):
    """@ingroup test_requirement
    @anchor test_function_requirement
    Test different requirement for function

    @param[in] capsys : capsys fixture reference
    @param[in] monkeypatch : monkeypatch fixture reference
    @param[in] input_test_function_requirement : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_function_requirement
    """
    req_name_list = iter(["F1_req_1", "F1_req_2", "F1_req_3", "F1_req_4", "F1_req_5"])
    monkeypatch.setattr('builtins.input', lambda _: next(req_name_list))
    file_name = "test_function_requirement"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_requirement[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_function_requirement[1]}\n")

    # result is a text about requirement allocation
    captured = capsys.readouterr()
    expected = [f'Creating {file_name}.xml !\n',
                f'To calculate y is a Function\n',
                f'a is a Data\n',
                f'x is a Data\n',
                f'b is a Data\n',
                f'y is a Data\n',
                f'The alias for To calculate y is F1\n',
                f'{file_name}.xml updated\n',
                f'{file_name}.xml parsed\n',
                f'Requirement identified about To calculate y: To calculate y shall calculate y as follows: y = a*x+b\n',
                f'[WARNING] Function To calculate y does not consume nor produce Data y\n',
                f'Requirement identified about To calculate y: F1 shall calculate y in less than 10 msec\n',
                f'Requirement identified about To calculate y: If a is greater than 1, '
                f'then F1 shall consider a as being equal to 1\n',
                f'[WARNING] Function To calculate y does not consume nor produce Data a\n',
                f'Requirement identified about To calculate y: When a is set to 0, '
                f'F1 shall consider b as being equal to 10\n',
                f'[WARNING] Function To calculate y does not consume nor produce Data b\n',
                f'Requirement identified about To calculate y: When b is changed, if a is set to 0, '
                f'then F1 shall consider b as unchanged\n',
                f'F1_req_1 is a requirement\n',
                f'F1_req_2 is a requirement\n',
                f'F1_req_3 is a requirement\n',
                f'F1_req_4 is a requirement\n',
                f'F1_req_5 is a requirement\n',
                f'Requirement F1_req_1 is satisfied by Function To calculate y\n',
                f'Requirement F1_req_2 is satisfied by Function To calculate y\n',
                f'Requirement F1_req_3 is satisfied by Function To calculate y\n',
                f'Requirement F1_req_4 is satisfied by Function To calculate y\n',
                f'Requirement F1_req_5 is satisfied by Function To calculate y\n',
                f'{file_name}.xml updated']

    test_lib.remove_xml_file(file_name)
    assert all(i in captured.out for i in expected)
