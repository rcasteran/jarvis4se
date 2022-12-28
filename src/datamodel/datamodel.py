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
    STATE = 6
    TRANSITION = 7
    ATTRIBUTE = 8
    VIEW = 9


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
        elif self == self.STATE:
            type_str = 'State'
        elif self == self.TRANSITION:
            type_str = 'Transition'
        elif self == self.ATTRIBUTE:
            type_str = 'Attribute'
        elif self == self.VIEW:
            type_str = 'View'
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


class Function:
    """Function class: Compatible with XMI"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTION, p_parent=None,
                 p_role=None, p_operand=None, p_derived=''):
        """Init Object"""
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
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

    def add_child(self, p_child):
        """Add child to child_list"""
        self.child_list.add(p_child)

    def set_input_role(self, p_role):
        """Set input role"""
        self.input_role = p_role

    def set_operand(self):
        """Set operand"""
        if isinstance(self.type, Type):
            if str(self.type.name).upper() == 'DIVIDE':
                self.operand = "denominator"
            elif str(self.type.name).upper() == 'SUBTRACT':
                self.operand = "subtractor"
            else:
                # May have further type/operand in the future
                pass    

    def set_derived(self, p_derived):
        """Set derived"""
        self.derived = p_derived


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


class State:
    """State class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.STATE, p_parent=None):
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


class Transition:
    """Transition class"""
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.TRANSITION, p_source=None,
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


class View:
    """View class"""
    def __init__(self, uid='', name='', v_type=BaseType.VIEW):
        """Init Object"""
        self.id = uid
        self.name = name
        self.type = v_type
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
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.ATTRIBUTE):
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
