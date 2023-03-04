"""@defgroup datamodel
Module for 3SE datamodel
"""

# Libraries
from enum import Enum

# Modules
from . import util


class BaseType(Enum):
    """@ingroup datamodel
    @anchor BaseType
    Basic types enumeration
    """
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
        """ Get the string representation for an enum value
        @param[in] self enum value
        @return string representation
        """
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
        """ Get the enum value for a string representation of a basic type
        @param[in] cls basic types enumeration
        @param[in] obj_type string representation of the basic type
        @return enum value
        """
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
        elif obj_type == 'State':
            enum_type = cls.STATE
        elif obj_type == 'Transition':
            enum_type = cls.TRANSITION
        elif obj_type == 'Attribute':
            enum_type = cls.ATTRIBUTE
        elif obj_type == 'View':
            enum_type = cls.VIEW
        
        return enum_type


class Function:
    """@ingroup datamodel
    @anchor Function
    Basic type representing a function
    
    A function is a transformation of incoming data to outgoing data, by means of some mechanisms,
    and subject to certain controls.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTION, p_parent=None,
                 p_role=None, p_operand=None, p_derived=''):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        function type\n
        Could be @ref BaseType .FUNCTION or a @ref Type based on @ref BaseType .FUNCTION
        
        @var parent
        parent identifier
        
        @var child_list
        child list
        
        @var input_role
        role of the function for a given data
        
        @var derived
        identifier of the function from which it is derived
        
        @var operand
        operand of the function
        """

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
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type
        self.set_operand()

    def set_parent(self, p_parent):
        """Set parent
        @param[in] self this class instance
        @param[in] p_parent identifier of the parent
        @return None
        """
        self.parent = p_parent

    def add_child(self, p_child):
        """Add child to child_list
        @param[in] self this class instance
        @param[in] p_child child
        @return None
        """
        self.child_list.add(p_child)

    def set_input_role(self, p_role):
        """Set role of the function for a given data
        @param[in] self this class instance
        @param[in] p_role role of the function
        @return None
        """
        self.input_role = p_role

    def set_operand(self):
        """Set operand of the function
        @param[in] self this class instance
        @return None
        """
        if isinstance(self.type, Type):
            if str(self.type.name).upper() == 'DIVIDE':
                self.operand = "denominator"
            elif str(self.type.name).upper() == 'SUBTRACT':
                self.operand = "subtractor"
            else:
                # May have further type/operand in the future
                pass    

    def set_derived(self, p_derived):
        """Set the identifier of the function from which it is derived
        @param[in] self this class instance
        @param[in] p_derived identifier of the function
        """
        self.derived = p_derived


class Data:
    """@ingroup datamodel
    @anchor Data
    Basic type representing a data
    
    A data is an output produced by a function and consumed by another function.
    It can be functional (information) or physical (flow of energy, particles...)
    """
    
    def __init__(self, p_id='', p_name='', p_type=BaseType.DATA):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var type
        data type\n
        Could be @ref BaseType .DATA or a @ref Type based on @ref BaseType .DATA
        
        @var predecessor_list
        data predecessor list
        """
        self.id = p_id
        self.name = p_name
        self.type = p_type
        self.predecessor_list = set()

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def add_predecessor(self, p_predecessor):
        """Add data predecessor to predecessor_list.
        @param[in] self this class instance
        @param[in] p_predecessor data predecessor
        @return None
        """
        self.predecessor_list.add(p_predecessor)


class State:
    """@ingroup datamodel
    @anchor State
    Basic type representing a state
    
    A state is an operational situation of the system characterized by its active functions.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.STATE, p_parent=None):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        state type\n
        Could be @ref BaseType .STATE or a @ref Type based on @ref BaseType .STATE
        
        @var parent
        parent identifier
        
        @var child_list
        child list
        
        @var allocated_function_list
        allocated function list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.allocated_function_list = set()

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def set_parent(self, p_parent):
        """Set parent
        @param[in] self this class instance
        @param[in] p_parent identifier of the parent
        @return None
        """
        self.parent = p_parent

    def add_child(self, p_child):
        """Add child to child_list
        @param[in] self this class instance
        @param[in] p_child child
        @return None
        """
        self.child_list.add(p_child)

    def add_allocated_function(self, p_function):
        """Add allocated function to allocated_function_list
        @param[in] self this class instance
        @param[in] p_function allocated function
        @return None
        """
        self.allocated_function_list.add(p_function)


