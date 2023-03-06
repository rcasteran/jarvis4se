""" @package tools
Tooling module

Defines the following classes that provides tooling features used by Jarvis:
- @ref MagicTools which defines magic line and cell for IPython interface
- @ref Logger which defines the logging mechanism
- @ref Config which defines the configuration mechanism

Provides the following utilities:
- @ref get_hyperlink to covert file path into HTML link

Provides the Jarvis console : @ref main
"""

from .util import get_hyperlink
from .magic_tools import MagicTools
from .config import Config
from .logger import Logger
