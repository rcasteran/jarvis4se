# Point class
# Compatible with LTPSICE
class Point:
    def __init__(self, p_x='', p_y=''):
        self.x = p_x
        self.y = p_y

    def set_x(self, p_x):
        self.x = p_x

    def set_y(self, p_y):
        self.y = p_y


# End point class
# Compatible with LTSPICE
class EndPoint:
    def __init__(self, p_name=''):
        self.name = p_name
        self.point_list = set()

    def set_name(self, p_name):
        self.name = p_name

    def add_point(self, p_point):
        self.point_list.add(p_point)