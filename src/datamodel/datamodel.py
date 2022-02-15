#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Libraries
from enum import Enum

# Modules
import util


# Function type
# Compatible with ArKItect and XMI
class FunctionType(Enum):
    UNKNOWN = 0
    ENABLING = 1
    HIGH_LEVEL_FUNCTION = 2
    FUNCTION = 3
    HIGH_LEVEL_SAFETY = 4
    SAFETY = 5
    ADD = 6
    SUBTRACT = 7
    MULTIPLY = 8
    DIVIDE = 9

    def __str__(self):
        type = 'unknown'

        if self == self.ENABLING:
            type = 'Enabling function'
        elif self == self.HIGH_LEVEL_FUNCTION:
            type = 'High level function'
        elif self == self.FUNCTION:
            type = 'Function'
        elif self == self.HIGH_LEVEL_SAFETY:
            type = 'High level safety function'
        elif self == self.SAFETY:
            type = 'Safety function'
        elif self == self.ADD:
            type = 'Add'
        elif self == self.SUBTRACT:
            type = 'Subtract'
        elif self == self.MULTIPLY:
            type = 'Multiply'
        elif self == self.DIVIDE:
            type = 'Divide'

        return type

    @classmethod
    def get_name(cls, type):
        name = cls.UNKNOWN

        if type == 'Enabling function':
            name = cls.ENABLING
        elif type == 'High level function':
            name = cls.HIGH_LEVEL_FUNCTION
        elif type == 'Function':
            name = cls.FUNCTION
        elif type == 'High level safety function':
            name = cls.HIGH_LEVEL_SAFETY
        elif type == 'Safety function':
            name = cls.SAFETY
        elif type == 'Add':
            name = cls.ADD
        elif type == 'Subtract':
            name = cls.SUBTRACT
        elif type == 'Multiply':
            name = cls.MULTIPLY
        elif type == 'Divide':
            name = cls.DIVIDE

        return name

    @classmethod
    def get_parent_function_type_list(cls):
        return [FunctionType.FUNCTION,
                FunctionType.HIGH_LEVEL_FUNCTION,
                FunctionType.SAFETY,
                FunctionType.HIGH_LEVEL_SAFETY,
                FunctionType.UNKNOWN]


# Function class
# Compatible with ArKItect and XMI
class Function:
    def __init__(self, p_id='', p_name='', p_alias='', p_type=FunctionType.UNKNOWN, p_parent=None,
                 p_ark_obj=None, p_role=None, p_operand=None):
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.ark_obj = p_ark_obj
        self.child_list = set()
        self.port_list = set()
        self.input_role = p_role
        self.operand = p_operand

    def set_id(self, p_id):
        self.id = p_id

    def set_name(self, p_name):
        self.name = p_name

    def set_alias(self, p_alias):
        self.alias = p_alias

    def set_type(self, p_type):
        self.type = p_type

    def set_parent(self, p_parent):
        self.parent = p_parent

    # Specific for ArKItect
    def set_ark_obj(self, p_ark_obj):
        self.ark_obj = p_ark_obj

    def add_child(self, p_child):
        self.child_list.add(p_child)

    # Specific for XMI
    def add_port(self, p_port):
        self.port_list.add(p_port)

    def set_input_role(self, p_role):
        self.input_role = p_role

    def set_operand(self):
        if self.type == FunctionType.DIVIDE:
            self.operand = "denominator"
        elif self.type == FunctionType.SUBTRACT:
            self.operand = "subtractor"
        else:
            # May have further type/operand in the future
            None


# System element type
# Compatible with LT SPICE
class SYSTEM_ELEMENT_TYPE(Enum):
    UNKNOWN = 0
    HIGH_LEVEL = 1
    SYSTEM = 2
    RESISTOR = 3
    CAPACITOR = 4
    ZENER = 5
    NPN = 6
    PNP = 7
    DIODE = 8
    VOLTAGE = 9
    LED = 10

    def __str__(self):
        type = 'unknown'

        if self == self.HIGH_LEVEL:
            type = 'High level system element'
        elif self == self.SYSTEM:
            type = 'System element'
        elif self == self.RESISTOR:
            type = 'res'
        elif self == self.CAPACITOR:
            type = 'cap'
        elif self == self.ZENER:
            type = 'zener'
        elif self == self.NPN:
            type = 'npn'
        elif self == self.PNP:
            type = 'pnp'
        elif self == self.DIODE:
            type = 'diode'
        elif self == self.VOLTAGE:
            type = 'voltage'
        elif self == self.LED:
            type = 'LED'

        return type

    @classmethod
    def get_name(cls, type):
        name = cls.UNKNOWN

        if type == 'High level system element':
            name = cls.HIGH_LEVEL
        elif type == 'System element':
            name = cls.SYSTEM
        # LTSPICE compatible
        elif type == 'res':
            name = cls.RESISTOR
        # LTSPICE compatible
        elif type == 'cap':
            name = cls.CAPACITOR
        # LTSPICE compatible
        elif type == 'zener':
            name = cls.ZENER
        # LTSPICE compatible
        elif type == 'npn':
            name = cls.NPN
        # LTSPICE compatible
        elif type == 'pnp':
            name = cls.PNP
        # LTSPICE compatible
        elif type == 'diode':
            name = cls.DIODE
        # LTSPICE compatible
        elif type == 'voltage':
            name = cls.VOLTAGE
        # LTSPICE compatible
        elif type == 'LED':
            name = cls.LED

        return name


