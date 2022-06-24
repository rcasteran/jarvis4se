#!/usr/bin/env python
"""Modules for MagicTools class i.e. magic line %retrieve_pkg_version and magic cell %%diagram"""
# Libraries
from sys import version as py_ver
from importlib.metadata import version
from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic)
from IPython.display import display, HTML, Markdown

# Modules
from jarvis.command_parser import get_hyperlink


@magics_class
class MagicTools(Magics):
    """Magic class"""
    def __init__(self, shell, generator):
        # You must call the parent constructor
        super().__init__(shell)
        self.generator = generator

    @staticmethod
    @line_magic
    def retrieve_pkg_version(_):
        """Magic line %retrieve_pkg_version that get dependecies versions, for users to share when
        they create issues"""
        pkg = ['ipython', 'lxml', 'notebook', 'plantuml', 'jarvis4se', 'pandas']
        pkg_ver = "\n".join(['=='.join(tups) for tups in list(zip(pkg, list(map(version, pkg))))])
        print(pkg_ver, f"\npython=={py_ver[:6]}")

    @cell_magic
    def diagram(self, _, cell):
        """Magic cell %%diagram """
        out = self.generator.get_diagram_url(cell, True)
        if out:
            hyper = get_hyperlink(out)
            display(HTML(hyper))
            print("Overview :")
            display(Markdown(f'![figure]({out})'))
