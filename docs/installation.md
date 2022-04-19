# Installation

JARVIS4SE requires a dedicated Python package and a [PlantUML](https://plantuml.com/en/) executable.

## Python package

The dedicated Python package for JARVIS4SE is available under [https://pypi.org/project/jarvis4se/](https://pypi.org/project/jarvis4se/)

JARVIS4SE requires Python 3.8 minimum. All additional python packages will be installed automatically if necessary (see setup.py).

For full depedencies to build and tests, see requirements.txt.

To install JARVIS4SE, please execute the following command line in your compatible Python environment:

```
// pip install jarvis4se
```

## PlantUML executable

The PlantUML executable for JARVIS4SE is available under [https://plantuml.com/en/download](https://plantuml.com/en/download).

It is a JAR file that needs to be located in the same directory than the one where you want to execute JARVIS4SE.

This JAR file needs to be renamed: `plantuml.jar`.

For exemple, if you want to use JARVIS4SE in a [Jupyter Notebook](https://jupyter.org), you need to copy the JAR file in the folder where your notebook is saved.
