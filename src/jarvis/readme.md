# Intelligent assistant for system engineering activities

This Python Project aims at developing an 'intelligent' assistant for system engineering activities called Jarvis

## Configuration & Dependencies
This project has been developed and tested using :

 - Python (3.9.6+) : https://www.python.org/downloads/
 - IPython (7.27.0+) : ```pip install ipython```
 - lxml (4.6.3+) : ```pip install lxml```
 - Jupyter notebook (6.4.3+): ```pip install notebook```
 - Plantuml (0.3.0): ```pip install plantuml``` 
 - JDK(11.0.11+): tested on 11.0.11 & 15.0.2 (since used of plantuml.jar client to extend PLANTUML_LIMIT_SIZE)
 
## Usage
Clone the MTC/deliverable/script repo from github, then start(cmd```jupyter notebook```) a new notebook within the "jarvis" folder.

Open you Notebook, load JARVIS :
```py
%reload_ext jarvis
```

and then call Jarvis in each cell you want to chat with him using Jupyter's magic function syntax:
```py
%%jarvis
```

## JARVIS Commands

### Overview

#### Scope definition
|                               | Function | Data | State | Functional element | Functional interface | Physical element | Physical interface |
|-------------------------------|:--------:|:----:|:-----:|:------------------:|:--------------------:|:----------------:|:------------------:|
| scope definition              | -        | -    | -     | -                  | -                    | -                | -                  |

#### Objects modification
|                               | Function | Data | State | Functional element | Functional interface | Physical element | Physical interface |
|-------------------------------|:--------:|:----:|:-----:|:------------------:|:--------------------:|:----------------:|:------------------:|
| function creation             | X        | -    | -     | -                  | -                    | -                | -                  |
| data creation                 | -        | X    | -     | -                  | -                    | -                | -                  |
| state creation                | -        | -    | X     | -                  | -                    | -                | -                  |
| functional element creation   | -        | -    | -     | X                  | -                    | -                | -                  |
| functional interface creation | -        | -    | -     | -                  | X                    | -                | -                  |
| physical element creation     | -        | -    | -     | -                  | -                    | X                | -                  |
| physical interface creation   | -        | -    | -     | -                  | -                    | -                | X                  |
| object type                   | X        | X    | X     | X                  | X                    | X                | X                  |
| object alias                  | X        | X    | X     | X                  | X                    | X                | X                  |
| object deletion               | X        | X    | X     | X                  | X                    | X                | X                  |

#### Objects relationship
|                               | Function | Data | State | Functional element | Functional interface | Physical element | Physical interface |
|-------------------------------|:--------:|:----:|:-----:|:------------------:|:--------------------:|:----------------:|:------------------:|
| object composition            | X        | -    | X     | X                  | -                    | X                | -                  |
| object consumption            | -        | X    | -     | -                  | X                    | -                | X                  |
| object production             | -        | X    | -     | -                  | X                    | -                | X                  |
| object allocation             | X        | -    | X     | X                  | -                    | -                | -                  |

#### Diagrams generation
|                               | Function | Data | State | Functional element | Functional interface | Physical element | Physical interface |
|-------------------------------|:--------:|:----:|:-----:|:------------------:|:--------------------:|:----------------:|:------------------:|
| context diagram               | X        | -    | X     | X                  | -                    | X                | -                  |
| decomposition diagram         | X        | -    | X     | X                  | -                    | X                | -                  |
| sequence diagram              | X        | -    | -     | X                  | -                    | X                | -                  |
| state diagram                 | -        | -    | X     | X                  | -                    | X                | -                  |
| overall diagram               | -        | -    | -     | -                  | -                    | -                | -                  |


### Scope definition
Specify the scope of your system engineering activities :
```py
%%jarvis
with <scope>
```

### Objects modification

#### Function creation
Add a function object:
```py
%%jarvis
with <scope>
<object name> is a function
```

#### Data creation
Add a data object:
```py
%%jarvis
with <scope>
<data name> is a data
```

#### State creation
Add a state object:
```py
%%jarvis
with <scope>
<state name> is a state
```

#### Functional element creation
Add a functional element object:
```py
%%jarvis
with <scope>
<functional element name> is a functional element
```

#### Functional interface creation
Add a functional interface object:
```py
%%jarvis
with <scope>
<functional interface name> is a functional interface
```

#### Physical element creation
Add a physical element object:
```py
%%jarvis
with <scope>
<physical element name> is a physical element
```

#### Physical interface creation
Add a physical interface object:
```py
%%jarvis
with <scope>
<physical interface name> is a physical interface
```

#### Object type
Specify the type of an object:
```py
%%jarvis
with <scope>
<object name or alias> is <object type>
```
NB: The type depend on the object and the metamodel used.

#### Object alias
Specify the alias of an object:
```py
%%jarvis
with <scope>
The alias of <object name> is <object alias>
```

### Objects deletion
Delete an element (only if it has no consumption/production relationship):
```py
%%jarvis
with <scope>
Delete <object name or alias>
```

### Objects relationship

#### Object composition
Add composition relationship between objects:
```py
%%jarvis
with <scope>
<object name or alias> composes <object name or alias>
```
or
```py
%%jarvis
with <scope>
<object name or alias> is composed of <object name or alias>
```

#### Object consumption
Add consumption relationship between a consumer object and an object to be consumed :
```py
%%jarvis
with <scope>
<consumer object name or alias> consumes <object name or alias>
```
or
```py
%%jarvis
with <scope>
<object name or alias> is an input of <consumer object name or alias>
```

#### Object production
Add production relationship between a producer object and an object to be produced :
```py
%%jarvis
with <scope>
<producer object name or alias> produces <object name or alias>
```
or
```py
%%jarvis
with <scope>
<object name or alias> is an output of <producer object name or alias>
```

#### Object allocation
Add allocation relationship between a targeted object and an object to be allocated :
```py
%%jarvis
with <scope>
<targeted object name or alias> allocates <object name or alias>
```
or
```py
%%jarvis
with <scope>
<object name or alias> is allocated to <targeted object name or alias>
```

### Diagrams generation

#### Context diagram
Show Context Diagram for an object:
```py
%%jarvis
with <scope>
show context <object name or alias>
```

#### Decomposition diagram
Show Decomposition Diagram for an object:
```py
%%jarvis
with <scope>
show decomposition <object name or alias>
```

#### Sequence diagram
Show Sequence Diagram of a list of object:
```py
%%jarvis
with <scope>
show sequence <object1 name or alias>, <object2 name or alias>
```

#### State diagram
Show State Diagram of an object:
```py
%%jarvis
with <scope>
show state <object1 name or alias>
```

#### Overall diagram
Show the whole model Diagram:
```py
%%jarvis
with <scope>
show all
```

## Development
Read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
