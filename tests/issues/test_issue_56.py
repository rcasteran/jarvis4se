"""@defgroup test_issue_56
Tests about extended types related to https://github.com/rcasteran/jarvis4se/issues/56

@see test_issue_56_in
@see test_issue_56_xml
"""
# Libraries


# Modules
import test_lib
from xml_adapter import XmlParser3SE
from datamodel import BaseType

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
xml_parser = XmlParser3SE()


def test_issue_56_in(capsys, input_test_issue_56):
    """@ingroup test_input_cell
    @anchor test_issue_56_in
    Test extended types related to @ref test_issue_56

    @param[in] capsys : capture fixture reference
    @param[in] input_test_issue_56 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_56
    """
    file_name = "test_issue_56_in"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_56[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_56[1]}\n")

    captured = capsys.readouterr()
    expected = [f"Creating {file_name}.xml !\n",
                "Safety interface is a type extending Functional interface\n",
                "The alias for Safety interface is sf\n",
                f"{file_name}.xml updated\n"
                f"{file_name}.xml parsed\n",
                "Fun_inter is a Functional interface\n",
                "sf_a is a type extending Safety interface\n",
                "sf_a_b is a type extending sf_a\n",
                "final one is a type extending sf_a_b\n",
                "The type of Fun_inter is final one\n",
                f"{file_name}.xml updated\n"]

    test_lib.remove_xml_file(file_name)

    assert all(i in captured.out for i in expected)


def test_issue_56_xml(input_test_issue_56):
    """@ingroup test_xml_file
    @anchor test_issue_56_xml
    Test extended types related to @ref test_issue_56

    @param[in] input_test_issue_56 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_issue_56
    """
    file_name = "test_issue_56_xml"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_56[0]}\n")
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_56[1]}\n")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    assert len([x for x in obj_dict.values() if x]) == 2
    assert len(obj_dict['xml_type_list']) == 4
    assert len(obj_dict['xml_fun_inter_list']) == 1

    expected_type = {('sf_a', 'Safety interface'), ('sf_a_b', 'sf_a'),
                     ('Safety interface', 'Functional interface'), ('final one', 'sf_a_b')}
    captured_type = set()
    for type_elem in obj_dict['xml_type_list']:
        if type_elem.name == 'Safety interface':
            assert type_elem.alias == 'sf'
        if isinstance(type_elem.base, BaseType):
            base_type = str(type_elem.base)
        else:
            base_type = type_elem.base.name
        captured_type.add((type_elem.name, base_type))

    assert expected_type == captured_type
    assert obj_dict['xml_fun_inter_list'].pop().type.name == "final one"

    test_lib.remove_xml_file(file_name)
