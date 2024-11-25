# Installation

## Installation

JARVIS4SE requires a dedicated Python package and a [PlantUML](https://plantuml.com/en/) executable.

### Python package

The dedicated Python package for JARVIS4SE is available under [https://pypi.org/project/jarvis4se/](https://pypi.org/project/jarvis4se/)

JARVIS4SE requires Python 3.8 minimum. All additional python packages will be installed automatically if necessary (see setup.py).

For full depedencies to build and tests, see requirements.txt.

To install JARVIS4SE, please execute the following command line in your compatible Python environment:

```
pip install jarvis4se
```

### PlantUML executable

The PlantUML executable (.jar) for JARVIS4SE is available under [https://plantuml.com/en/download](https://plantuml.com/en/download).

It is a JAR file that needs to be saved in the same directory (root) where you want to execute/call JARVIS4SE.

If not present, the default diagrams server will be [PlantUML online server](https://www.plantuml.com/plantuml/uml/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000) which is limited for large diagrams.

{% hint style="info" %}
The installation of JARVIS4SE comes with the Python package plantuml available under[https://pypi.org/project/plantuml/](https://pypi.org/project/plantuml/) to enable a remote connexion with the PlantUML online server.
{% endhint %}

### OpenModelica executable

The OpenModelica executable is available under [https://openmodelica.org/download/download-windows/](https://openmodelica.org/download/download-windows/)

Once installed, you need to install first PyZMQ, and then OMPython:

* PyZMQ is a Python package available under [https://pypi.org/project/pyzmq/](https://pypi.org/project/pyzmq/)
* OMPython is another Python package delivered in your OpenModelica installation as explained in [https://github.com/OpenModelica/OMPython](https://github.com/OpenModelica/OMPython)

{% hint style="danger" %}
The installation of OpenModelica executable and related Python packages is only required if you activate the option "OpenModelica simulation" of JARVIS4SE.
{% endhint %}

## Installation with [Jupyter](https://jupyter.org)

### Creating a python virtual environment with a terminal

* Open command line in the folder that suits you best
* Create a virtual environment: `python -m venv venv`
* Start your venv depending on your OS:&#x20;
  * Windows: `venv\Scripts\activate`
  * Linux / MacOS: `source venv/bin/activate`
* Follow "Installation" section above in your virtual environment.

### Opening a new notebook

* Start notebook server: `python -m jupyter notebook` (browser should pop up listing files of your folder)
* Open a Notebook: top right corner click New then select the appropriate kernel
* Within a cell, load jarvis extension for JARVIS4SE: `%load_ext jarvis`

## Installation with [IPython](https://ipython.org/)

* Follow "Installation" section above in your virtual environment.
* Start IPython: `python -m IPython`
* Load jarvis extension for JARVIS4SE: `%load_ext jarvis`



