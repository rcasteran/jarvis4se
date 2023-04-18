"""@defgroup test_issue_81
Tests about functional decomposition related to https://github.com/rcasteran/jarvis4se/issues/81

@see test_issue_81_diagram

**Jarvis4se equivalent:**

    with test_issue_81
    F1 is a function
    F2 is a function
    a is a data
    F1 produces a
    F2 consumes a
    F21 is a function
    F22 is a function
    F21 composes F2
    F22 composes F2
    F211 is a function
    F212 is a function
    F211 composes F21
    F212 composes F21
    F211 consumes a
    F212 produces b
    c is a data
    F211 produces c
    F212 consumes c
    F21 consumes a
    b is a data
    F21 produces b
    F22 consumes b
"""
# Libraries

# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_issue_81_diagram(mocker, input_test_issue_81):
    """@ingroup test_decomposition_diagrams
    @anchor test_issue_81_diagram
    Test context diagram display related to @ref test_issue_81

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_issue_81 : input fixture reference
    @return none
    """
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")

    file_name = "fun_elem_decomposition_level"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_issue_81}\n"
                         "show decomposition F2 at level 1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "F2" as f2 <<Function>>\n',
                'object "F21" as f21 <<Function>>\n',
                'object "F22" as f22 <<Function>>\n',
                'object "F1" as f1 <<Function>>\n',
                'f1 #--> f21 : a\n',
                'f21 #--> f22 : b\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 3*len("\'id: xxxxxxxxxx\n")