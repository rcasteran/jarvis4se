# JARVIS4SE configuration file
JARVIS4SE configuration file is a file named "config.cfg" and stored under the folder "./config" in the folder where JARVIS4SE is executed.

It has the following structure:
```
log = <0|1>
diagram = <0|1>
open_modelica = <0|1>
verbose = <0|1|2>
```
Where:
- ```log = 1``` indicates that log file storage is activated. By default it is deactivated.
- ```diagram = 1``` indicates that diagram file storage is activated. By default it is deactivated.
- ```open_modelica = 1``` indicates that OpenModelica simulation is activated. By default it is deactivated.
- ```verbose = 0``` indicates that only ERROR and WARNING messages are displayed
- ```verbose = 1``` indicates that ERROR, WARNING and INFO messages are displayed
- ```verbose = 2``` indicates that ERROR, WARNING, INFO and DEBUG messages are displayed

## Log file storage option
When the log file storage is activated, JARVIS4SE generates a log file "log_<date>.log" where <date> is the current date formatted in %Y%M%D,
  and stores it under the folder "./log" where it is executed.

All log files are deleted when JARVIS4SE is initializing.

By default, the log file storage is deactivated.
  
## Diagram file storage option
When the diagram file storage is activated, JARVIS4SE generates a SVG file "Diagram<uuid>.svg" for each generated diagram where <uuid> is a unique identifier,
  and stores it under the folder "./diagrams" where it is executed.

All SVG files are deleted when JARVIS4SE is initializing.

By default, the diagram file storage is deactivated.

## OpenModelica simulation
When the OpenModelica simulation is activated, JARVIS4SE will connect to the OpenModelica executable to run simulation and to plot simulation results.

All simulation files are stored under the folder "./simulations/".

By default, the OpenModelica simulation is deactivated.

## Verbosity level option
By default, ERROR, WARNING and INFO messages are displayed (which corresponds to ```verbose = 1```)