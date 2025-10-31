"""@defgroup datamodel
Module for 3SE datamodel
"""

# Libraries
from enum import Enum

# Modules
from . import util

# Constants
REQUIREMENT_PATTERN = r"([^. |\n][^.|\n]*) shall (([^.]|\n)*)"
GOAL_PATTERN = r"([^. |\n][^.|\n]*) I want (.*?) to ([^.|\n]*)"
DIRECTION_PATTERN = r"([^. |\n][^.|\n]*) from (.*?) to ([^.|\n]*)"

# Type definition


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
    REQUIREMENT = 8
    GOAL = 9
    ACTIVITY = 10
    INFORMATION = 11
    ATTRIBUTE = 12
    VIEW = 13

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
        elif self == self.ACTIVITY:
            type_str = 'Activity'
        elif self == self.INFORMATION:
            type_str = 'Information'
        elif self == self.ATTRIBUTE:
            type_str = 'Attribute'
        elif self == self.VIEW:
            type_str = 'View'
        elif self == self.REQUIREMENT:
            type_str = 'Requirement'
        elif self == self.GOAL:
            type_str = 'Goal'

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
        elif obj_type == 'Activity':
            enum_type = cls.ACTIVITY
        elif obj_type == 'Information':
            enum_type = cls.INFORMATION
        elif obj_type == 'Attribute':
            enum_type = cls.ATTRIBUTE
        elif obj_type == 'View':
            enum_type = cls.VIEW
        elif obj_type == 'Requirement':
            enum_type = cls.REQUIREMENT
        elif obj_type == 'Goal':
            enum_type = cls.GOAL

        return enum_type


class Activity:
    """@ingroup datamodel
    @anchor Activity
    Basic type representing an activity

    An activity is a defined body of work to be performed to achieve a goal, including its required incoming and
    outgoing exchanges.
    """

    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.ACTIVITY):
        """
        @var id
        unique identifier

        @var name
        unique name

        @var alias
        unique alias

        @var type
        activity type\n
        Could be @ref BaseType .ACTIVITY or a @ref Type based on @ref BaseType .ACTIVITY

        @var allocated_goal_list
        allocated goal list
        """

        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.allocated_goal_list = set()

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

    def add_allocated_goal(self, p_goal):
        """Add allocated goal to allocated_goal_list
        @param[in] self this class instance
        @param[in] p_goal allocated goal
        @return None
        """
        self.allocated_goal_list.add(p_goal)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        # Activity cannot be derived
        # Activity has no parent
        # Activity has no child
        # Activity has no allocated requirement
        # Activity has no allocated data
        # Activity has no allocated activity
        # Activity has no allocated information
        rep += util.str_allocated_goal(self) + '\n'

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                # Activity cannot be derived
                # Activity has no parent
                # Activity has no child
                # Activity has no allocated requirement
                # Activity has no allocated data
                # Activity has no allocated activity
                # Activity has no allocated information
                **util.info_allocated_goal(self)
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_PARENT,
                    util.INFO_KEY_GOAL_LIST
                    ]


