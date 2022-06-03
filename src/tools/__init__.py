#!/usr/bin/env python
from sys import version as py_ver
from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic)
from importlib.metadata import version
from plantuml_adapter import get_url_from_string
from IPython.display import display, HTML, Markdown
from jarvis.command_parser import get_hyperlink


@magics_class
class MagicTools(Magics):
    @line_magic
    def retrieve_pkg_version(self, _):
        """Get dependecies versions, for users to share when they create issues"""
        pkg = ['ipython', 'lxml', 'notebook', 'plantuml', 'jarvis4se', 'pandas']
        pkg_ver = "\n".join(['=='.join(tups) for tups in list(zip(pkg, list(map(version, pkg))))])
        print(pkg_ver, f"\npython=={py_ver[:6]}")
        return

    @cell_magic
    def diagram(self, _, cell):
        out = get_url_from_string(cell)
        if out:
            hyper = get_hyperlink(out)
            display(HTML(hyper))
            print("Overview :")
            display(Markdown(f'![figure]({out})'))
