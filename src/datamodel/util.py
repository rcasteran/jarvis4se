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