class Function:
    """@ingroup datamodel
    @anchor Function
    Basic type representing a function
    
    A function is a transformation of incoming data to outgoing data, by means of some mechanisms,
    and subject to certain controls.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTION, p_parent=None,
                 p_role=None, p_operand=None, p_derived=None):
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

        @var allocated_req_list
        allocated requirement list

        @var allocated_activity_list
        allocated requirement list
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
        self.allocated_req_list = set()
        self.allocated_activity_list = set()

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def add_allocated_activity(self, p_activity):
        """Add allocated activity to allocated_activity_list
        @param[in] self this class instance
        @param[in] p_activity allocated activity
        @return None
        """
        self.allocated_activity_list.add(p_activity)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        rep += util.str_derived(self) + '\n'
        rep += util.str_parent(self) + '\n'
        rep += util.str_child_list(self) + '\n'
        rep += util.str_allocated_req(self) + '\n'
        # Function has no allocated data
        rep += util.str_allocated_activity(self)
        # Function has no allocated information
        # Function has no allocated goal
        # No display of input_role and operand

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                **util.info_derived(self),
                **util.info_parent(self),
                **util.info_child_list(self),
                **util.info_allocated_req(self),
                # Function has no allocated data
                **util.info_allocated_activity(self)
                # Function has no allocated information
                # Function has no allocated goal
                # No display of input_role and operand
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_DERIVED,
                    util.INFO_KEY_PARENT,
                    util.INFO_KEY_CHILD_LIST,
                    util.INFO_KEY_REQUIREMENT_LIST,
                    util.INFO_KEY_ACTIVITY_LIST
                    ]


class Information:
    """@ingroup datamodel
    @anchor Information
    Basic type representing an Information

    An information is an output produced by an activity and consumed by another activity.
    It can be functional (representation of knowledge element acquired by human beings) or
    physical (representation of a flow which follows the physical laws of nature - flow of energy, particles...)
    """

    def __init__(self, p_id='', p_name='', p_type=BaseType.INFORMATION):
        """
        @var id
        unique identifier

        @var name
        unique name

        @var type
        data type\n
        Could be @ref BaseType .DATA or a @ref Type based on @ref BaseType .INFORMATION

        @var predecessor_list
        data predecessor list

        @var allocated_req_list
        allocated requirement list
        """
        self.id = p_id
        self.name = p_name
        self.type = p_type
        self.predecessor_list = set()
        self.allocated_req_list = set()

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        # Information has no alias
        # Information cannot be specialized
        # Information has no parent
        # Information has no children
        rep += util.str_allocated_req(self)
        # Information has no allocated data
        # Information has no allocated activity
        # Information has no allocated information
        # Information has no allocated goal
        # No display of predecessor list

        return rep

    def info(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        return {**util.info_type(self),
                # Information has no alias
                # Information cannot be specialized
                # Information has no parent
                # Information has no children
                **util.info_allocated_req(self)
                # Information has no allocated data
                # Information has no allocated activity
                # Information has no allocated information
                # Information has no allocated goal
                # No display of predecessor list
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_REQUIREMENT_LIST
                    ]


class Data:
    """@ingroup datamodel
    @anchor Data
    Basic type representing a data
    
    A data is an output produced by a function and consumed by another function.
    It can be functional (participating in the definition of a functional information) or
    physical (participating in the definition of a physical information)
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

        @var allocated_req_list
        allocated requirement list

        @var allocated_information_list
        allocated information list
        """
        self.id = p_id
        self.name = p_name
        self.type = p_type
        self.predecessor_list = set()
        self.allocated_info_list = set()
        self.allocated_req_list = set()

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

    def add_allocated_information(self, p_information):
        """Add allocated information to allocated_info_list
        @param[in] self this class instance
        @param[in] p_information allocated information
        @return None
        """
        self.allocated_info_list.add(p_information)

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        # Data has no alias
        # Data cannot be specialized
        # Data has no parent
        # Data has no children
        rep += util.str_allocated_req(self) + '\n'
        # Data has no allocated data
        # Data has no allocated activity
        rep += util.str_allocated_information(self)
        # Data has no allocated goal
        # No display of predecessor list

        return rep

    def info(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        return {**util.info_type(self),
                # Data has no alias
                # Data cannot be specialized
                # Data has no parent
                # Data has no children
                **util.info_allocated_req(self),
                # Data has no allocated data
                # Data has no allocated activity
                **util.info_allocated_information(self)
                # Data has no allocated goal
                # No display of predecessor list
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_REQUIREMENT_LIST,
                    util.INFO_KEY_INFORMATION_LIST
                    ]


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

        @var allocated_req_list
        allocated requirement list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.allocated_function_list = set()
        self.allocated_req_list = set()

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

    def remove_allocated_function(self, p_function):
        """Remove allocated function from allocated_function_list
        @param[in] self this class instance
        @param[in] p_function allocated function
        @return None
        """
        self.allocated_function_list.remove(p_function)

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        # State cannot be specialized
        rep += util.str_parent(self) + '\n'
        rep += util.str_child_list(self) + '\n'
        rep += util.str_allocated_req(self)
        # State has no allocated data
        # State has no allocated activity
        # State has no allocated information
        # State has no allocated goal
        # No display of allocated function list

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.str_type(self),
                **util.str_alias(self),
                # State cannot be specialized
                **util.str_parent(self),
                **util.str_child_list(self),
                **util.str_allocated_req(self)
                # State has no allocated data
                # State has no allocated activity
                # State has no allocated information
                # State has no allocated goal
                # No display of allocated function list
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_PARENT,
                    util.INFO_KEY_CHILD_LIST,
                    util.INFO_KEY_REQUIREMENT_LIST
                    ]


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

        @var allocated_req_list
        allocated requirement list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.source = p_source
        self.destination = p_destination
        self.condition_list = set()
        self.allocated_req_list = set()

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        # Transition cannot be specialized
        # Transition has no parent
        # Transition has no children
        rep += util.str_allocated_req(self)
        # Transition has no allocated data
        # Transition has no allocated activity
        # Transition has no allocated information
        # Transition has no allocated goal
        # No display of source, destination and condition_list

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                # Transition cannot be specialized
                # Transition has no parent
                # Transition has no children
                **util.info_allocated_req(self)
                # Transition has no allocated data
                # Transition has no allocated activity
                # Transition has no allocated goal
                # No display of source, destination and condition_list
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_REQUIREMENT_LIST
                    ]


class FunctionalElement:
    """@ingroup datamodel
    @anchor FunctionalElement
    Basic type representing a functional element
    
    A functional element is a part of a system element responsible for carrying out some functions devolved to
    the system, by interacting with its other functional elements and/or functional enabling systems.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTIONAL_ELEMENT,
                 p_parent=None, p_derived=None):
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

        @var allocated_req_list
        allocated requirement list
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
        self.allocated_req_list = set()

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
        """Add allocated state to allocated_state_list
        @param[in] self this class instance
        @param[in] p_state allocated state
        @return None
        """
        self.allocated_state_list.add(p_state)

    def remove_allocated_state(self, p_state):
        """Remove allocated state from allocated_state_list
        @param[in] self this class instance
        @param[in] p_state allocated state
        @return None
        """
        self.allocated_state_list.remove(p_state)

    def add_allocated_function(self, p_function):
        """Add allocated function to allocated_function_list
        @param[in] self this class instance
        @param[in] p_function allocated function
        @return None
        """
        self.allocated_function_list.add(p_function)

    def remove_allocated_function(self, p_function):
        """Remove allocated function from allocated_function_list
        @param[in] self this class instance
        @param[in] p_function allocated function
        @return None
        """
        self.allocated_function_list.remove(p_function)

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        rep += util.str_derived(self) + '\n'
        rep += util.str_parent(self) + '\n'
        rep += util.str_child_list(self) + '\n'
        rep += util.str_allocated_req(self)
        # Functional element has no allocated data
        # Functional element has no allocated activity
        # Functional element has no allocated information
        # Functional element has no allocated goal
        # No display of allocated function, allocated state and exposed interface

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                **util.info_derived(self),
                **util.info_parent(self),
                **util.info_child_list(self),
                **util.info_allocated_req(self)
                # Functional element has no allocated data
                # Functional element has no allocated activity
                # Functional element has no allocated information
                # Functional element has no allocated goal
                # No display of allocated function, allocated state and exposed interface
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_DERIVED,
                    util.INFO_KEY_PARENT,
                    util.INFO_KEY_CHILD_LIST,
                    util.INFO_KEY_REQUIREMENT_LIST
                    ]


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
        view type\n
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
        self.allocated_item_filter_dict = {}

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

    def add_allocated_item_filter(self, p_item, p_consumer, p_producer):
        """Add allocated item filter to add_allocated_item_filter
        @param[in] self this class instance
        @param[in] p_item allocated item
        @param[in] p_consumer allocated item consumer
        @param[in] p_producer allocated item producer
        @return None
        """
        self.allocated_item_filter_dict[p_item] = [p_consumer, p_producer]

    def set_activation(self, p_activation):
        """Change the activation status
        @param[in] self this class instance
        @param[in] p_activation activation status
        @return None
        """
        self.activated = p_activation

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self)
        # View has no alias
        # View cannot be specialized
        # View has no parent
        # View has no children
        # View has no allocated requirement
        # View has no allocated data
        # View has no allocated activity
        # View has no allocated information
        # View has no allocated goal
        # No display of allocated item list

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self)
                # View has no alias
                # View cannot be specialized
                # View has no parent
                # View has no children
                # View has no allocated requirement
                # View has no allocated data
                # View has no allocated activity
                # View has no allocated information
                # View has no allocated goal
                # No display of allocated item list
                }, [util.INFO_KEY_TYPE
                    ]


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

        @var allocated_req_list
        allocated requirement list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.described_item_list = set()
        self.allocated_req_list = set()

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        # Attribute cannot be specialized
        # Attribute has no parent
        # Attribute has no children
        rep += util.str_allocated_req(self)
        # Attribute has no allocated data
        # Attribute has no allocated activity
        # Attribute has no allocated information
        # Attribute has no allocated goal
        # No display of described item list

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                # Attribute cannot be specialized
                # Attribute has no parent
                # Attribute has no children
                **util.info_allocated_req(self)
                # Attribute has no allocated data
                # Attribute has no allocated activity
                # Attribute has no allocated information
                # Attribute has no allocated goal
                # No display of described item list
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_REQUIREMENT_LIST
                    ]


