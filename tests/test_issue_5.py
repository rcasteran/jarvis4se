"""@defgroup test_issue_5
Test about function parent and child consumer related to https://github.com/rcasteran/jarvis4se/issues/5

@see test_issue_5_diagram
@see test_issue_5_xml

**Jarvis4se equivalent:**

    with test_issue_5
    F1 is a function
    F1a is a function
    F1b is a function
    F1c is a function
    F1d is a function
    F1e is a function
    F2 is a function
    F3 is a function

    F1 is composed of F1a
    F1 is composed of F1b
    F1 is composed of F1c
    F1 is composed of F1d
    F1 is composed of F1e

    a is a data
    F1 produces a
    F2 consumes a

    F1a produces a
    F1b consumes a

    b is a data
    F1c produces b
    F1d consumes b

    c is a data
    F3 produces c
    F1e consumes c

    show decomposition F1
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter
from xml_adapter import XmlParser3SE

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]
xml_parser = XmlParser3SE()


def test_issue_5_diagram(mocker, input_test_issue_5):
    """@ingroup test_decomposition_diagrams
    @anchor test_issue_5_diagram
    Test decomposition diagram related to @ref test_issue_5

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_5 : input fixture reference
    @return none
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")
    file_name = "test_issue_5"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_5}\n"
                         "show decomposition F1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['object "F3" as f3 <<Function>>\n',
                'component "F1" as f1 <<Function>>{\n',
                'object "F1c" as f1c <<Function>>\n',
                'object "F1d" as f1d <<Function>>\n',
                'object "F1e" as f1e <<Function>>\n',
                'object "F1a" as f1a <<Function>>\n',
                'object "F1b" as f1b <<Function>>\n',
                '}\n',
                'object "F2" as f2 <<Function>>\n',
                'f1a #--> f2 : a\n',
                'f1c #--> f1d : b\n',
                'f1a #--> f1b : a\n',
                'f3 #--> f1e : c\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 8*len("\'id: xxxxxxxxxx\n")


def test_issue_5_xml(input_test_issue_5):
    """@ingroup test_xml_file
    @anchor test_issue_5_xml
    Test xml file related to @ref test_issue_5

    @param[in] input_test_issue_5 : input fixture reference
    @return none
    """
    file_name = "test_issue_5"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_5}")

    obj_dict = xml_parser.parse_xml(file_name + ".xml")

    expected_cons = {('a', 'F1b'), ('b', 'F1d'), ('a', 'F2'), ('c', 'F1e'), ('c', 'F1')}
    expected_prod = {('b', 'F1c'), ('c', 'F3'), ('a', 'F1a'), ('a', 'F1')}
    expected_child = {('F1', 'F1e'), ('F1', 'F1d'), ('F1', 'F1c'), ('F1', 'F1b'), ('F1', 'F1a')}

    # xml_adapter.parse_xml() returns mainly set(), so the order can change
    # thus we have to compare it with a set also
    result_cons = set()
    result_prod = set()
    result_child = set()
    assert len(obj_dict['xml_data_list']) == 3 and len(obj_dict['xml_function_list']) == 8
    assert len(obj_dict['xml_consumer_function_list']) == 5 and \
           len(obj_dict['xml_producer_function_list']) == 4

    for cons in obj_dict['xml_consumer_function_list']:
        result_cons.add((cons[0], cons[1].name))
    for prod in obj_dict['xml_producer_function_list']:
        result_prod.add((prod[0], prod[1].name))
    for fun in obj_dict['xml_function_list']:
        if fun.child_list:
            for child in fun.child_list:
                result_child.add((fun.name, child.name))

    test_lib.remove_xml_file(file_name)

    assert expected_cons == result_cons
    assert expected_prod == result_prod
    assert expected_child == result_child
