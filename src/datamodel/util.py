"""@defgroup datamodel
Module for 3SE datamodel
"""

# Constants
INFO_KEY_TYPE = 'type'
INFO_KEY_ALIAS = 'alias'
INFO_KEY_PARENT = 'parent'
INFO_KEY_DERIVED = 'derived from object'
INFO_KEY_CHILD_LIST = 'child list'
INFO_KEY_REQUIREMENT_LIST = 'requirement list'
INFO_KEY_GOAL_LIST = 'goal list'
INFO_KEY_DATA_LIST = 'allocated data list'
INFO_KEY_ACTIVITY_LIST = 'allocated activity list'
INFO_KEY_INFORMATION_LIST = 'allocated information list'
INFO_KEY_TEXT = 'text'


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
    Return a string representation of the type of class instance
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.type == type(p_obj).__name__:
        rep = f'"{p_obj.name}" is a {p_obj.type} of class {type(p_obj).__name__} (id: {p_obj.id}).'
    else:
        rep = f'"{p_obj.name}" is a {p_obj.type.name} (id:{p_obj.id}).'

    return rep


def info_type(p_obj):
    """@ingroup datamodel
    @anchor info_type
    Return a dict representation of the type of class instance
    @param[in] p_obj class instance
    @return dict
    """
    if p_obj.type == type(p_obj).__name__:
        info_dict = {INFO_KEY_TYPE: type(p_obj).__name__}
    else:
        info_dict = {INFO_KEY_TYPE: p_obj.type.name}

    return info_dict


def str_alias(p_obj):
    """@ingroup datamodel
    @anchor str_alias
    Return a string representation of the alias of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.alias:
        rep = f'"{p_obj.name}" alias is {p_obj.alias}.'
    else:
        rep = f'"{p_obj.name}" has no alias.'

    return rep


def info_alias(p_obj):
    """@ingroup datamodel
    @anchor info_alias
    Return a dict representation of the alias of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if p_obj.alias:
        info_dict = {INFO_KEY_ALIAS: p_obj.alias}
    else:
        info_dict = {INFO_KEY_ALIAS: 'none'}

    return info_dict


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


def info_parent(p_obj):
    """@ingroup datamodel
    @anchor info_parent
    Return a dict representation of the parent of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if p_obj.parent is not None:
        info_dict = {INFO_KEY_PARENT: p_obj.parent.name}
    else:
        info_dict = {INFO_KEY_PARENT: 'none'}

    return info_dict


def str_derived(p_obj):
    """@ingroup datamodel
    @anchor str_derived
    Return a string representation of the object the class instance is derived from
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.derived is not None:
        rep = f'"{p_obj.name}" is derived from object (id: {p_obj.derived.id}).'
    else:
        rep = f'"{p_obj.name}" is not derived from other object.'

    return rep


def info_derived(p_obj):
    """@ingroup datamodel
    @anchor info_derived
    Return a dict representation of the object the class instance is derived from
    @param[in] p_obj class instance
    @return dict
    """
    if p_obj.derived is not None:
        info_dict = {INFO_KEY_DERIVED: p_obj.derived.id}
    else:
        info_dict = {INFO_KEY_DERIVED: 'none'}

    return info_dict


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


def info_child_list(p_obj):
    """@ingroup datamodel
    @anchor info_child_list
    Return a dict representation of the child list of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if len(p_obj.child_list) > 0:
        child_name_list = ''
        for item in p_obj.child_list:
            child_name_list += f'{item.name}\n'
        child_name_list = child_name_list[:-1]
        info_dict = {INFO_KEY_CHILD_LIST: child_name_list}
    else:
        info_dict = {INFO_KEY_CHILD_LIST: 'none'}

    return info_dict


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


def info_allocated_req(p_obj):
    """@ingroup datamodel
    @anchor info_allocated_req
    Return a dict representation of the allocated requirement list of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if len(p_obj.allocated_req_list) > 0:
        req_id_list = ''
        for item in p_obj.allocated_req_list:
            req_id_list += f'{item}\n'
        req_id_list = req_id_list[:-1]
        info_dict = {INFO_KEY_REQUIREMENT_LIST: req_id_list}
    else:
        info_dict = {INFO_KEY_REQUIREMENT_LIST: 'none'}

    return info_dict