class Transition:
    """@ingroup datamodel
    @anchor Transition
    Basic type representing a transition
    
    A transition is a change from one initial state to a final state or the same one, whose evaluation depends on the
    data produced by the active functions in the initial state.
    """
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.TRANSITION, p_source=None,
                 p_destination=None):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        transition type\n
        Could be @ref BaseType .TRANSITION or a @ref Type based on @ref BaseType .TRANSITION
        
        @var source
        initial state
        
        @var destination
        final state
        
        @var condition_list
        condition list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.source = p_source
        self.destination = p_destination
        self.condition_list = set()

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def set_source(self, p_source):
        """Set initial state
        @param[in] self this class instance
        @param[in] p_source initial state
        @return None
        """
        self.source = p_source

    def set_destination(self, p_destination):
        """Set final state
        @param[in] self this class instance
        @param[in] p_destination final state
        @return None
        """
        self.destination = p_destination

    def add_condition(self, p_condition):
        """Add condition to condition_list
        @param[in] self this class instance
        @param[in] p_condition condition associated to the transition
        @return None
        """
        self.condition_list.add(p_condition)


class FunctionalElement:
    """@ingroup datamodel
    @anchor FunctionalElement
    Basic type representing a functional element
    
    A functional element is a part of a system element responsible for carrying out some functions devolved to
    the system, by interacting with its other functional elements and/or functional enabling systems.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTIONAL_ELEMENT,
                 p_parent=None, p_derived=''):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        functional element type\n
        Could be @ref BaseType .FUNCTIONAL_ELEMENT or a @ref Type based on @ref BaseType .FUNCTIONAL_ELEMENT
        
        @var parent
        parent identifier
        
        @var child_list
        child list
        
        @var allocated_state_list
        allocated state list
        
        @var allocated_function_list
        allocated function list
        
        @var exposed_interface_list
        exposed interface list
        
        @var derived
        identifier of the functional element from which it is derived
        """
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
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def set_parent(self, p_parent):
        """Set parent
        @param[in] self this class instance
        @param[in] p_parent identifier of the parent
        @return None
        """
        self.parent = p_parent

    def add_child(self, p_child):
        """Add child to child_list
        @param[in] self this class instance
        @param[in] p_child child
        @return None
        """
        self.child_list.add(p_child)

    def add_allocated_state(self, p_state):
        """Add allocated state to add_allocated_state
        @param[in] self this class instance
        @param[in] p_state allocated state
        @return None
        """
        self.allocated_state_list.add(p_state)

    def add_allocated_function(self, p_function):
        """Add allocated function to allocated_function_list
        @param[in] self this class instance
        @param[in] p_function allocated function
        @return None
        """
        self.allocated_function_list.add(p_function)

    def add_exposed_interface(self, p_interface):
        """Add exposed interface to exposed_interface_list
        @param[in] self this class instance
        @param[in] p_interface exposed interface
        @return None
        """
        self.exposed_interface_list.add(p_interface)

    def set_derived(self, p_derived):
        """Set the identifier of the functional element from which it is derived
        @param[in] self this class instance
        @param[in] p_derived identifier of the functional element
        """
        self.derived = p_derived


class View:
    """@ingroup datamodel
    @anchor View
    View class
    """
    
    def __init__(self, uid='', name='', v_type=BaseType.VIEW):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var type
        attribute type\n
        Could be @ref BaseType .STATE or a @ref Type based on @ref BaseType .VIEW
        
        @var activated
        Indicates if the view is activated (TRUE) or not (FALSE)
        
        @var allocated_item_list
        allocated item list
        """
        self.id = uid
        self.name = name
        self.type = v_type
        self.activated = False
        self.allocated_item_list = set()

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def add_allocated_item(self, p_item):
        """Add allocated item to allocated_item_list
        @param[in] self this class instance
        @param[in] p_item allocated item
        @return None
        """
        self.allocated_item_list.add(p_item)

    def set_activation(self, p_activation):
        """Change the activation status
        @param[in] self this class instance
        @param[in] p_activation activation status
        @return None
        """
        self.activated = p_activation


class Attribute:
    """@ingroup datamodel
    @anchor Attribute
    Attribute class
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.ATTRIBUTE):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        attribute type\n
        Could be @ref BaseType .STATE or a @ref Type based on @ref BaseType .ATTRIBUTE
        
        @var described_item_list
        described item list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.described_item_list = set()

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def add_described_item(self, p_item):
        """Add described item to described_item_list
        @param[in] self this class instance
        @param[in] p_item described item
        @return None
        """
        self.described_item_list.add(p_item)