# Element class
# Compatible with LTSPICE
# Depends on EndPoint class
class Element:
    def __init__(self, p_id='', p_name='', p_alias='', p_type=SYSTEM_ELEMENT_TYPE.UNKNOWN,
                 p_parent=None, p_ark_obj=None, p_role=None, p_spice_rotation='',
                 p_spice_prefix='', p_spice_model=''):
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.ark_obj = p_ark_obj
        self.child_list = set()
        self.port_list = set()
        self.input_role = p_role
        self.point_list = []
        self.spice_window_list = set()
        self.spice_rotation = p_spice_rotation
        self.constraint_list = set()
        self.spice_prefix = p_spice_prefix
        self.spice_model = p_spice_model

    def set_id(self, p_id):
        self.id = p_id

    def set_name(self, p_name):
        self.name = p_name

    def set_alias(self, p_alias):
        self.alias = p_alias

    def set_type(self, p_type):
        self.type = p_type

    def set_parent(self, p_parent):
        self.parent = p_parent

    # Specific for ArKItect
    def set_ark_obj(self, p_ark_obj):
        self.ark_obj = p_ark_obj

    def add_child(self, p_child):
        self.child_list.add(p_child)

    # Specific for XMI
    def add_port(self, p_port):
        self.port_list.add(p_port)

    def set_input_role(self, p_role):
        self.input_role = p_role

    # Specific for LTSPICE
    def add_spice_window(self, p_window):
        self.spice_window_list.add(p_window)

    # Specific for LTSPICE
    def set_spice_rotation(self, p_ref):
        self.spice_rotation = p_ref

    # Specific for LTSPICE
    def add_point(self, p_point):
        self.point_list.append(p_point)

    # Specific for LTSPICE
    def add_constraint(self, p_constraint):
        self.constraint_list.add(p_constraint)

    # Specific for LTSPICE
    def set_spice_prefix(self, p_prefix):
        self.spice_prefix = p_prefix

    # Specific for LTSPICE
    def set_spice_model(self, p_model):
        self.spice_model = p_model

    # Specific for LTSPICE
    def determine_relative_point(self, p_point):
        if str(self.type).find("voltage") > -1:
            if self.spice_rotation == "R0":
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y + 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y + 96)
                self.add_point(point)
            elif self.spice_rotation == "R90":
                point = util.Point()
                point.set_x(p_point.x - 16)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 96)
                point.set_y(p_point.y)
                self.add_point(point)
            elif self.spice_rotation == "R180":
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y - 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y - 96)
                self.add_point(point)
            elif self.spice_rotation == "R270":
                point = util.Point()
                point.set_x(p_point.x + 16)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 96)
                point.set_y(p_point.y)
                self.add_point(point)
            else:
                print("Unsupported rotation value: " + self.spice_rotation)
        elif str(self.type).find("cap") > -1 or str(self.type).find("zener") > -1 or \
                str(self.type).find("diode") > -1 or str(self.type).find("LED") > -1:
            if self.spice_rotation == "R0":
                point = util.Point()
                point.set_x(p_point.x + 16)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 16)
                point.set_y(p_point.y + 64)
                self.add_point(point)
            elif self.spice_rotation == "R90":
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y + 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 64)
                point.set_y(p_point.y + 16)
                self.add_point(point)
            elif self.spice_rotation == "R180":
                point = util.Point()
                point.set_x(p_point.x - 16)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 16)
                point.set_y(p_point.y - 64)
                self.add_point(point)
            elif self.spice_rotation == "R270":
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y - 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 64)
                point.set_y(p_point.y - 16)
                self.add_point(point)
            else:
                print("Unsupported rotation value: " + self.spice_rotation)
        elif str(self.type).find("res") > -1:
            if self.spice_rotation == "R0":
                point = util.Point()
                point.set_x(p_point.x + 16)
                point.set_y(p_point.y + 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 16)
                point.set_y(p_point.y + 96)
                self.add_point(point)
            elif self.spice_rotation == "R90":
                point = util.Point()
                point.set_x(p_point.x - 16)
                point.set_y(p_point.y + 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 96)
                point.set_y(p_point.y + 16)
                self.add_point(point)
            elif self.spice_rotation == "R180":
                point = util.Point()
                point.set_x(p_point.x - 16)
                point.set_y(p_point.y - 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 16)
                point.set_y(p_point.y - 96)
                self.add_point(point)
            elif self.spice_rotation == "R270":
                point = util.Point()
                point.set_x(p_point.x + 16)
                point.set_y(p_point.y - 16)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 96)
                point.set_y(p_point.y - 16)
                self.add_point(point)
            else:
                print("Unsupported rotation value: " + self.spice_rotation)
        elif str(self.type).find("npn") > -1 or str(self.type).find("pnp") > -1:
            if self.spice_rotation == "R0":
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y + 48)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 64)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 64)
                point.set_y(p_point.y + 96)
                self.add_point(point)
            elif self.spice_rotation == "R90":
                point = util.Point()
                point.set_x(p_point.x - 48)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y + 64)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 96)
                point.set_y(p_point.y + 64)
                self.add_point(point)
            elif self.spice_rotation == "R180":
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y - 48)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 64)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x - 64)
                point.set_y(p_point.y - 96)
                self.add_point(point)
            elif self.spice_rotation == "R270":
                point = util.Point()
                point.set_x(p_point.x + 48)
                point.set_y(p_point.y)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x)
                point.set_y(p_point.y - 64)
                self.add_point(point)
                point = util.Point()
                point.set_x(p_point.x + 96)
                point.set_y(p_point.y - 64)
                self.add_point(point)
            else:
                print("Unsupported rotation value: " + self.spice_rotation)
        else:
            print("Unsupported type value for relative points: " + str(self.type))


