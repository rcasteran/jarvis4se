# JARVIS4SE configuration file
JARVIS4SE configuration file is a file named "config.cfg" and stored under the folder "./config" in the folder where it is executed.

It has the following structure:
```
log = <0|1>
diagram = <0|1>
```
Where:
- ```log = 1``` indicates that log file storage is activated. By default it is deactivated.
- ```diagram = 1``` indicates that diagram file storage is activated. By default it is deactivated.

## Log file storage option
When the log file storage is activated, JARVIS4SE generates a log file "log_<date>.log" where <date> is the current date formatted in %Y%M%D,
  and stores it under the folder "./log" where it is executed.

All log files are deleted when JARVIS4SE is initializing.
  
## Diagram file storage option
When the diagram file storage is activated, JARVIS4SE generates a SVG file "Diagram<uuid>.svg" for each generated diagram where <uuid> is a unique identifier,
  and stores it under the folder "./diagrams" where it is executed.

All SVG files are deleted when JARVIS4SE is initializing.
