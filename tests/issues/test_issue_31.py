"""@defgroup test_issue_31
Tests about function children production and consumption related to https://github.com/rcasteran/jarvis4se/issues/31

@see test_issue_31_plantuml_context
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter
from xml_adapter import XmlParser3SE

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
xml_parser = XmlParser3SE()


def test_issue_31_plantuml_context(mocker, input_test_issue_31):
    """@ingroup test_plantuml_context
    @anchor test_issue_31_plantuml_context
    Test context diagram display related to @ref test_issue_31

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_31 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_31
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_issue_31_plantuml_context"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_31}\n"
                         f"show context F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F1" as f1 <<Function>>\n',
                'circle f1_i\n',
                'circle f1_o\n',
                'f1_i --> f1 : ',
                'b', '\\n', 'd', '\n',
                'f1 --> f1_o  : ',
                'c', '\\n', 'a', '\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == len("\'id: xxxxxxxxxx\n")


def test_issue_31_xml(input_test_issue_31):
    """@ingroup test_xml_file
    @anchor test_issue_31_xml
    Test xml file generation related to @ref test_issue_31

    @param[in] input_test_issue_31 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_31
    """
    file_name = "test_issue_31_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_31}\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected_cons = {('b', 'F1a'), ('d', 'F1'), ('b', 'F1'), ('d', 'F1a'), ('d', 'F1a1')}
    expected_prod = {('c', 'F1a1'), ('a', 'F1'), ('c', 'F1'), ('c', 'F1a'), ('a', 'F1a')}
    expected_child = {('F1', 'F1a'), ('F1a', 'F1a1')}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result_cons = set()
    result_prod = set()
    result_child = set()
    assert len(obj_dict['xml_data_list']) == 4 and len(obj_dict['xml_function_list']) == 3
    assert (len(obj_dict['xml_consumer_function_list']) and
            len(obj_dict['xml_producer_function_list'])) == 5

    for cons in obj_dict['xml_consumer_function_list']:
        result_cons.add((cons[0].name, cons[1].name))
    for prod in obj_dict['xml_producer_function_list']:
        result_prod.add((prod[0].name, prod[1].name))
    for fun in obj_dict['xml_function_list']:
        if fun.child_list:
            for child in fun.child_list:
                result_child.add((fun.name, child.name))

    test_lib.remove_xml_file(file_name)

    assert expected_cons == result_cons
    assert expected_prod == result_prod
    assert expected_child == result_child
