"""@defgroup jarvis
Jarvis module
"""
# Libraries

# Modules
from tools import Logger


def update_dictionaries(p_csv_dict, **kwargs):
    csv_dictionary_list = {
        0: p_csv_dict['csv_function_list'],
        1: p_csv_dict['csv_consumer_function_list'],
        2: p_csv_dict['csv_producer_function_list'],
        3: p_csv_dict['csv_data_list'],
        4: p_csv_dict['csv_state_list'],
        5: p_csv_dict['csv_transition_list'],
        6: p_csv_dict['csv_fun_elem_list'],
        7: p_csv_dict['csv_view_list'],
        8: p_csv_dict['csv_attribute_list'],
        9: p_csv_dict['csv_fun_inter_list'],
        10: p_csv_dict['csv_phy_elem_list'],
        11: p_csv_dict['csv_phy_inter_list'],
        12: p_csv_dict['csv_type_list'],
        13: p_csv_dict['csv_requirement_list']
    }
    xml_dictionary_list = {
        0: kwargs['xml_function_list'],
        1: kwargs['xml_consumer_function_list'],
        2: kwargs['xml_producer_function_list'],
        3: kwargs['xml_data_list'],
        4: kwargs['xml_state_list'],
        5: kwargs['xml_transition_list'],
        6: kwargs['xml_fun_elem_list'],
        7: kwargs['xml_view_list'],
        8: kwargs['xml_attribute_list'],
        9: kwargs['xml_fun_inter_list'],
        10: kwargs['xml_phy_elem_list'],
        11: kwargs['xml_phy_inter_list'],
        12: kwargs['xml_type_list'],
        13: kwargs['xml_requirement_list']
    }
    output_xml_write_list = {
        0: kwargs['output_xml'].write_function,
        1: kwargs['output_xml'].write_data_consumer,
        2: kwargs['output_xml'].write_data_producer,
        3: kwargs['output_xml'].write_data,
        4: kwargs['output_xml'].write_state,
        5: kwargs['output_xml'].write_transition,
        6: kwargs['output_xml'].write_functional_element,
        7: kwargs['output_xml'].write_view,
        8: kwargs['output_xml'].write_attribute,
        9: kwargs['output_xml'].write_functional_interface,
        10: kwargs['output_xml'].write_physical_element,
        11: kwargs['output_xml'].write_physical_interface,
        12: kwargs['output_xml'].write_type_element,
        13: kwargs['output_xml'].write_requirement
    }

    update = 0
    for i in range(0, len(csv_dictionary_list)):
        csv_obj_dict = csv_dictionary_list.get(i)
        xml_obj_dict = xml_dictionary_list.get(i)
        for csv_obj in csv_obj_dict:
            is_obj_id = False
            for xml_obj in xml_obj_dict:
                if xml_obj.id == csv_obj.id:
                    is_obj_id = True
                    Logger.set_info(__name__,
                                    f'Object "{xml_obj.name}" has the same identifier than "{csv_obj.name}"')
                    break
                # Else do nothing

            if not is_obj_id:
                xml_obj_dict.add(csv_obj)
                call = output_xml_write_list.get(i)
                call([csv_obj])
                Logger.set_info(__name__,
                                f'Object "{csv_obj.name}" added')
                update = 1
            # Else do nothing

    return update