# Interface class
# Compatible with LTSPICE
# Depends on Point class
class Interface:
    def __init__(self, p_name=''):
        self.name = p_name
        self.point_list = []
        self.provider_list = set()
        self.user_list = set()

    def set_name(self, p_name):
        self.name = p_name

    def add_point(self, p_point):
        self.point_list.append(p_point)

    def set_provider_user_list(self, p_element):
        for point in p_element.point_list:
            if abs(point.x - self.point_list[0].x) == 0 \
                    and abs(point.y - self.point_list[0].y) == 0:
                self.provider_list.add(p_element)
            elif abs(point.x - self.point_list[1].x) == 0 \
                    and abs(point.y - self.point_list[1].y) == 0:
                self.user_list.add(p_element)
            #Else do nothing


# Data type
class DataType(Enum):
    UNKNOWN = 0
    FLOW = 1
    SAFETY = 2

    def __str__(self):
        data_type = 'unknown'
        if self == self.FLOW:
            data_type = 'Flow'
        elif self == self.SAFETY:
            data_type = 'Safety flow'

        return data_type

    @classmethod
    def get_name(cls, data_type):
        name = cls.UNKNOWN

        if data_type == 'Flow':
            name = cls.FLOW
        if data_type == 'Safety flow':
            name = cls.SAFETY
        return name


# Data class
class Data:
    def __init__(self, p_id='', p_name='', p_type=DataType.UNKNOWN):
        self.id = p_id
        self.name = p_name
        self.type = p_type
        self.predecessor_list = set()

    def set_id(self, p_id):
        self.id = p_id

    def set_name(self, p_name):
        self.name = p_name

    def set_type(self, p_type):
        self.type = p_type

    def add_predecessor(self, p_predecessor):
        self.predecessor_list.add(p_predecessor)


# State type
class StateType(Enum):
    UNKNOWN = 0
    STATE = 1
    HIGH_LEVEL_STATE = 2
    ENTRY = 3
    EXIT = 4

    def __str__(self):
        state_type = 'unknown'
        
        if self == self.STATE:
            state_type = 'State'
        elif self == self.HIGH_LEVEL_STATE:
            state_type = 'High Level State'
        elif self == self.ENTRY:
            state_type = 'Entry'
        elif self == self.EXIT:
            state_type = 'Exit'

        return state_type

    @classmethod
    def get_name(cls, state_type):
        name = cls.UNKNOWN

        if state_type == 'State':
            name = cls.STATE
        elif state_type == 'High Level State':
            name = cls.HIGH_LEVEL_STATE
        elif state_type == 'Entry':
            name = cls.ENTRY
        elif state_type == 'Exit':
            name = cls.EXIT
        
        return name


# State class
class State:
    def __init__(self, p_id='', p_name='', p_alias='', p_type=StateType.UNKNOWN, p_parent=None):
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.allocated_function_list = set()

    def set_id(self, p_id):
        self.id = p_id

    def set_name(self, p_name):
        self.name = p_name

    def set_alias(self, p_alias):
        self.alias = p_alias

    def set_type(self, p_type):
        self.type = p_type

    def set_parent(self, p_parent):
        self.parent = p_parent

    def add_child(self, p_child):
        self.child_list.add(p_child)

    def add_allocated_function(self, p_function):
        self.allocated_function_list.add(p_function)


