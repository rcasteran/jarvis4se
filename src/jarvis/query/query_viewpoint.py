""" @defgroup query
Jarvis query module
"""
# Libraries


# Modules
from jarvis.orchestrator import orchestrator_viewpoint_type


def query_type_by_name(p_type_name, **kwargs):
    return orchestrator_viewpoint_type.retrieve_type_by_name(p_type_name, **kwargs)


def query_type_object_name_list(p_type_object, **kwargs):
    return orchestrator_viewpoint_type.retrieve_type_object_name_list(p_type_object, **kwargs)
