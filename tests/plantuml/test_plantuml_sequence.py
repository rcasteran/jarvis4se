"""@defgroup test_plantuml_sequence
Tests about Plantuml sequence diagrams
"""
# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_fun_elem_with_interfaces_plantuml_sequence(mocker, input_test_fun_elem_with_interfaces_3):
    """@ingroup test_plantuml_sequence
    @anchor test_fun_elem_with_interfaces_plantuml_sequence
    Test sequence diagram display for functional elements with interfaces

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_fun_elem_with_interfaces_3 : input fixture reference
    @return None

    **Jarvis4se equivalent:**
    @ref input_test_fun_elem_with_interfaces_3
    """
    spy = mocker.spy(plantuml_adapter, "get_sequence_diagram")
    file_name = "fun_inter_simple_sequence"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_with_interfaces_3}\n"
                         "show sequence Fun_inter\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['!pragma teoz true\n',
                'participant "Fun_elem_1" as fun_elem_1 <<Functional element>>\n',
                'participant "Fun_elem_2" as fun_elem_2 <<Functional element>>\n',
                'activate fun_elem_1\n',
                'activate fun_elem_2\n',
                'fun_elem_1 -> fun_elem_2 : 1- A\n',
                'fun_elem_2 -> fun_elem_1 : 2- B\n',
                'fun_elem_1 -> fun_elem_2 : 3- C\n',
                'deactivate fun_elem_1\n',
                'deactivate fun_elem_2\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) == len(''.join(expected))
