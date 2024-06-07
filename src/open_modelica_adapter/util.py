"""@defgroup open_modelica_adapter
Open modelica adapter module
"""
# Libraries

# Modules


class StateModel:
    """@ingroup open_modelica_adapter
    @anchor StateModel
    Class to encode open modelica text for state model
    """

    def __init__(self, p_obj_name):
        """
        @var string_begin
        Open modelica text for declaration beginning

        @var string_global
        Open modelica text for global declaration

        @var string_equation
        Open modelica text for equation

        @var string_algorithm
        Open modelica text for algorithm

        @var string_end
        Open modelica text for declaration end

        @var string_state_name_list
        Open modelica text for state name list

        @var string_state_initial
        Open modelica text for initial state
        """

        # Initialize OpenModelica text
        self.string_begin = f'model {p_obj_name}\n'
        self.string_global = f'Boolean clock\n'
        self.string_equation = 'equation\nclock = sample(0,1);\n'
        self.string_algorithm = 'algorithm\nwhen clock then\n'
        self.string_end = 'end when;\nend system;\n'

        self.string_state_name_list = 'type State = enumeration();'
        self.string_state_initial = ''

    def create_data(self, p_data, p_initial_value=0):
        self.string_global = self.string_global + p_data.modelica_type + ' ' \
                             + p_data.name \
                             + f'(start={p_initial_value});\n'

    def create_state(self, p_state, p_is_initial=False, **kwargs):
        xml_function_list = kwargs['xml_function_list']
        xml_producer_function_list = kwargs['xml_producer_function_list']

        if p_is_initial:
            self.string_state_initial = f'State state(start = State.{p_state.name});\n'
        # Else do nothing

        # Update state name list text
        if self.string_state_name_list[-3] == '(':
            self.string_state_name_list = self.string_state_name_list[:-2] + p_state.name + ');\n'
        else:
            self.string_state_name_list = self.string_state_name_list[:-2] + ', ' + p_state.name + ');\n'

        # Update algorithm
        self.string_algorithm = self.string_algorithm + f'if state == state.{p_state.name} then\n'
        for allocated_function_id in p_state.allocated_function_list:
            for xml_function in xml_function_list:
                if xml_function.id == allocated_function_id:
                    self.string_algorithm = self.string_algorithm + xml_function.modelica_algorithm + ';\n'

                    for xml_producer_function in xml_producer_function_list:
                        if xml_producer_function[1].id == allocated_function_id:
                            self.create_data(xml_producer_function[0])
                        # Else do nothing
                # Else do nothing
        self.string_algorithm = self.string_algorithm + f'endif;\n'

    def create_transition(self, p_transition, **kwargs):
        xml_state_list = kwargs['xml_state_list']
        for xml_state in xml_state_list:
            if xml_state.id == p_transition.destination:
                self.string_algorithm = self.string_algorithm + 'if ' + p_transition.modelica_algorithm + ' then\n' \
                                        + f'state := state.{xml_state.name};' \
                                        + 'endif;\n'
                break
            # Else do nothing

    def get_model(self):
        return self.string_begin \
            + self.string_global \
            + self.string_state_name_list \
            + self.string_state_initial \
            + self.string_equation \
            + self.string_algorithm \
            + self.string_end
