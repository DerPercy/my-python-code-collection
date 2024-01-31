import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print(os.path.join(os.path.dirname(__file__), '..'))
import m_code
import m_code.todoist as todoist
import m_code.sorare as sorare
import m_code.sorare.func_sorare_heroes as sorare_func_sorare_heroes

import m_code.clockify.clockify as clockify