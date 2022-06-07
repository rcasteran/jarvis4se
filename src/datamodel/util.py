#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Module extension for datamodel"""


class Point:
    """Point class: Compatible with LTPSICE"""
    def __init__(self, p_x='', p_y=''):
        """Init"""
        self.x = p_x
        self.y = p_y

    def set_x(self, p_x):
        """Set x"""
        self.x = p_x

    def set_y(self, p_y):
        """Set y"""
        self.y = p_y


class EndPoint:
    """End point class: Compatible with LTSPICE"""
    def __init__(self, p_name=''):
        """Init"""
        self.name = p_name
        self.point_list = set()

    def set_name(self, p_name):
        """Set name"""
        self.name = p_name

    def add_point(self, p_point):
        """Add point to point_list"""
        self.point_list.add(p_point)
