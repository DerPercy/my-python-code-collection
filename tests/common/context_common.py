import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

print(os.path.join(os.path.dirname(__file__), '..'))
import m_code
from m_code.common.hash_map import MyHashMap
from m_code.common.hash_map import prepare_converter
from m_code.common.value_aggregator import MyValueAggregator