class FunctionalInterface:
    """@ingroup datamodel
    @anchor FunctionalInterface
    Basic type representing a functional interface
    
    A functional interface is a boundary across which two functional elements and/or enabling functional elements
    meet and exchange data.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.FUNCTIONAL_INTERFACE,
                 p_derived=None):
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

        @var allocated_req_list
        allocated requirement list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.allocated_data_list = set()
        self.derived = p_derived
        self.allocated_req_list = set()

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        rep += util.str_derived(self) + '\n'
        # Functional interface has no parent
        # Functional interface has no children
        rep += util.str_allocated_req(self) + '\n'
        rep += util.str_allocated_data(self)
        # Functional interface has no allocated activity
        # Functional interface has no allocated information
        # Functional interface has no allocated goal

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                **util.info_derived(self),
                # Functional interface has no parent
                # Functional interface has no children
                **util.info_allocated_req(self),
                **util.info_allocated_data(self)
                # Functional interface has no allocated activity
                # Functional interface has no allocated information
                # Functional interface has no allocated goal
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_DERIVED,
                    util.INFO_KEY_REQUIREMENT_LIST,
                    util.INFO_KEY_DATA_LIST
                    ]


class PhysicalElement:
    """@ingroup datamodel
    @anchor PhysicalElement
    Basic type representing a physical element
    
    A physical element is a physical part of a system that satisfies specified requirements.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.PHYSICAL_ELEMENT,
                 p_parent=None, p_derived=None):
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

        @var allocated_activity_list
        allocated activity list

        @var allocated_fun_elem_list
        allocated functional element list
        
        @var exposed_interface_list
        exposed interface list
        
        @var child_list
        child list
        
        @var derived
        identifier of the functional element from which it is derived

        @var allocated_req_list
        allocated requirement list

        @var allocated_goal_list
        allocated goal list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.allocated_activity_list = set()
        self.allocated_fun_elem_list = set()
        self.exposed_interface_list = set()
        self.child_list = set()
        self.derived = p_derived
        self.allocated_req_list = set()
        self.allocated_goal_list = set()

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

    def add_allocated_activity(self, p_activity):
        """Add allocated activity to allocated_activity_list
        @param[in] self this class instance
        @param[in] p_activity allocated activity
        @return None
        """
        self.allocated_activity_list.add(p_activity)

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def add_allocated_goal(self, p_goal):
        """Add allocated goal to allocated_goal_list
        @param[in] self this class instance
        @param[in] p_goal allocated goal
        @return None
        """
        self.allocated_goal_list.add(p_goal)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        rep += util.str_derived(self) + '\n'
        rep += util.str_parent(self) + '\n'
        rep += util.str_child_list(self) + '\n'
        rep += util.str_allocated_req(self) + '\n'
        # Physical element has no allocated data
        rep += util.str_allocated_activity(self)
        # Physical element has no allocated information
        rep += util.str_allocated_goal(self) + '\n'
        # No display of allocated activity, allocated functional element list and exposed interface list

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                **util.info_derived(self),
                **util.info_parent(self),
                **util.info_child_list(self),
                **util.info_allocated_req(self),
                # Physical element has no allocated data
                **util.info_allocated_activity(self),
                # Physical element has no allocated information
                **util.info_allocated_goal(self)
                # No display of allocated activity, allocated functional element list and exposed interface list
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_DERIVED,
                    util.INFO_KEY_PARENT,
                    util.INFO_KEY_CHILD_LIST,
                    util.INFO_KEY_REQUIREMENT_LIST,
                    util.INFO_KEY_ACTIVITY_LIST,
                    util.INFO_KEY_GOAL_LIST
                    ]


