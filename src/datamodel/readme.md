# Package Datamodel

## Installation

### ArKItect installation
The package "Datamodel" has to be installed under the folder '/PythonLib/Lib' of the ArKItect installation folder

### Jupyter notebook installation
The import of the package elements has to be modified from:
```
import <element_name>
```
to
```
import datamodel.<element_name>
```
And all references to the elements have to be replaced accordingly.

## Content
The package "Datamodel" instanciates the objects :
* coming from the [3SE datamodel](https://github.com/rcasteran/3se/tree/main/datamodel)
* used to describe a graphical display, such as Point and EndPoint
