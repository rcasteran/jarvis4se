"""@defgroup test_requirement
Tests about requirements creation
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


def test_requirement_with_id(capsys, input_test_requirement):
    """@ingroup test_requirement_with_id
    @anchor test_requirement
    Test single requirement input

    @param[in] capsys : capsys fixture reference
    @param[in] input_test_requirement : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_requirement
    """
    file_name = "test_requirement_with_id"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_requirement[0]}\n")

    # result is a text about requirement creation
    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                'REQ1 is a Requirement\n',
                f'{file_name}.xml updated\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_requirement_with_text(capsys, input_test_requirement):
    """@ingroup test_requirement
    @anchor test_requirement_with_text
    Test single requirement input

    @param[in] capsys : capsys fixture reference
    @param[in] input_test_requirement : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_requirement
    """
    file_name = "test_requirement_with_text"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_requirement[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_requirement[1]}\n")

    # result is a text about requirement text
    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                '[WARNING] Subject "The system" of the requirement REQ1 is unknown\n',
                'REQ1 text is The system shall open the door\n',
                f'{file_name}.xml updated\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_requirement_derivation(capsys, input_test_requirement):
    """@ingroup test_requirement
    @anchor test_requirement_derivation
    Test single requirement input

    @param[in] capsys : capsys fixture reference
    @param[in] input_test_requirement : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_requirement
    """
    file_name = "test_requirement_derivation"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_requirement[0]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_requirement[1]}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_requirement[2]}\n"
                         f"{input_test_requirement[3]}\n")

    # result is a text about requirement derivation
    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                'REQ2 is a Requirement\n',
                '[WARNING] Subject "the system" of the requirement REQ2 is unknown\n',
                'REQ2 text is If the system detects an emergency stop, then the system shall open the door\n',
                'Requirement REQ2 derives from Requirement REQ1\n',
                'REQ3 is a Requirement\n',
                '[WARNING] Subject "the system" of the requirement REQ3 is unknown\n',
                'REQ3 text is When the system is stopped, if the system detects an emergency stop, '
                'then the system shall open the door\n',
                'Requirement REQ3 derives from Requirement REQ1\n',
                f'{file_name}.xml updated\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)