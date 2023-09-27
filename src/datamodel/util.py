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


def str_child_list(obj):
    """@ingroup datamodel
    @anchor str_child_list
    Return a string representation of the child list of a class instance
    @param[in] obj class instance
    @return string
    """
    if len(obj.child_list) > 1:
        rep = f'"{obj.name}" has {len(obj.child_list)} children:\n'
        for item in obj.child_list:
            rep += f' - "{item.name}" with identifier {item.id}\n'
    elif len(obj.child_list) == 1:
        rep = f'"{obj.name}" has one child:\n'
        for item in obj.child_list:
            rep += f' - "{item.name}" with identifier {item.id}\n'
    else:
        rep = f'"{obj.name}" has no child.\n'

    return rep


def str_allocated_req(obj):
    """@ingroup datamodel
    @anchor str_allocated_req
    Return a string representation of the allocated requirement list of a class instance
    @param[in] obj class instance
    @return string
    """
    if len(obj.allocated_req_list) > 1:
        rep = f'"{obj.name}" has {len(obj.allocated_req_list)} allocated requirements:\n'
        for item in obj.allocated_req_list:
            rep += f' - requirement with identifier {item}\n'
    elif len(obj.allocated_req_list) == 1:
        rep = f'"{obj.name}" has one allocated requirement:\n'
        for item in obj.allocated_req_list:
            rep += f' - requirement with identifier {item}\n'
    else:
        rep = f'"{obj.name}" has no allocated requirement.\n'

    return rep
