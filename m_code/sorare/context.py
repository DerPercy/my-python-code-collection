import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../common')))

import file_func
from myjinja2 import myjinja2 as myjinja2
from handler.Coinstack import CoinStackHandler
from handler.AssetHandler import AssetHandler


