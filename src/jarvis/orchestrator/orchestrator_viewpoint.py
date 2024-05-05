"""@defgroup jarvis
Jarvis module
"""
# Libraries

# Modules
import datamodel
from . import orchestrator_shared
from jarvis.query import question_answer
from jarvis import util
from tools import Logger


def add_view(p_str_list, **kwargs):
    """
        Check if each string in view_name_str is not already corresponding to an actual
        object's name, create new View() object, instantiate it, write it within XML and
        then returns update_list.

            Parameters:
                p_str_list ([str]) : Lists of string from jarvis cell
                xml_view_list ([Function]) : view list from xml parsing
                output_xml (XmlWriter3SE object) : XML's file object

            Returns:
                1 if update, else 0
        """
    xml_view_list = kwargs['xml_view_list']
    output_xml = kwargs['output_xml']
    view_list = []
    update = 0

    # Create a list with all view names already in the xml
    xml_view_name_list = question_answer.get_objects_names(xml_view_list)

    for p_str in p_str_list:
        # Loop on the list and create set for functions
        if p_str not in xml_view_name_list:
            # Instantiate view class
            view = datamodel.View(name=p_str, uid=util.get_unique_id())
            # Add view to new set() and existing set() from xml
            xml_view_list.add(view)
            view_list.append(view)

        activate_view(p_str, xml_view_list)

        if view_list:
            output_xml.write_view(view_list)
            for view in view_list:
                Logger.set_info(__name__,
                                view.name + " is a view")
            update = 1

    return update


def activate_view(view_name, xml_view_list):
    """Activates View from view's name str"""
    for view in xml_view_list:
        if view_name == view.name:
            view.set_activation(True)
        else:
            view.set_activation(False)


def check_get_consider(consider_str_list, **kwargs):
    """
    Check and get all "consider xxx" strings. If corresponds to an actual object not yet added to
    the current view => add it to View object and as allocatedItem within xml
    Args:
        consider_str_list ([strings]): list of strings (separated by comma is possible)
        xml_function_list ([Function]) : Function list from xml parsing
        xml_fun_elem_list ([Fun Elem]) : Functional Element list from xml parsing
        xml_data_list ([Data]) : Data list from xml parsing
        xml_view_list ([View]) : View list from xml parsing
        output_xml (XmlWriter3SE object) : XML's file object

    Returns:
        update ([0/1]) : 1 if update, else 0
    """
    xml_function_list = kwargs['xml_function_list']
    xml_fun_elem_list = kwargs['xml_fun_elem_list']
    xml_data_list = kwargs['xml_data_list']
    xml_view_list = kwargs['xml_view_list']
    output_xml = kwargs['output_xml']

    allocated_item_list = []
    # Create lists with all object names/aliases already in the xml
    xml_fun_elem_name_list = question_answer.get_objects_names(xml_fun_elem_list)
    xml_function_name_list = question_answer.get_objects_names(xml_function_list)
    xml_data_name_list = question_answer.get_objects_names(xml_data_list)

    consider_str_list = util.cut_chain_from_string_list(consider_str_list)

    for consider_str in consider_str_list:
        if consider_str not in [*xml_fun_elem_name_list, *xml_function_name_list,
                                *xml_data_name_list]:
            Logger.set_warning(__name__,
                               f"Object {consider_str} does not exist, available object types are : "
                               f"Functional Element, Function and Data")
        else:
            result_function = any(item == consider_str for item in xml_function_name_list)
            result_fun_elem = any(item == consider_str for item in xml_fun_elem_name_list)
            result_data = any(item == consider_str for item in xml_data_name_list)

            if result_function:
                allocated_fun = orchestrator_shared.check_add_allocated_item(
                    consider_str, xml_function_list, xml_view_list)
                if allocated_fun:
                    allocated_item_list.append(allocated_fun)
            elif result_fun_elem:
                allocated_fun_elem = orchestrator_shared.check_add_allocated_item(
                    consider_str, xml_fun_elem_list, xml_view_list)
                if allocated_fun_elem:
                    allocated_item_list.append(allocated_fun_elem)
            elif result_data:
                allocated_data = orchestrator_shared.check_add_allocated_item(
                    consider_str, xml_data_list, xml_view_list)
                if allocated_data:
                    allocated_item_list.append(allocated_data)

    update = orchestrator_shared.add_allocation({5: allocated_item_list}, **kwargs)

    return update
