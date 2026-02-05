""" @defgroup xml_adapter
Module for 3SE xml parsing and writing
"""
from .xml_writer import XmlWriter3SE
from .xml_parser import XmlParser3SE
from .xml_parser import XmlDictKeyListForObjects
from .xml_parser import XmlDictKeyListForTypeIndex
from .xml_parser import XmlDictKeyDictForObjectBaseTypes
from .util import XML_DICT_KEY_0_DATA_LIST
from .util import XML_DICT_KEY_1_FUNCTION_LIST
from .util import XML_DICT_KEY_2_FUN_ELEM_LIST
from .util import XML_DICT_KEY_3_FUN_INTF_LIST
from .util import XML_DICT_KEY_4_PHY_ELEM_LIST
from .util import XML_DICT_KEY_5_PHY_INTF_LIST
from .util import XML_DICT_KEY_6_STATE_LIST
from .util import XML_DICT_KEY_7_TRANSITION_LIST
from .util import XML_DICT_KEY_8_REQUIREMENT_LIST
from .util import XML_DICT_KEY_9_GOAL_LIST
from .util import XML_DICT_KEY_10_ACTIVITY_LIST
from .util import XML_DICT_KEY_11_INFORMATION_LIST
from .util import XML_DICT_KEY_12_ATTRIBUTE_LIST
from .util import XML_DICT_KEY_13_VIEW_LIST
from .util import XML_DICT_KEY_14_TYPE_LIST
from .util import XML_DICT_KEY_15_FUN_CONS_LIST
from .util import XML_DICT_KEY_16_FUN_PROD_LIST
from .util import XML_DICT_KEY_17_ACT_CONS_LIST
from .util import XML_DICT_KEY_18_ACT_PROD_LIST
