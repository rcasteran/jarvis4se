# Installation

JARVIS4SE requires a dedicated Python package and a [PlantUML](https://plantuml.com/en/) executable.

## Python package

The dedicated Python package for JARVIS4SE is available under 
[https://pypi.org/project/jarvis4se/](https://pypi.org/project/jarvis4se/)

JARVIS4SE requires Python 3.8 minimum. All additional python packages will be installed 
automatically if necessary (see setup.py).

For full depedencies to build and tests, see requirements.txt.

To install JARVIS4SE, please execute the following command line in your compatible Python environment:

```
pip install jarvis4se
```

## PlantUML executable

The PlantUML executable(.jar) for JARVIS4SE is available under [https://plantuml.com/en/download](https://plantuml.com/en/download).

It is a JAR file that needs to be saved in the same directory(root) where you want to execute/call 
JARVIS4SE.

If not present, the default diagrams server will be [PLantUML online server](https://www.plantuml.com/plantuml/uml/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000) 
which is limited for large diagrams.


# Installation with [Jupyter Notebook](https://jupyter.org)

## With terminal

- Open command line in the folder that suits you best
- Create a virtual environment: ````python3 -m venv venv````
- Start your venv depending on your OS: Windows ````venv\Scripts\activate````/ 
LINUX/MACOS```source venv/bin/activate```
- Follow "Installation" section above.
- Start notebook server: ```jupyter notebook```(browser should pop up listing files of your folder)
- Open a Notebook: Top right corner click New>Python3(ipykernel)
- Within a cell, load jarvis extension for JARVIS4SE:```%load_ext jarvis```
- See [Documentation](https://github.com/rcasteran/jarvis4se/tree/main/docs) for the rest ;)