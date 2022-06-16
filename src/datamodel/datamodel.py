#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module containing all object's class, i.e. all objects that will be manipulated by
Systems engineers"""
# Libraries
from enum import Enum

# Modules
from . import util


class BaseType(Enum):
    """BaseType class"""
    DATA = 0
    FUNCTION = 1
    FUNCTIONAL_ELEMENT = 2
    FUNCTIONAL_INTERFACE = 3
    PHYSICAL_ELEMENT = 4
    PHYSICAL_INTERFACE = 5

    def __str__(self):
        """Get the str representation from Enum"""
        type_str = ''
        if self == self.DATA:
            type_str = 'Data'
        elif self == self.FUNCTION:
            type_str = 'Function'
        elif self == self.FUNCTIONAL_ELEMENT:
            type_str = 'Functional element'
        elif self == self.FUNCTIONAL_INTERFACE:
            type_str = 'Functional interface'
        elif self == self.PHYSICAL_ELEMENT:
            type_str = 'Physical element'
        elif self == self.PHYSICAL_INTERFACE:
            type_str = 'Physical interface'
        return type_str

    @classmethod
    def get_enum(cls, obj_type):
        """Get the Enum representation from string"""
        enum_type = None
        if obj_type == 'Data':
            enum_type = cls.DATA
        elif obj_type == 'Function':
            enum_type = cls.FUNCTION
        elif obj_type == 'Functional element':
            enum_type = cls.FUNCTIONAL_ELEMENT
        elif obj_type == 'Functional interface':
            enum_type = cls.FUNCTIONAL_INTERFACE
        elif obj_type == 'Physical element':
            enum_type = cls.PHYSICAL_ELEMENT
        elif obj_type == 'Physical interface':
            enum_type = cls.PHYSICAL_INTERFACE

        return enum_type


class FunctionType(Enum):
    """Function type: Compatible with ArKItect and XMI"""
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
        """Get the str representation from Enum"""
        function_type = 'unknown'

        if self == self.ENABLING:
            function_type = 'Enabling function'
        elif self == self.HIGH_LEVEL_FUNCTION:
            function_type = 'High level function'
        elif self == self.FUNCTION:
            function_type = 'Function'
        elif self == self.HIGH_LEVEL_SAFETY:
            function_type = 'High level safety function'
        elif self == self.SAFETY:
            function_type = 'Safety function'
        elif self == self.ADD:
            function_type = 'Add'
        elif self == self.SUBTRACT:
            function_type = 'Subtract'
        elif self == self.MULTIPLY:
            function_type = 'Multiply'
        elif self == self.DIVIDE:
            function_type = 'Divide'
        elif self == self.UNKNOWN:
            function_type = 'unknown'

        return function_type

    @classmethod
    def get_name(cls, function_type):
        """Get the Enum representation from string"""
        name = cls.UNKNOWN

        if function_type == 'Enabling function':
            name = cls.ENABLING
        elif function_type == 'High level function':
            name = cls.HIGH_LEVEL_FUNCTION
        elif function_type == 'Function':
            name = cls.FUNCTION
        elif function_type == 'High level safety function':
            name = cls.HIGH_LEVEL_SAFETY
        elif function_type == 'Safety function':
            name = cls.SAFETY
        elif function_type == 'Add':
            name = cls.ADD
        elif function_type == 'Subtract':
            name = cls.SUBTRACT
        elif function_type == 'Multiply':
            name = cls.MULTIPLY
        elif function_type == 'Divide':
            name = cls.DIVIDE

        return name

    @classmethod
    def get_parent_function_type_list(cls):
        """Returns string representation of abjects able to be parent i.e. composed"""
        base_function_type = [cls.FUNCTION, cls.HIGH_LEVEL_FUNCTION, cls.SAFETY,
                              cls.HIGH_LEVEL_SAFETY, cls.UNKNOWN]
        return [str(i) for i in base_function_type]


class Function:
    """Function class: Compatible with ArKItect and XMI"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTION, p_parent=None,
                 p_ark_obj=None, p_role=None, p_operand=None, p_derived=''):
        """Init Object"""
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
        self.derived = p_derived

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type
        self.set_operand()

    def set_parent(self, p_parent):
        """Set parent"""
        self.parent = p_parent

    def set_ark_obj(self, p_ark_obj):
        """Specific for ArKItect"""
        self.ark_obj = p_ark_obj

    def add_child(self, p_child):
        """Add child to child_list"""
        self.child_list.add(p_child)

    def add_port(self, p_port):
        """Specific for XMI"""
        self.port_list.add(p_port)

    def set_input_role(self, p_role):
        """Set input role"""
        self.input_role = p_role

    def set_operand(self):
        """Set operand"""
        if self.type == FunctionType.DIVIDE:
            self.operand = "denominator"
        elif self.type == FunctionType.SUBTRACT:
            self.operand = "subtractor"
        else:
            # May have further type/operand in the future
            pass

    def set_derived(self, p_derived):
        """Set derived"""
        self.derived = p_derived


