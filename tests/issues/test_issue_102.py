"""@defgroup test_issue_102
Tests about function allocation related to https://github.com/rcasteran/jarvis4se/issues/102

@see test_issue_102_plantuml_decomposition
@see test_issue_102_xml
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter
from xml_adapter import XmlParser3SE

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
xml_parser = XmlParser3SE()

def test_issue_102_plantuml_decomposition(mocker, input_test_issue_102):
    """@ingroup test_issue_102_plantuml_decomposition
    @anchor test_issue_102_plantuml_decomposition
    Test function allocation on functional element when decomposition is greater than 2 levels

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_102 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_102
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "test_issue_102_plantuml_decomposition"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_102}\n")

    jarvis4se.jarvis("", f"with {file_name}\n"
                         'show decomposition E\n')

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E" as e <<Functional element>>{\n',
                'component "E1" as e1 <<Functional element>>{\n',
                'object "F11" as f11 <<Function>>\n',
                '}\n',
                'component "E2" as e2 <<Functional element>>{\n',
                'component "E22" as e22 <<Functional element>>{\n',
                'object "F2" as f2 <<Function>>\n',
                '}\n',
                'component "E21" as e21 <<Functional element>>{\n',
                'object "F12" as f12 <<Function>>\n',
                '}\n',
                '}\n',
                '}\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 8 * len("\'id: xxxxxxxxxx\n")


def test_issue_102_xml(input_test_issue_102):
    """@ingroup test_issue_102_plantuml_decomposition
    @anchor test_issue_102_xml
    Test function allocation on functional element when decomposition is greater than 2 levels

    @param[in] input_test_issue_102 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_102
    """
    file_name = "test_issue_102_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_102}\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected_allocated_function_name_list = dict()
    expected_allocated_function_name_list['E21'] = 'F12'
    expected_allocated_function_name_list['E22'] = 'F2'
    expected_allocated_function_name_list['E1'] = 'F11'

    result_allocated_function_name_list = dict()
    for fun_elem in obj_dict['xml_fun_elem_list']:
        if len(fun_elem.allocated_function_list) > 0:
            for allocated_fun_id in fun_elem.allocated_function_list:
                for fun in obj_dict['xml_function_list']:
                    if fun.id == allocated_fun_id:
                        result_allocated_function_name_list[fun_elem.name] = fun.name
                        break
                    # Else do nothing
        else:
            result_allocated_function_name_list[fun_elem.name] = ''

    test_lib.remove_xml_file(file_name)

    assert expected_allocated_function_name_list['E21'] == result_allocated_function_name_list['E21']
    assert expected_allocated_function_name_list['E22'] == result_allocated_function_name_list['E22']
    assert expected_allocated_function_name_list['E1'] == result_allocated_function_name_list['E1']

