"""Module that contains tests for State()"""
from conftest import get_jarvis4se, remove_xml_file
import plantuml_adapter

jarvis4se = get_jarvis4se()


def test_state_entry_exit_chain(mocker, state_exit_entry_chain_output_diagram):
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
    assert all(i in result for i in state_exit_entry_chain_output_diagram)
    assert len(result) - len(''.join(state_exit_entry_chain_output_diagram)) == 2*len("\'id: xxxxxxxxxx\n")

    remove_xml_file(file_name)