class PhysicalInterface:
    """@ingroup datamodel
    @anchor PhysicalInterface
    Basic type representing a physical interface
    
    A physical interface is a boundary across which two physical elements and/or enabling physical elements meet and
    exchange data.
    """
    
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.PHYSICAL_INTERFACE,
                 p_derived=None):
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

        @var allocated_req_list
        allocated requirement list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.allocated_fun_inter_list = set()
        self.derived = p_derived
        self.allocated_req_list = set()

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        rep += util.str_derived(self) + '\n'
        # Physical interface has no parent
        # Physical interface has no children
        rep += util.str_allocated_req(self)
        # Physical interface has no allocated data
        # Physical interface has no allocated activity
        # Physical interface has no allocated information
        # Physical interface has no allocated goal
        # No display of allocated functional interface list

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                **util.info_derived(self),
                # Physical interface has no parent
                # Physical interface has no children
                **util.info_allocated_req(self)
                # Physical interface has no allocated data
                # Physical interface has no allocated activity
                # Physical interface has no allocated information
                # Physical interface has no allocated goal
                # No display of allocated functional interface list
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_DERIVED,
                    util.INFO_KEY_REQUIREMENT_LIST
                    ]


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

        @var allocated_req_list
        allocated requirement list
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.base = p_base
        self.allocated_req_list = set()

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

    def add_allocated_requirement(self, p_req):
        """Add allocated requirement to allocated_req_list
        @param[in] self this class instance
        @param[in] p_req allocated requirement
        @return None
        """
        self.allocated_req_list.add(p_req)

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = f'"{self.name}" is a type (id: {self.id}).\n'
        rep += util.str_alias(self) + '\n'
        # Type cannot be specialized
        # Type has no parent
        # Type has no children
        rep += util.str_allocated_req(self)
        # Type has no allocated data
        # Type has no allocated activity
        # Type has no allocated information
        # Type has no allocated goal
        # No display of base type

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_alias(self),
                # Type cannot be specialized
                # Type has no parent
                # Type has no children
                **util.info_allocated_req(self)
                # Type has no allocated data
                # Type has no allocated activity
                # Type has no allocated information
                # Type has no allocated goal
                # No display of base type
                }, [util.INFO_KEY_ALIAS,
                    util.INFO_KEY_REQUIREMENT_LIST
                    ]


