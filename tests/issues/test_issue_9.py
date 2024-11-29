"""@defgroup test_issue_9
Tests about object allocation to a view related to https://github.com/rcasteran/jarvis4se/issues/9

@see test_issue_9_in
@see test_issue_9_xml
"""
# Libraries


# Modules
import test_lib
from xml_adapter import XmlParser3SE

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
xml_parser = XmlParser3SE()


def test_issue_9_in(capsys, input_test_issue_9):
    """@ingroup test_input_cell
    @anchor test_issue_9_in
    Test object allocation to a view related to @ref test_issue_9

    @param[in] capsys : capture fixture reference
    @param[in] input_test_issue_9 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_9
    """
    file_name = "test_issue_9_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_9[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_9[1]}\n")

    captured = capsys.readouterr()
    expected = [f"{file_name}.xml parsed\n",
                "test_view is a view\n",
                "[WARNING] Object toto does not exist, available object types are:\n"
                "- Functional Element, Function and Data\n",
                "- Physical Element, Activity and Information\n",
                "[WARNING] Object tata does not exist, available object types are:\n"
                "- Functional Element, Function and Data\n",
                "- Physical Element, Activity and Information\n",
                "Function F1 is allocated to View test_view\n",
                "Data a is allocated to View test_view\n",
                "FunctionalElement Fun_elem is allocated to View test_view\n",
                "Function F2 with a long name is allocated to View test_view\n",
                "Function F3 is allocated to View test_view\n",
                "Function F4 is allocated to View test_view\n",
                f"{file_name}.xml updated\n"]

    # Get last part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]

    test_lib.remove_xml_file(file_name)

    assert all(i in last_out for i in expected)


def test_issue_9_xml(input_test_issue_9):
    """@ingroup test_input_cell
    @anchor test_issue_9_xml
    Test object allocation to a view related to @ref test_issue_9

    @param[in] input_test_issue_9 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_9
    """
    file_name = "test_issue_9_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_9[0]}")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_9[1]}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected = {'F1', 'F2 with a long name', 'F3', 'F4', 'a', 'Fun_elem'}
    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result = set()
    assert len(obj_dict['xml_view_list']) == 1
    assert "test_view" in {i.name for i in obj_dict['xml_view_list']}
    for item in next(iter(obj_dict['xml_view_list'])).allocated_item_list:
        for fun in obj_dict['xml_function_list']:
            if item == fun.id:
                result.add(fun.name)

        for fun_elem in obj_dict['xml_fun_elem_list']:
            if item == fun_elem.id:
                result.add(fun_elem.name)

        for data in obj_dict['xml_data_list']:
            if item == data.id:
                result.add(data.name)

    test_lib.remove_xml_file(file_name)

    assert expected == result
