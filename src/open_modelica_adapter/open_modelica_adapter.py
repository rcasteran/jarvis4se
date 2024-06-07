"""@defgroup open_modelica_adapter
Open modelica adapter module
"""
# Libraries

# Modules
import datamodel
from .util import StateModel


def get_state_machine_model(p_fun_elem_name, p_state_list, p_transition_list, **kwargs):
    string_obj = StateModel(p_fun_elem_name)
    for state in p_state_list:
        is_initial = False
        for transition in p_transition_list:
            if transition.destination == state:
                if not isinstance(transition.source.type, datamodel.BaseType):
                    is_initial = datamodel.EntryStateLabel in transition.source.type.name.lower()
                # Else do nothing
            # Else do nothing

        string_obj.create_state(state, is_initial, **kwargs)

    for transition in p_transition_list:
        string_obj.create_transition(transition, **kwargs)

    return string_obj.get_model()
