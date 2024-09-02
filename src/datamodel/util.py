"""@defgroup datamodel
Module for 3SE datamodel
"""

class Point:
    """@ingroup datamodel
    @anchor Point
    Basic type for diagram coordinates
    """
    def __init__(self, p_x='', p_y=''):
        """
        @var x
        X coordinate

        @var y
        Y coordinate
        """

        self.x = p_x
        self.y = p_y

    def set_x(self, p_x):
        """Set X coordinate
        @param[in] self this class instance
        @param[in] p_x X coordinate value
        @return None
        """
        self.x = p_x

    def set_y(self, p_y):
        """Set Y coordinate
        @param[in] self this class instance
        @param[in] p_y Y coordinate value
        @return None
        """
        self.y = p_y


class EndPoint:
    """@ingroup datamodel
    @anchor EndPoint
    Basic type for diagram object defined as a set of points
    """
    
    def __init__(self, p_name=''):
        """
        @var name
        unique name
        
        @var point_list
        point list
        """
        self.name = p_name
        self.point_list = set()

    def set_name(self, p_name):
        """Set unique name
        @param[in] self this class instance
        @param[in] p_name unique name
        @return None
        """
        self.name = p_name

    def add_point(self, p_point):
        """Add point to point_list
        @param[in] self this class instance
        @param[in] p_point point
        @return None
        """
        self.point_list.add(p_point)


def str_type(p_obj):
    """@ingroup datamodel
    @anchor str_type
    Return a string representation of the type of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.type == type(p_obj).__name__:
        rep = f'"{p_obj.name}" is a {p_obj.type} of class {type(p_obj).__name__} (id: {p_obj.id}).'
    else:
        rep = f'"{p_obj.name}" is a {p_obj.type.name} (id:{p_obj.id}).'

    return rep


def str_alias(p_obj):
    """@ingroup datamodel
    @anchor str_type
    Return a string representation of the alias of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.alias:
        rep = f'"{p_obj.name}" alias is {p_obj.alias}.'
    else:
        rep = f'"{p_obj.name}" has no alias.'

    return rep


def str_parent(p_obj):
    """@ingroup datamodel
    @anchor str_parent
    Return a string representation of the parent of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.parent is not None:
        rep = f'"{p_obj.name}" has "{p_obj.parent.name}" (id: {p_obj.parent.id}) as parent.'
    else:
        rep = f'"{p_obj.name}" has no parent.'

    return rep


def str_derived(p_obj):
    """@ingroup datamodel
    @anchor str_type
    Return a string representation of the object the class instance is derived from
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.derived is not None:
        rep = f'"{p_obj.name}" is derived from object (id: {p_obj.derived.id}).'
    else:
        rep = f'"{p_obj.name}" is not derived from other object.'

    return rep


def str_child_list(p_obj):
    """@ingroup datamodel
    @anchor str_child_list
    Return a string representation of the child list of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if len(p_obj.child_list) > 1:
        rep = f'"{p_obj.name}" has {len(p_obj.child_list)} children:\n'
        for item in p_obj.child_list:
            rep += f' - "{item.name}" (id: {item.id})\n'
        rep = rep[:-1]
    elif len(p_obj.child_list) == 1:
        rep = f'"{p_obj.name}" has one child:\n'
        for item in p_obj.child_list:
            rep += f' - "{item.name}" (id: {item.id})\n'
        rep = rep[:-1]
    else:
        rep = f'"{p_obj.name}" has no child.'

    return rep


def str_allocated_req(p_obj):
    """@ingroup datamodel
    @anchor str_allocated_req
    Return a string representation of the allocated requirement list of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if len(p_obj.allocated_req_list) > 1:
        rep = f'"{p_obj.name}" has {len(p_obj.allocated_req_list)} allocated requirements:\n'
        for item in p_obj.allocated_req_list:
            rep += f' - requirement (id: {item})\n'
        rep = rep[:-1]
    elif len(p_obj.allocated_req_list) == 1:
        rep = f'"{p_obj.name}" has one allocated requirement:\n'
        for item in p_obj.allocated_req_list:
            rep += f' - requirement (id: {item})\n'
        rep = rep[:-1]
    else:
        rep = f'"{p_obj.name}" has no allocated requirement.'

    return rep


def str_allocated_data(p_obj):
    """@ingroup datamodel
    @anchor str_allocated_data
    Return a string representation of the allocated data list of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if len(p_obj.allocated_data_list) > 1:
        rep = f'"{p_obj.name}" has {len(p_obj.allocated_data_list)} allocated data:\n'
        for item in p_obj.allocated_data_list:
            rep += f' - data with identifier {item}\n'
        rep = rep[:-1]
    elif len(p_obj.allocated_data_list) == 1:
        rep = f'"{p_obj.name}" has one allocated data:\n'
        for item in p_obj.allocated_data_list:
            rep += f' - data with identifier {item}\n'
        rep = rep[:-1]
    else:
        rep = f'"{p_obj.name}" has no allocated data.'

    return rep