class Requirement:
    """@ingroup datamodel
    @anchor Requirement
    Basic type representing a requirement

    1. A condition or capability needed by a user to achieve a goal.
    2. A condition or capability that must be met or possessed by a system or system element to satisfy an agreement,
    standard, specification, or other formally imposed documents.
    3. A documented representation of a condition or capability as in (1) or (2)
    """

    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.REQUIREMENT,
                 p_parent=None):
        """
        @var id
        unique identifier

        @var name
        unique name

        @var alias
        unique alias

        @var type
        requirement type\n
        Could be @ref BaseType .REQUIREMENT or a @ref Type based on @ref BaseType .REQUIREMENT

        @var parent
        parent identifier

        @var child_list
        child list

        @var text
        requirement text
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.text = ""

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

    def set_text(self, p_text):
        """Set text
        @param[in] self this class instance
        @param[in] p_text requirement text
        @return None
        """
        self.text = p_text

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        # Requirement cannot be specialized
        rep += util.str_parent(self) + '\n'
        rep += util.str_child_list(self) + '\n'
        # Requirement has no allocated requirement
        # Requirement has no allocated data
        # Requirement has no allocated activity
        # Requirement has no allocated information
        # Requirement has no allocated goal
        rep += util.str_text(self)

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                # Requirement cannot be specialized
                **util.info_parent(self),
                **util.info_child_list(self),
                # Requirement has no allocated requirement
                # Requirement has no allocated data
                # Requirement has no allocated activity
                # Requirement has no allocated information
                # Requirement has no allocated goal
                **util.info_text(self)
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_PARENT,
                    util.INFO_KEY_CHILD_LIST,
                    util.INFO_KEY_TEXT
                    ]


class Goal:
    """@ingroup datamodel
    @anchor Goal
    Basic type representing a goal

    Stakeholder’s description of an characteristic (property, behavior…) of a system
    """
    def __init__(self, p_id='', p_name='', p_alias='', p_type=BaseType.GOAL,
                 p_parent=None):
        """
        @var id
        unique identifier

        @var name
        unique name

        @var alias
        unique alias

        @var type
        Goal type\n
        Could be @ref BaseType .GOAL or a @ref Type based on @ref BaseType .GOAL

        @var parent
        parent identifier

        @var child_list
        child list

        @var text
        goal text
        """
        self.id = p_id
        self.name = p_name
        self.alias = p_alias
        self.type = p_type
        self.parent = p_parent
        self.child_list = set()
        self.text = ""

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

    def set_text(self, p_text):
        """Set text
        @param[in] self this class instance
        @param[in] p_text requirement text
        @return None
        """
        self.text = p_text

    def __str__(self):
        """Return a string representation of the class instance
        @param[in] self this class instance
        @return string
        """
        rep = util.str_type(self) + '\n'
        rep += util.str_alias(self) + '\n'
        # Goal cannot be specialized
        rep += util.str_parent(self) + '\n'
        rep += util.str_child_list(self) + '\n'
        # Goal has no allocated requirement
        # Goal has no allocated data
        # Goal has no allocated activity
        # Goal has no allocated information
        # Goal has no allocated goal
        rep += util.str_text(self)

        return rep

    def info(self):
        """Return a dict representation of the class instance
        @param[in] self this class instance
        @return dict
        """
        return {**util.info_type(self),
                **util.info_alias(self),
                # Goal cannot be specialized
                **util.info_parent(self),
                **util.info_child_list(self),
                # Goal has no allocated requirement
                # Goal has no allocated data
                # Goal has no allocated activity
                # Goal has no allocated information
                # Goal has no allocated goal
                **util.info_text(self)
                }, [util.INFO_KEY_TYPE,
                    util.INFO_KEY_ALIAS,
                    util.INFO_KEY_PARENT,
                    util.INFO_KEY_CHILD_LIST,
                    util.INFO_KEY_TEXT
                    ]


# Global variables definition
TypeWithChildList = (Function, State, FunctionalElement, PhysicalElement, Requirement, Goal)
TypeWithChildListFunctionIndex = 0
TypeWithChildListStateIndex = 1
TypeWithChildListFunctionalElementIndex = 2
TypeWithChildListPhysicalElementIndex = 3
TypeWithChildListRequirementIndex = 4
TypeWithChildListGoalIndex = 5
TypeWithAllocatedReqList = (Function, Information, Data, State, Transition, FunctionalElement, Attribute,
                            FunctionalInterface, PhysicalElement, PhysicalInterface, Type)
EntryStateLabel = 'entry'
ExitStateLabel = 'exit'
DesignAttributeLabel = 'design'
InitialValueAttributeLabel = "initial value"
ObjectTextPropertyLabel = 'text'
ObjectTypePropertyLabel = 'type'
ObjectAliasPropertyLabel = 'alias'
ObjectSourcePropertyLabel = 'source'
ObjectDestinationPropertyLabel = 'destination'
