""" @defgroup orchestrator
Jarvis orchestrator module
"""
# Libraries

# Modules
from xml_adapter import XML_DICT_KEY_0_DATA_LIST, XML_DICT_KEY_1_FUNCTION_LIST, XML_DICT_KEY_2_FUN_ELEM_LIST, \
    XML_DICT_KEY_3_FUN_INTF_LIST, XML_DICT_KEY_4_PHY_ELEM_LIST, XML_DICT_KEY_5_PHY_INTF_LIST, \
    XML_DICT_KEY_6_STATE_LIST, XML_DICT_KEY_7_TRANSITION_LIST, XML_DICT_KEY_8_REQUIREMENT_LIST, \
    XML_DICT_KEY_9_ACTIVITY_LIST, XML_DICT_KEY_10_ATTRIBUTE_LIST, XML_DICT_KEY_11_VIEW_LIST, \
    XML_DICT_KEY_12_TYPE_LIST, XML_DICT_KEY_13_FUN_CONS_LIST, XML_DICT_KEY_14_FUN_PROD_LIST
from tools import Logger


def update_dictionaries(p_csv_dict, **kwargs):
    csv_dictionary_list = {
        0: p_csv_dict['csv_data_list'],
        1: p_csv_dict['csv_function_list'],
        2: p_csv_dict['csv_fun_elem_list'],
        3: p_csv_dict['csv_fun_inter_list'],
        4: p_csv_dict['csv_phy_elem_list'],
        5: p_csv_dict['csv_phy_inter_list'],
        6: p_csv_dict['csv_state_list'],
        7: p_csv_dict['csv_transition_list'],
        8: p_csv_dict['csv_requirement_list'],
        9: p_csv_dict['csv_attribute_list'],
        10: p_csv_dict['csv_view_list'],
        11: p_csv_dict['csv_type_list'],
        12: p_csv_dict['csv_consumer_function_list'],
        13: p_csv_dict['csv_producer_function_list']
    }
    xml_dictionary_list = {
        0: kwargs[XML_DICT_KEY_0_DATA_LIST],
        1: kwargs[XML_DICT_KEY_1_FUNCTION_LIST],
        2: kwargs[XML_DICT_KEY_2_FUN_ELEM_LIST],
        3: kwargs[XML_DICT_KEY_3_FUN_INTF_LIST],
        4: kwargs[XML_DICT_KEY_4_PHY_ELEM_LIST],
        5: kwargs[XML_DICT_KEY_5_PHY_INTF_LIST],
        6: kwargs[XML_DICT_KEY_6_STATE_LIST],
        7: kwargs[XML_DICT_KEY_7_TRANSITION_LIST],
        8: kwargs[XML_DICT_KEY_8_REQUIREMENT_LIST],
        9: kwargs[XML_DICT_KEY_10_ATTRIBUTE_LIST],
        10: kwargs[XML_DICT_KEY_11_VIEW_LIST],
        11: kwargs[XML_DICT_KEY_12_TYPE_LIST],
        12: kwargs[XML_DICT_KEY_13_FUN_CONS_LIST],
        13: kwargs[XML_DICT_KEY_14_FUN_PROD_LIST]
    }
    output_xml_write_list = {
        0: kwargs['output_xml'].write_data,
        1: kwargs['output_xml'].write_function,
        2: kwargs['output_xml'].write_functional_element,
        3: kwargs['output_xml'].write_functional_interface,
        4: kwargs['output_xml'].write_physical_element,
        5: kwargs['output_xml'].write_physical_interface,
        6: kwargs['output_xml'].write_state,
        7: kwargs['output_xml'].write_transition,
        8: kwargs['output_xml'].write_requirement,
        9: kwargs['output_xml'].write_attribute,
        10: kwargs['output_xml'].write_view,
        11: kwargs['output_xml'].write_type_element,
        12: kwargs['output_xml'].write_data_consumer,
        13: kwargs['output_xml'].write_data_producer
    }

    update = 0
    for i in range(0, len(csv_dictionary_list)):
        csv_obj_dict = csv_dictionary_list.get(i)
        xml_obj_dict = xml_dictionary_list.get(i)
        for csv_obj in csv_obj_dict:
            is_obj_id = False
            for xml_obj in xml_obj_dict:
                if i in [2, 3]:
                    if xml_obj[0] == csv_obj[0] and xml_obj[1].id == csv_obj[1].id:
                        is_obj_id = True
                        Logger.set_info(__name__,
                                        f'Relationship "{xml_obj}" is the same than "{csv_obj}"')
                else:
                    if xml_obj.id == csv_obj.id:
                        is_obj_id = True
                        Logger.set_info(__name__,
                                        f'Object "{xml_obj.name}" has the same identifier than "{csv_obj.name}"')
                        break
                    # Else do nothing

            if not is_obj_id:
                if i in [2, 3]:
                    xml_obj_dict.append(csv_obj)
                else:
                    xml_obj_dict.add(csv_obj)

                call = output_xml_write_list.get(i)
                call([csv_obj])

                if i in [2, 3]:
                    Logger.set_info(__name__,
                                    f'Relationship {csv_obj} added')
                else:
                    Logger.set_info(__name__,
                                    f'Object "{csv_obj.name}" added')

                update = 1
            # Else do nothing

    return update
