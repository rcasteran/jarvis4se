"""@defgroup test_magic_tools
Tests about Jarvis IPython magic tools
"""
# Libraries


# Modules
import test_lib

# Initialisation of Jarvis
jarvis4se_all = test_lib.get_jarvis4se()
generator = jarvis4se_all[1]
jarvis4se_tool = jarvis4se_all[2]


def test_retrieve_pkg_version_tool(capsys):
    """@ingroup test_magic_tools
    Test the magic line "%retrieve_pkg_version"

    @param[in] capsys : capture fixture reference
    @return None
    """
    jarvis4se_tool.retrieve_pkg_version('')
    captured = capsys.readouterr()
    expected = ["lxml==", "notebook==", "plantuml==", "jarvis4se==", "pandas==", "python=="]
    assert all(i in captured.out for i in expected)


def test_diagram_cell_tool(capsys, mocker):
    """@ingroup test_magic_tools
    Test the magic cell "%%diagram"

    @param[in] capsys : capture fixture reference
    @param[in] mocker : mocker fixture reference
    @return None
    """
    spy = mocker.spy(generator, "get_diagram_url")
    jarvis4se_tool.diagram('', "@startuml\n"
                         "!define Junction_Or circle #black\n"
                         "!define Junction_And circle #whitesmoke\n"
                         "\n"
                         "\n"
                         "Junction_And JunctionAnd\n"
                         "Junction_Or JunctionOr\n"
                         "\n"
                         "archimate #Technology 'VPN Server' as vpnServerA <<technology-device>>\n"
                         "\n"
                         "rectangle GO #lightgreen\n"
                         "rectangle STOP #red\n"
                         "rectangle WAIT #orange\n"
                         "GO -up-> JunctionOr\n"
                         "STOP -up-> JunctionOr\n"
                         "STOP -down-> JunctionAnd\n"
                         "WAIT -down-> JunctionAnd\n"
                         "@enduml\n")
    expected_plantuml_link = "http://www.plantuml.com/plantuml/svg/TL2nhi8m3Dpz5KOTcFe7gA8JUWmK" \
                             "YGf651BJHgGESjCY_fx04oW8sExEToVRypue2KFdO6BeQ9bmER0ErlE-4jHMj2FC3ax" \
                             "fqwUZPFEoN5eRgE_yYG3WpV4a4KDQ_iIL02ZHhUrKY4KrwPQzyyqLfzlr2ZSa8yaKLO" \
                             "_ZcVzPYRDPUFboGwFLL1G0GZeeRk92YmepPvisD4B4oM1JLslCX4oYxSg_6ZClaH74P" \
                             "3wSyo9Ty17weHf_uKI_d_de-pQO4vlxisy="
    expected_notebook_output = "<IPython.core.display.HTML object>\n" \
                               "Overview :\n" \
                               "<IPython.core.display.Markdown object>\n"
    captured = capsys.readouterr()
    assert spy.spy_return == expected_plantuml_link
    assert captured.out == expected_notebook_output
