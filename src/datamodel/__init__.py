""" @defgroup datamodel
Module for 3SE datamodel

Defines the following basic types that are manipulated by systems engineers:
- For functional analysis: @ref Function, @ref Data, @ref FunctionalElement and @ref FunctionalInterface
- For state analysis: @ref State and @ref Transition
- For physical analysis: @ref PhysicalElement and @ref PhysicalInterface
- For type declaration: @ref BaseType and @ref Type
- For attribute declaration: @ref Attribute
- For view declaration: @ref View
"""

from .datamodel import Function
from .datamodel import Data
from .datamodel import State
from .datamodel import Transition
from .datamodel import FunctionalElement
from .datamodel import View
from .datamodel import Attribute
from .datamodel import FunctionalInterface
from .datamodel import PhysicalElement
from .datamodel import PhysicalInterface
from .datamodel import Type
from .datamodel import BaseType
from .datamodel import Requirement
from .datamodel import TypeWithChildList
from .datamodel import TypeWithChildListFunctionIndex
from .datamodel import TypeWithChildListStateIndex
from .datamodel import TypeWithChildListFunctionalElementIndex
from .datamodel import TypeWithChildListPhysicalElementIndex
from .datamodel import TypeWithChildListRequirementIndex
from .datamodel import EntryStateLabel
from .datamodel import ExitStateLabel
from .datamodel import DesignAttributeLabel
from .datamodel import InitialValueAttributeLabel
from .datamodel import RequirementTextLabel
