"""Test module for tools pkg i.e. MagicTools"""
from IPython import get_ipython

import jarvis

ip = get_ipython()
generator = jarvis.PlantUmlGen()
my_magic = jarvis.MagicTools(ip, generator)


def test_retrieve_pkg_version(capsys):
    """Notebook equivalent:
    %retrieve_pkg_version
    """
    my_magic.retrieve_pkg_version('')
    captured = capsys.readouterr()
    expected = ["lxml==", "notebook==", "plantuml==", "jarvis4se==", "pandas==", "python=="]
    assert all(i in captured.out for i in expected)


def test_diagram_cell(capsys, mocker):
    """Notebook equivalent:
    %%diagram
    @startuml
    !define Junction_Or circle #black
    !define Junction_And circle #whitesmoke

    Junction_And JunctionAnd
    Junction_Or JunctionOr

    archimate #Technology "VPN Server" as vpnServerA <<technology-device>>

    rectangle GO #lightgreen
    rectangle STOP #red
    rectangle WAIT #orange
    GO -up-> JunctionOr
    STOP -up-> JunctionOr
    STOP -down-> JunctionAnd
    WAIT -down-> JunctionAnd
    @enduml
    """
    spy = mocker.spy(generator, "get_diagram_url")
    my_magic.diagram('', "@startuml\n"
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