class SystemElementType(Enum):
    """System element type: Compatible with LT SPICE"""
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
        """Get the str representation from Enum"""
        sys_elem_type = 'unknown'

        if self == self.HIGH_LEVEL:
            sys_elem_type = 'High level system element'
        elif self == self.SYSTEM:
            sys_elem_type = 'System element'
        elif self == self.RESISTOR:
            sys_elem_type = 'res'
        elif self == self.CAPACITOR:
            sys_elem_type = 'cap'
        elif self == self.ZENER:
            sys_elem_type = 'zener'
        elif self == self.NPN:
            sys_elem_type = 'npn'
        elif self == self.PNP:
            sys_elem_type = 'pnp'
        elif self == self.DIODE:
            sys_elem_type = 'diode'
        elif self == self.VOLTAGE:
            sys_elem_type = 'voltage'
        elif self == self.LED:
            sys_elem_type = 'LED'

        return sys_elem_type

    @classmethod
    def get_name(cls, sys_elem_type):
        """Get the Enum representation from string"""
        name = cls.UNKNOWN

        if sys_elem_type == 'High level system element':
            name = cls.HIGH_LEVEL
        elif sys_elem_type == 'System element':
            name = cls.SYSTEM
        # LTSPICE compatible
        elif sys_elem_type == 'res':
            name = cls.RESISTOR
        # LTSPICE compatible
        elif sys_elem_type == 'cap':
            name = cls.CAPACITOR
        # LTSPICE compatible
        elif sys_elem_type == 'zener':
            name = cls.ZENER
        # LTSPICE compatible
        elif sys_elem_type == 'npn':
            name = cls.NPN
        # LTSPICE compatible
        elif sys_elem_type == 'pnp':
            name = cls.PNP
        # LTSPICE compatible
        elif sys_elem_type == 'diode':
            name = cls.DIODE
        # LTSPICE compatible
        elif sys_elem_type == 'voltage':
            name = cls.VOLTAGE
        # LTSPICE compatible
        elif sys_elem_type == 'LED':
            name = cls.LED

        return name


