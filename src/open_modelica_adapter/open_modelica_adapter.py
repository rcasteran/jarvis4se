"""@defgroup open_modelica_adapter
Open modelica adapter module
"""
# Libraries

# Modules
import datamodel
from .util import StateModel


def get_state_machine_model(p_fun_elem_name, p_state_list, p_transition_list, **kwargs):
    string_obj = StateModel(p_fun_elem_name)
    for state_dest in p_state_list:
        is_initial = False
        for transition in p_transition_list:
            if transition.destination == state_dest.id:
                for state_src in p_state_list:
                    if transition.source == state_src.id:
                        if not isinstance(state_src.type, datamodel.BaseType):
                            is_initial = datamodel.EntryStateLabel in state_src.type.name.lower()
                        # Else do nothing
                    # Else do nothing
            # Else do nothing

        if datamodel.EntryStateLabel not in state_dest.name.lower():
            string_obj.create_state(state_dest, is_initial, **kwargs)
        # Else do nothing

    for transition in p_transition_list:
        string_obj.create_transition(transition, **kwargs)

    return string_obj.get_model()
