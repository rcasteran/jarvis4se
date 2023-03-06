""" @package plantuml_adapter
Plantuml adapter module

Defines the different functions and classes used by Jarvis to call Plantuml as a diagram generator:
- function to construct the PlantUml text and url for the functions diagram: @ref get_function_diagrams
- function to construct the PlantUml text for the sequence diagrams: @ref get_sequence_diagram
- function to construct the PlantUml text and url for state machine diagrams:
@ref get_state_machine_diagram
- function to construct the PlantUml text for the functional element decomposition diagram:
@ref get_fun_elem_decomposition
- function to construct the PlantUml text and url for the context diagram for functional elements:
@ref get_fun_elem_context_diagram
- class to handle local PlantUml PicoWeb Server: @ref PlantUmlPicoServer
- class to encode PlantUml text and get server url as .svg : @ref PlantUmlGen
- class to encode PlantUml text for state diagram : @ref StateDiagram
- class to encode PlantUml text for sequence diagram : @ref SequenceDiagram
- class to encode PlantUml text for object diagram : @ref ObjDiagram
"""

from .plantuml_adapter import get_function_diagrams
from .plantuml_adapter import get_sequence_diagram
from .plantuml_adapter import get_state_machine_diagram
from .plantuml_adapter import get_fun_elem_decomposition
from .plantuml_adapter import get_fun_elem_context_diagram
from .util import PlantUmlPicoServer
from .util import PlantUmlGen