class Element:
    """Element class : Compatible with LTSPICE and Depends on EndPoint class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=SystemElementType.UNKNOWN,
                 p_parent=None, p_ark_obj=None, p_role=None, p_spice_rotation='',
                 p_spice_prefix='', p_spice_model=''):
        """Init Object"""
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
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def set_parent(self, p_parent):
        """Set parent"""
        self.parent = p_parent

    def set_ark_obj(self, p_ark_obj):
        """Specific for ArKItect"""
        self.ark_obj = p_ark_obj

    def add_child(self, p_child):
        """Add child to child_list"""
        self.child_list.add(p_child)

    def add_port(self, p_port):
        """Specific for XMI"""
        self.port_list.add(p_port)

    def set_input_role(self, p_role):
        """Set input role"""
        self.input_role = p_role

    def add_spice_window(self, p_window):
        """Specific for LTSPICE"""
        self.spice_window_list.add(p_window)

    def set_spice_rotation(self, p_ref):
        """Specific for LTSPICE"""
        self.spice_rotation = p_ref

    def add_point(self, p_point):
        """Specific for LTSPICE"""
        self.point_list.append(p_point)

    def add_constraint(self, p_constraint):
        """Specific for LTSPICE"""
        self.constraint_list.add(p_constraint)

    def set_spice_prefix(self, p_prefix):
        """Specific for LTSPICE"""
        self.spice_prefix = p_prefix

    def set_spice_model(self, p_model):
        """Specific for LTSPICE"""
        self.spice_model = p_model

    def determine_relative_point(self, p_point):
        """Specific for LTSPICE"""
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


class Interface:
    """Interface class: Compatible with LTSPICE and Depends on Point class"""
    def __init__(self, p_name=''):
        """Init Object"""
        self.name = p_name
        self.point_list = []
        self.provider_list = set()
        self.user_list = set()

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def add_point(self, p_point):
        """Add point"""
        self.point_list.append(p_point)

    def set_provider_user_list(self, p_element):
        """Set provider user list"""
        for point in p_element.point_list:
            if abs(point.x - self.point_list[0].x) == 0 \
                    and abs(point.y - self.point_list[0].y) == 0:
                self.provider_list.add(p_element)
            elif abs(point.x - self.point_list[1].x) == 0 \
                    and abs(point.y - self.point_list[1].y) == 0:
                self.user_list.add(p_element)
            # Else do nothing


class DataType(Enum):
    """Data type class"""
    UNKNOWN = 0
    FLOW = 1
    SAFETY = 2

    def __str__(self):
        """Get the str representation from Enum"""
        data_type = 'unknown'
        if self == self.FLOW:
            data_type = 'Flow'
        elif self == self.SAFETY:
            data_type = 'Safety flow'

        return data_type

    @classmethod
    def get_name(cls, data_type):
        """Get the Enum representation from string"""
        name = cls.UNKNOWN

        if data_type == 'Flow':
            name = cls.FLOW
        if data_type == 'Safety flow':
            name = cls.SAFETY
        return name


class Data:
    """Data class"""
    def __init__(self, p_id='', p_name='', p_type=BaseType.DATA):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.type = p_type
        self.predecessor_list = set()

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def add_predecessor(self, p_predecessor):
        """Add predecessor to predecessor list"""
        self.predecessor_list.add(p_predecessor)


class StateType(Enum):
    """State type"""
    UNKNOWN = 0
    STATE = 1
    HIGH_LEVEL_STATE = 2
    ENTRY = 3
    EXIT = 4

    def __str__(self):
        """Get the str representation from Enum"""
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
        """Get the Enum representation from string"""
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


class State:
    """State class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=StateType.UNKNOWN, p_parent=None):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.allocated_function_list = set()

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def set_parent(self, p_parent):
        """Set parent"""
        self.parent = p_parent

    def add_child(self, p_child):
        """Add child to child_list"""
        self.child_list.add(p_child)

    def add_allocated_function(self, p_function):
        """Add allocated function to allocated_function_list"""
        self.allocated_function_list.add(p_function)


class TransitionType(Enum):
    """Transition type"""
    UNKNOWN = 0
    DEFAULT = 1

    def __str__(self):
        """Get the str representation from Enum"""
        state_type = 'unknown'
        if self == self.DEFAULT:
            state_type = 'Default'

        return state_type

    @classmethod
    def get_name(cls, state_type):
        """Get the Enum representation from string"""
        name = cls.UNKNOWN
        if state_type == 'Default':
            name = cls.DEFAULT

        return name


class Transition:
    """Transition class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=StateType.UNKNOWN, p_source=None,
                 p_destination=None):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.source = p_source
        self.destination = p_destination
        self.condition_list = set()

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def set_source(self, p_source):
        """Set source"""
        self.source = p_source

    def set_destination(self, p_destination):
        """Set destination"""
        self.destination = p_destination

    def add_condition(self, p_condition):
        """Add condition to condition_list"""
        self.condition_list.add(p_condition)


class FunctionalElementType(Enum):
    """FunctionalElement type"""
    UNKNOWN = 0
    ENABLING = 1
    FUNCTIONAL_ELEMENT = 2
    HIGH_LEVEL_FUNCTIONAL_ELEMENT = 3

    def __str__(self):
        """Get the str representation from Enum"""
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
        """Get the Enum representation from string"""
        name = cls.UNKNOWN
        if functional_element_type == 'Enabling functional element':
            name = cls.ENABLING
        elif functional_element_type == 'Functional element':
            name = cls.FUNCTIONAL_ELEMENT
        elif functional_element_type == 'High level functional element':
            name = cls.HIGH_LEVEL_FUNCTIONAL_ELEMENT
        return name


class FunctionalElement:
    """FunctionalElement class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTIONAL_ELEMENT,
                 p_parent=None, p_derived=''):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.allocated_state_list = set()
        self.allocated_function_list = set()
        self.exposed_interface_list = set()
        self.derived = p_derived

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def set_parent(self, p_parent):
        """Set parent"""
        self.parent = p_parent

    def add_child(self, p_child):
        """Add child to child_list"""
        self.child_list.add(p_child)

    def add_allocated_state(self, p_state):
        """Add allocated state to allocated_state_list"""
        self.allocated_state_list.add(p_state)

    def add_allocated_function(self, p_function):
        """Add allocated function to allocated_function_list"""
        self.allocated_function_list.add(p_function)

    def add_exposed_interface(self, p_interface):
        """Add interface to exposed_interface_list"""
        self.exposed_interface_list.add(p_interface)

    def set_derived(self, p_derived):
        """Set derived"""
        self.derived = p_derived


