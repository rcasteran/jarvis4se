import os
from IPython import get_ipython
from pathlib import Path

import jarvis


def test_attribute_declaration_input(capsys):
    """Notebook equivalent:
     %%jarvis
     with attribute_declaration_input
     A is an attribute
     B is an attribute. C is an attribute

     """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "attribute_declaration_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "A is an attribute\n"
                    "B is an attribute. C is an attribute\n")

    captured = capsys.readouterr()
    expected = ["Creating attribute_declaration_input.xml !\n",
                "C is an attribute (added)\n",
                "A is an attribute (added)\n",
                "B is an attribute (added)\n",
                "attribute_declaration_input.xml updated"]

    assert all(i in captured.out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)


def test_described_attribute_input(capsys):
    """Notebook equivalent:
     %%jarvis
     with described_attribute_input
     F1 is a function
     Fun elem is a functional element
     ========================================
     %%jarvis
     with described_attribute_input
     A is an attribute
     B is an attribute. C is an attribute
     ========================================
     %%jarvis
     with described_attribute_input
     The A of F1 is 4,2
     The C of F1 is pink
     The B of Fun elem is 8,5.
     The A of Fun elem is 100

     """
    ip = get_ipython()
    my_magic = jarvis.MyMagics(ip)
    file_name = "described_attribute_input"
    my_magic.jarvis("", "with %s\n" % file_name +
                    "F1 is a function\n"
                    "Fun elem is a functional element\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "A is an attribute\n"
                    "B is an attribute. C is an attribute\n")
    my_magic.jarvis("", "with %s\n" % file_name +
                    "The A of F1 is 4,2\n"
                    "The C of F1 is pink\n"
                    "The B of Fun elem is 8,5.\n"
                    "The A of Fun elem is 100\n")

    captured = capsys.readouterr()
    expected = ["described_attribute_input.xml parsed\n",
                "Attribute A for F1 with value 4,2 (added)\n",
                "Attribute C for F1 with value pink (added)\n",
                "Attribute B for Fun elem with value 8,5 (added)\n",
                "Attribute A for Fun elem with value 100 (added)\n",
                "described_attribute_input.xml updated\n"]
    # Get las part from capsys
    last_out = captured.out[-len(''.join(expected))-1:len(captured.out)]
    assert all(i in last_out for i in expected)

    fname = os.path.join("./", file_name + ".xml")
    path = Path(fname)
    if path:
        os.remove(path)