# Transition type
class TransitionType(Enum):
    UNKNOWN = 0
    DEFAULT = 1

    def __str__(self):
        state_type = 'unknown'
        if self == self.DEFAULT:
            state_type = 'Default'

        return state_type

    @classmethod
    def get_name(cls, state_type):
        name = cls.UNKNOWN
        if state_type == 'Default':
            name = cls.DEFAULT

        return name


# Transition class
class Transition:
    def __init__(self, p_id='', p_name='', p_alias='', p_type=StateType.UNKNOWN, p_source=None,
                 p_destination=None):
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.source = p_source
        self.destination = p_destination
        self.condition_list = set()

    def set_id(self, p_id):
        self.id = p_id

    def set_name(self, p_name):
        self.name = p_name

    def set_alias(self, p_alias):
        self.alias = p_alias

    def set_type(self, p_type):
        self.type = p_type

    def set_source(self, p_source):
        self.source = p_source

    def set_destination(self, p_destination):
        self.destination = p_destination

    def add_condition(self, p_condition):
        self.condition_list.add(p_condition)


# FunctionalElement type
class FunctionalElementType(Enum):
    UNKNOWN = 0
    ENABLING = 1
    FUNCTIONAL_ELEMENT = 2
    HIGH_LEVEL_FUNCTIONAL_ELEMENT = 3

    def __str__(self):
        functional_element_type = 'unknown'
        if self == self.ENABLING:
            functional_element_type = 'Enabling functional element'
        elif self == self.FUNCTIONAL_ELEMENT:
            functional_element_type = 'Functional element'
        elif self == self.HIGH_LEVEL_FUNCTIONAL_ELEMENT:
            functional_element_type = 'High level functional element'

        return functional_element_type

    @classmethod
    def get_name(cls, functional_element_type):
        name = cls.UNKNOWN
        
        if functional_element_type == 'Enabling functional element':
            name = cls.ENABLING
        elif functional_element_type == 'Functional element':
            name = cls.FUNCTIONAL_ELEMENT
        elif functional_element_type == 'High level functional element':
            name = cls.HIGH_LEVEL_FUNCTIONAL_ELEMENT
        
        return name


# FunctionalElement class
class FunctionalElement:
    def __init__(self, p_id='', p_name='', p_alias='', p_type=FunctionalElementType.UNKNOWN,
                 p_parent=None):
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.allocated_state_list = set()
        self.allocated_function_list = set()

    def set_id(self, p_id):
        self.id = p_id

    def set_name(self, p_name):
        self.name = p_name

    def set_alias(self, p_alias):
        self.alias = p_alias

    def set_type(self, p_type):
        self.type = p_type

    def set_parent(self, p_parent):
        self.parent = p_parent

    def add_child(self, p_child):
        self.child_list.add(p_child)

    def add_allocated_state(self, p_state):
        self.allocated_state_list.add(p_state)

    def add_allocated_function(self, p_function):
        self.allocated_function_list.add(p_function)


# Chain type
class ChainType(Enum):
    UNKNOWN = 0
    FUNCTION = 1
    STATE = 2
    TRANSITION = 3
    FUNCTIONAL_ELEMENT = 4
    DATA = 5

    def __str__(self):
        chain_type = 'unknown'

        if self == self.FUNCTION:
            chain_type = 'Function'
        elif self == self.STATE:
            chain_type = 'State'
        elif self == self.TRANSITION:
            chain_type = 'Transition'
        elif self == self.FUNCTIONAL_ELEMENT:
            chain_type = 'Functional element'
        elif self == self.DATA:
            chain_type = 'Data'

        return chain_type

    @classmethod
    def get_name(cls, chain_type):
        name = cls.UNKNOWN

        if chain_type == 'Function':
            name = cls.FUNCTION
        elif chain_type == 'State':
            name = cls.STATE
        elif chain_type == 'Transition':
            name = cls.TRANSITION
        elif chain_type == 'Functional element':
            name = cls.FUNCTIONAL_ELEMENT
        elif chain_type == 'Data':
            name = cls.DATA

        return name


# Chain class
class Chain:
    def __init__(self, p_id='', p_name='', p_type=ChainType.UNKNOWN):
        self.id = p_id
        self.name = p_name
        self.type = p_type
        self.activated = False
        self.allocated_item_list = set()

    def set_id(self, p_id):
        self.id = p_id

    def set_name(self, p_name):
        self.name = p_name

    def set_type(self, p_type):
        self.type = p_type

    def add_allocated_item(self, p_item):
        self.allocated_item_list.add(p_item)

    def set_activation(self, p_activation):
        self.activated = p_activation