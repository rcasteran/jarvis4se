"""@defgroup tools
Tooling module
"""

# Libraries
from sys import version as py_ver
from importlib.metadata import version
from IPython.core.magic import (Magics, magics_class, cell_magic, line_magic)
from IPython.display import display, HTML, Markdown

# Modules
from .util import get_hyperlink


@magics_class
class MagicTools(Magics):
    """@ingroup tools
    @anchor MagicTools
    Magic call for IPython interface
    """

    def __init__(self, shell, generator, simulator):
        """
        @var generator
        Jarvis diagram generator
        """

        # You must call the parent constructor
        super().__init__(shell)
        self.generator = generator
        self.simulator = simulator

    @staticmethod
    @line_magic
    def retrieve_pkg_version(_):
        """Magic line that get Jarvis dependencies versions
        @return None
        """
        package_list = ['ipython', 'lxml', 'notebook', 'plantuml', 'jarvis4se', 'pandas', 'requests', 'nltk', 'PyZMQ',
                        'OMPython']
        package_version_list = ""
        for package in package_list:
            try:
                package_version = version(package)
            except ModuleNotFoundError:
                package_version = "Not found"
            package_version_list = package_version_list + f'\n{package}=={package_version}'

        print(package_version_list, "\npython=={}".format(py_ver[:6]))

    @cell_magic
    def diagram(self, _, cell):
        """Magic cell that allows to call directly Jarvis diagram generator
        @param[in] cell cell instance
        @param[in] _ not used
        @return None
        """
        out = self.generator.get_diagram_url(cell, True)
        if out:
            hyper = get_hyperlink(out)
            display(HTML(hyper))
            # Single display (not related to logging)
            print("Overview :")
            display(Markdown(f'![figure]({out})'))
