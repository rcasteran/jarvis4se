"""@defgroup test_decomposition_diagrams
Tests about decomposition diagrams
"""
# Libraries


# Modules
import test_lib
import plantuml_adapter

# Initialisation of Jarvis
jarvis4se = test_lib.get_jarvis4se()[0]


def test_fun_elem_decomposition_with_interface(mocker, input_test_fun_elem_decomposition_with_interface):
    """@ingroup test_decomposition_diagrams
    @anchor test_fun_elem_decompo_with_interface
    Test decomposition diagram display with functional element decomposition and interface allocation

    @param[in] mocker : mocker fixture reference
    @param[in] input_test_fun_elem_decompo_with_interface : input fixture reference
    @return none

    **Jarvis4se equivalent:**

        with fun_elem_decompo_with_interface
        F1 is a function
        F1b is a function
        F1c is a function
        F1 is composed of F1b
        F1 is composed of F1c

        F1c1 is a function
        F1c is composed of F1c1

        F_ext is a function

        E1 is a functional element
        E1b is a functional element
        E1c is a functional element
        Ext is a functional element
        E1 is composed of E1c
        E1 is composed of E1b
        E1c1 is a functional element
        E1c is composed of E1c1

        E1 allocates F1
        E1b allocates F1b
        E1c allocates F1c
        E1c1 allocates F1c1
        Ext allocates F_ext

        A is a data
        A_2 is a data
        B is a data
        C is a data

        Fun_inter_A is a functional interface
        Fun_inter_A allocates A
        Fun_inter_A allocates A_2
        Fun_inter_B is a functional interface
        Fun_inter_B allocates B

        F1c1 produces A
        F1c1 produces A_2
        F1b consumes A
        F1b consumes A_2

        F_ext produces B
        F1c1 consumes B

        F1b produces C
        F_ext consumes C

        E1c exposes Fun_inter_A
        E1c1 exposes Fun_inter_A
        E1b exposes Fun_inter_A

        show decomposition E1
    """
    spy = mocker.spy(plantuml_adapter, "get_fun_elem_decomposition")
    file_name = "fun_elem_decompo_with_interface"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_elem_decomposition_with_interface}\n"                         
                         "show decomposition E1\n")

    # result = plantuml text without "@startuml ... @enduml" tags
    result = spy.spy_return
    expected = ['component "E1" as e1 <<Functional element>>{\n',
                'component "E1c" as e1c <<Functional element>>{\n',
                'component "E1c1" as e1c1 <<Functional element>>{\n',
                'object "F1c1" as f1c1 <<Function>>\n',
                '}\n',
                '}\n',
                'component "E1b" as e1b <<Functional element>>{\n',
                'object "F1b" as f1b <<Function>>\n',
                '}\n',
                '}\n',
                'component "Ext" as ext <<Functional element>>{\n',
                'object "F_ext" as f_ext <<Function>>\n',
                '}\n',
                'f_ext #--> f1c1 : B\n',
                'f1b #--> f_ext : C\n',
                'e1b', ' -- ', 'e1c1 ', ': fun_inter_a\n']

    test_lib.remove_xml_file(file_name)

    assert all(i in result for i in expected)
    assert len(result) - len(''.join(expected)) == 8*len("\'id: xxxxxxxxxx\n")


def test_fun_decomposition_level(mocker, input_test_fun_decomposition_level):
    spy = mocker.spy(plantuml_adapter, "get_function_diagrams")

    file_name = "fun_elem_decomposition_level"
    jarvis4se.jarvis("", f"with {file_name}\n"
                         f"{input_test_fun_decomposition_level}\n"
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