def str_allocated_goal(p_obj):
    """@ingroup datamodel
    @anchor str_allocated_goal
    Return a string representation of the allocated goal list of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if len(p_obj.allocated_goal_list) > 1:
        rep = f'"{p_obj.name}" has {len(p_obj.allocated_goal_list)} allocated goals:\n'
        for item in p_obj.allocated_goal_list:
            rep += f' - goal (id: {item})\n'
        rep = rep[:-1]
    elif len(p_obj.allocated_goal_list) == 1:
        rep = f'"{p_obj.name}" has one allocated goal:\n'
        for item in p_obj.allocated_goal_list:
            rep += f' - goal (id: {item})\n'
        rep = rep[:-1]
    else:
        rep = f'"{p_obj.name}" has no allocated goal.'

    return rep


def info_allocated_goal(p_obj):
    """@ingroup datamodel
    @anchor info_allocated_goal
    Return a dict representation of the allocated goal list of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if len(p_obj.allocated_goal_list) > 0:
        goal_id_list = ''
        for item in p_obj.allocated_goal_list:
            goal_id_list += f'{item}\n'
        goal_id_list = goal_id_list[:-1]
        info_dict = {INFO_KEY_GOAL_LIST: goal_id_list}
    else:
        info_dict = {INFO_KEY_GOAL_LIST: 'none'}

    return info_dict


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


def info_allocated_data(p_obj):
    """@ingroup datamodel
    @anchor info_allocated_data
    Return a dict representation of the allocated data list of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if len(p_obj.allocated_data_list) > 0:
        data_id_list = ''
        for item in p_obj.allocated_data_list:
            data_id_list += f'{item}\n'
        data_id_list = data_id_list[:-1]
        info_dict = {INFO_KEY_DATA_LIST: data_id_list}
    else:
        info_dict = {INFO_KEY_DATA_LIST: 'none'}

    return info_dict


def str_allocated_activity(p_obj):
    """@ingroup datamodel
    @anchor str_allocated_activity
    Return a string representation of the allocated activity list of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if len(p_obj.allocated_activity_list) > 1:
        rep = f'"{p_obj.name}" has {len(p_obj.allocated_activity_list)} allocated activity:\n'
        for item in p_obj.allocated_activity_list:
            rep += f' - activity with identifier {item}\n'
        rep = rep[:-1]
    elif len(p_obj.allocated_activity_list) == 1:
        rep = f'"{p_obj.name}" has one allocated activity:\n'
        for item in p_obj.allocated_activity_list:
            rep += f' - activity with identifier {item}\n'
        rep = rep[:-1]
    else:
        rep = f'"{p_obj.name}" has no allocated activity.'

    return rep


def info_allocated_activity(p_obj):
    """@ingroup datamodel
    @anchor info_allocated_activity
    Return a dict representation of the allocated activity list of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if len(p_obj.allocated_activity_list) > 0:
        activity_id_list = ''
        for item in p_obj.allocated_activity_list:
            activity_id_list += f'{item}\n'
        activity_id_list = activity_id_list[:-1]
        info_dict = {INFO_KEY_ACTIVITY_LIST: activity_id_list}
    else:
        info_dict = {INFO_KEY_ACTIVITY_LIST: 'none'}

    return info_dict


def str_allocated_information(p_obj):
    """@ingroup datamodel
    @anchor str_allocated_information
    Return a string representation of the allocated information of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if len(p_obj.allocated_info_list) > 1:
        rep = f'"{p_obj.name}" has {len(p_obj.allocated_info_list)} allocated information:\n'
        for item in p_obj.allocated_info_list:
            rep += f' - information with identifier {item}\n'
        rep = rep[:-1]
    elif len(p_obj.allocated_info_list) == 1:
        rep = f'"{p_obj.name}" has one allocated information:\n'
        for item in p_obj.allocated_info_list:
            rep += f' - information with identifier {item}\n'
        rep = rep[:-1]
    else:
        rep = f'"{p_obj.name}" has no allocated information.'

    return rep


def info_allocated_information(p_obj):
    """@ingroup datamodel
    @anchor info_allocated_information
    Return a dict representation of the allocated information of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if len(p_obj.allocated_info_list) > 0:
        information_id_list = ''
        for item in p_obj.allocated_info_list:
            information_id_list += f'{item}\n'
        information_id_list = information_id_list[:-1]
        info_dict = {INFO_KEY_INFORMATION_LIST: information_id_list}
    else:
        info_dict = {INFO_KEY_INFORMATION_LIST: 'none'}

    return info_dict


def str_text(p_obj):
    """@ingroup datamodel
    @anchor str_text
    Return a string representation of the text of a class instance
    @param[in] p_obj class instance
    @return string
    """
    if p_obj.text:
        rep = f'"{p_obj.name}" text is {p_obj.text}.'
    else:
        rep = f'"{p_obj.name}" has no text.'

    return rep


def info_text(p_obj):
    """@ingroup datamodel
    @anchor info_text
    Return a dict representation of the text of a class instance
    @param[in] p_obj class instance
    @return dict
    """
    if p_obj.text:
        info_dict = {INFO_KEY_TEXT: p_obj.text}
    else:
        info_dict = {INFO_KEY_TEXT: 'none'}

    return info_dict
