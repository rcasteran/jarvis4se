"""@defgroup open_modelica_adapter
Open modelica adapter module
"""
# Libraries
from OMPython import OMCSessionZMQ

# Modules
from tools import Logger


class OpenModelicaConnector(OMCSessionZMQ):
    def __init__(self):
        super().__init__()

    def simulate(self, p_om_name, p_om_directory, p_om_file, p_start_time, p_stop_time):
        if self.sendExpression(f'cd("{p_om_directory}")'):
            if self.sendExpression(f'loadFile("{p_om_file}")'):
                Logger.set_info(__name__, f'Simulation model loaded...')
                if self.sendExpression(f'instantiateModel({p_om_name})'):
                    Logger.set_info(__name__, f'Simulation model instantiated...')
                    result = self.sendExpression(f'simulate({p_om_name}, startTime={p_start_time}, stopTime={p_stop_time})')
                    if 'LOG_SUCCESS' in result['messages']:
                        Logger.set_info(__name__,
                                        f'Simulation done')
                    else:
                        Logger.set_error(__name__,
                                         f'Simulation failed. Please refer to the simulation log file')
                else:
                    Logger.set_error(__name__,
                                     f'Model instantiation failed. Please check the model: {p_om_name}')
            else:
                Logger.set_error(__name__,
                                 f'Model load failed. Please check the model: {p_om_name}')
        else:
            Logger.set_error(__name__,
                             f'Working directory change failed. Please check the directory: {p_om_directory}')

    def plot(self, p_var_list):
        if self.sendExpression('plot({' + p_var_list[0] + '})'):
            Logger.set_info(__name__, f'Variables "{p_var_list[0]}" displayed')
        else:
            Logger.set_error(__name__, f'Variables "{p_var_list[0]}" not displayed')