class ViewType(Enum):
    """View type"""
    UNKNOWN = 0
    FUNCTION = 1
    STATE = 2
    TRANSITION = 3
    FUNCTIONAL_ELEMENT = 4
    DATA = 5

    def __str__(self):
        """Get the str representation from Enum"""
        view_type = 'unknown'

        if self == self.FUNCTION:
            view_type = 'Function'
        elif self == self.STATE:
            view_type = 'State'
        elif self == self.TRANSITION:
            view_type = 'Transition'
        elif self == self.FUNCTIONAL_ELEMENT:
            view_type = 'Functional element'
        elif self == self.DATA:
            view_type = 'Data'

        return view_type

    @classmethod
    def get_name(cls, view_type):
        """Get the Enum representation from string"""
        name = cls.UNKNOWN

        if view_type == 'Function':
            name = cls.FUNCTION
        elif view_type == 'State':
            name = cls.STATE
        elif view_type == 'Transition':
            name = cls.TRANSITION
        elif view_type == 'Functional element':
            name = cls.FUNCTIONAL_ELEMENT
        elif view_type == 'Data':
            name = cls.DATA

        return name


class View:
    """View class"""
    def __init__(self, p_id='', p_name='', p_type=ViewType.UNKNOWN):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.type = p_type
        self.activated = False
        self.allocated_item_list = set()

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def add_allocated_item(self, p_item):
        """Add allocated item to allocated_item_list"""
        self.allocated_item_list.add(p_item)

    def set_activation(self, p_activation):
        """Set activation"""
        self.activated = p_activation


class Attribute:
    """Attribute class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type='unknown'):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.described_item_list = set()

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def add_described_item(self, p_item):
        """Add described item to described_item_list"""
        self.described_item_list.add(p_item)


class FunctionalInterface:
    """Functional Interface class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTIONAL_INTERFACE,
                 p_derived=''):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.allocated_data_list = set()
        self.derived = p_derived

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def add_allocated_data(self, p_item):
        """Add allocated data to allocated_data_list"""
        self.allocated_data_list.add(p_item)

    def set_derived(self, p_derived):
        """Set derived"""
        self.derived = p_derived


class PhysicalElement:
    """Physical Element class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.PHYSICAL_ELEMENT,
                 p_parent=None, p_derived=''):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.allocated_fun_elem_list = set()
        self.exposed_interface_list = set()
        self.child_list = set()
        self.derived = p_derived

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def set_parent(self, p_parent):
        """Set parent"""
        self.parent = p_parent

    def add_allocated_fun_elem(self, p_fun_elem):
        """Add allocated fun_elem to allocated_fun_elem_list"""
        self.allocated_fun_elem_list.add(p_fun_elem)

    def add_exposed_interface(self, p_interface):
        """Add interface to exposed_interface_list"""
        self.exposed_interface_list.add(p_interface)

    def add_child(self, p_child):
        """Add child to child_list"""
        self.child_list.add(p_child)

    def set_derived(self, p_derived):
        """Set derived"""
        self.derived = p_derived


class PhysicalInterface:
    """PhysicalInterface class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.PHYSICAL_INTERFACE,
                 p_derived=''):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.allocated_fun_inter_list = set()
        self.derived = p_derived

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type"""
        self.type = p_type

    def add_allocated_fun_inter(self, p_fun_inter):
        """Add allocated fun_inter to allocated_fun_inter_list"""
        self.allocated_fun_inter_list.add(p_fun_inter)

    def set_derived(self, p_derived):
        """Set derived"""
        self.derived = p_derived


class Type:
    """Type class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_base=''):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.base = p_base

    def set_id(self, p_id):
        """Set id"""
        self.id = p_id

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def set_alias(self, p_alias):
        """Set alias"""
        self.alias = p_alias

    def set_base(self, p_base):
        """Set base"""
        self.base = p_base
