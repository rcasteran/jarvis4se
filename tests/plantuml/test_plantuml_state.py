"""@defgroup test_plantuml_state
Tests about Plantuml state diagrams
"""
# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_entry_exit_plantuml_state(mocker):
    """Notebook equivalent:
     %%jarvis
     with state_entry_exit_chain
    EXIT_TOTO extends state
    ENTRY state extends state
    S1 is a EXIT_TOTO
    S2 is a ENTRY state
    show chain S1, S2
     """
    spy = mocker.spy(plantuml_adapter, "get_state_machine_diagram")
    file_name = "state_entry_exit_chain"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         "EXIT_TOTO extends state\n"
                         "ENTRY state extends state\n"
                         "S1 is a EXIT_TOTO\n"
                         "S2 is a ENTRY state\n"
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
