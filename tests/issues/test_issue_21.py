"""@defgroup test_issue_21
Tests about type and alias related to https://github.com/rcasteran/jarvis4se/issues/21

@see test_issue_21_in
"""
# Libraries


# Modules
import test_lib

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_21_in(capsys, input_test_issue_21):
    """@ingroup test_input_cell
    @anchor test_issue_21_in
    Test type and alias related to @ref test_issue_21

    @param[in] capsys : capture fixture reference
    @param[in] input_test_issue_21 : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_issue_21
    """
    file_name = "test_issue_21_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_21}\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "high level function is a type extending Function\n"
                "F1 is a Function\n",
                "The alias for F1 is f1\n",
                "The type of F1 is high level function\n",
                f"{file_name}.xml updated\n"]

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)
    assert len(captured.out) == len(''.join(expected))
