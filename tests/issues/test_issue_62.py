"""@defgroup test_issue_62
Tests about type creation from extended type related to https://github.com/rcasteran/jarvis4se/issues/62

@see test_issue_62_in
@see test_issue_62_xml
"""
# Libraries


# Modules
import test_lib
from xml_adapter import XmlParser3SE
from datamodel import BaseType

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
xml_parser = XmlParser3SE()


def test_issue_62_in(capsys, input_test_issue_62):
    """@ingroup test_input_cell
    @anchor test_issue_62_in
    Test type creation from extended type related to @ref test_issue_62

    @param[in] capsys : capture fixture reference
    @param[in] input_test_issue_62 : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_issue_62
    """
    file_name = "test_issue_62_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_62}\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "High level function is a type extending Function\n",
                "High high level function is a type extending High level function\n",
                "High high high level function is a type extending High high level function\n"
                "3High is a High high high level function\n",
                f"{file_name}.xml updated\n"]

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_issue_62_xml(input_test_issue_62):
    """@ingroup test_xml_file
    @anchor test_issue_62_xml
    Test type creation from extended type related to @ref test_issue_62

    @param[in] input_test_issue_62 : input fixture reference
    @return none

    **Jarvis4se equivalent:**
    @ref input_test_issue_62
    """
    file_name = "test_issue_62_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_62}\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    assert len([x for x in obj_dict.values() if x]) == 2
    assert len(obj_dict['xml_type_list']) == 3
    assert len(obj_dict['xml_function_list']) == 1

    expected_type = {('High level function', 'Function'),
                     ('High high level function', 'High level function'),
                     ('High high high level function', 'High high level function')}
    captured_type = set()
    for type_elem in obj_dict['xml_type_list']:
        print(type_elem, type_elem.base)
        if isinstance(type_elem.base, BaseType):
            base_type = str(type_elem.base)
        else:
            base_type = type_elem.base.name
        captured_type.add((type_elem.name, base_type))

    assert expected_type == captured_type
    assert obj_dict['xml_function_list'].pop().type.name == "High high high level function"

    test_lib.remove_xml_file(file_name)
