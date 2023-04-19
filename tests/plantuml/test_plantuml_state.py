"""@defgroup test_plantuml_state
Tests about Plantuml state diagrams
"""
# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_entry_exit_plantuml_state(mocker, input_test_entry_exit):
    """@ingroup test_plantuml_state
    @anchor test_entry_exit_plantuml_state
    Test state diagram display for entry and exit states in a chain

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_entry_exit : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_entry_exit
    """
    spy = mocker.spy(plantuml_adapter, "get_state_machine_diagram")
    file_name = "state_entry_exit_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_entry_exit}\n"
                         "show chain S1, S2\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['skinparam useBetaStyle true\n',
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
                'state "S2" as s2 <<ENTRY>>\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 2 * len("\'id: xxxxxxxxxx\n")