class FunctionalInterface:
    """@ingroup datamodel
    @anchor FunctionalInterface
    Basic type representing a functional interface
    
    A functional interface is a boundary across which two functional elements and/or enabling functional elements
    meet and exchange data.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTIONAL_INTERFACE,
                 p_derived=''):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        functional interface type\n
        Could be @ref BaseType .FUNCTIONAL_ELEMENT or a @ref Type based on @ref BaseType .FUNCTIONAL_ELEMENT
        
        @var allocated_data_list
        allocated data list
        
        @var derived
        identifier of the functional interface from which it is derived
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.allocated_data_list = set()
        self.derived = p_derived

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def add_allocated_data(self, p_item):
        """Add allocated data to allocated_data_list
        @param[in] self this class instance
        @param[in] p_item allocated data
        @return None
        """
        self.allocated_data_list.add(p_item)

    def set_derived(self, p_derived):
        """Set the identifier of the functional interface from which it is derived
        @param[in] self this class instance
        @param[in] p_derived identifier of the functional interface
        """
        self.derived = p_derived


class PhysicalElement:
    """@ingroup datamodel
    @anchor PhysicalElement
    Basic type representing a physical element
    
    A physical element is a physical part of a system that satisfies specified requirements.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.PHYSICAL_ELEMENT,
                 p_parent=None, p_derived=''):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        Physical element type\n
        Could be @ref BaseType .PHYSICAL_ELEMENT or a @ref Type based on @ref BaseType .PHYSICAL_ELEMENT
        
        @var parent
        parent identifier
        
        @var allocated_fun_elem_list
        allocated functional element list
        
        @var exposed_interface_list
        exposed interface list
        
        @var child_list
        child list
        
        @var derived
        identifier of the functional element from which it is derived
        """
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
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def set_parent(self, p_parent):
        """Set parent
        @param[in] self this class instance
        @param[in] p_parent identifier of the parent
        @return None
        """
        self.parent = p_parent

    def add_allocated_fun_elem(self, p_fun_elem):
        """Add allocated functional element to allocated_fun_elem_list
        @param[in] self this class instance
        @param[in] p_fun_elem allocated functional element
        @return None
        """
        self.allocated_fun_elem_list.add(p_fun_elem)

    def add_exposed_interface(self, p_interface):
        """Add exposed interface to exposed_interface_list
        @param[in] self this class instance
        @param[in] p_interface exposed interface
        @return None
        """
        self.exposed_interface_list.add(p_interface)

    def add_child(self, p_child):
        """Add child to child_list
        @param[in] self this class instance
        @param[in] p_child child
        @return None
        """
        self.child_list.add(p_child)

    def set_derived(self, p_derived):
        """Set the identifier of the physical element from which it is derived
        @param[in] self this class instance
        @param[in] p_derived identifier of the physical element
        """
        self.derived = p_derived


class PhysicalInterface:
    """@ingroup datamodel
    @anchor PhysicalInterface
    Basic type representing a physical interface
    
    A physical interface is a boundary across which two physical elements and/or enabling physical elements meet and
    exchange data.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.PHYSICAL_INTERFACE,
                 p_derived=''):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var type
        Physical interface type
        Could be @ref BaseType .PHYSICAL_ELEMENT or a @ref Type based on @ref BaseType .PHYSICAL_ELEMENT
        
        @var allocated_fun_inter_list
        allocated functional interface list
        
        @var derived
        identifier of the physical interface from which it is derived
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.allocated_fun_inter_list = set()
        self.derived = p_derived

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_type(self, p_type):
        """Set type
        @param[in] self this class instance
        @param[in] p_type type
        @return None
        """
        self.type = p_type

    def add_allocated_fun_inter(self, p_fun_inter):
        """Add allocated functional interface to allocated_fun_inter_list
        @param[in] self this class instance
        @param[in] p_fun_inter allocated functional interface
        @return None
        """
        self.allocated_fun_inter_list.add(p_fun_inter)

    def set_derived(self, p_derived):
        """Set the identifier of the physical interface from which it is derived
        @param[in] self this class instance
        @param[in] p_derived identifier of the physical interface
        """
        self.derived = p_derived


class Type:
    """@ingroup datamodel
    @anchor Type
    Type class
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_base=''):
        """
        @var id
        unique identifier
        
        @var name
        unique name
        
        @var alias
        unique alias
        
        @var base
        Type base\n
        Must be @ref BaseType value
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.base = p_base

    def set_id(self, p_id):
        """Set unique identifier
        @param[in] self this class instance
        @param[in] p_id unique identifier
        @return None
        """
        self.id = p_id

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def set_alias(self, p_alias):
        """Set unique alias
        @param[in] self this class instance
        @param[in] p_alias unique alias
        @return None
        """
        self.alias = p_alias

    def set_base(self, p_base):
        """Set basic type
        @param[in] self this class instance
        @param[in] p_base basic type
        @return None
        """
        self.base = p_base
