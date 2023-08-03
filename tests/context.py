import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print(os.path.join(os.path.dirname(__file__), '..'))
import m_code
import m_code.todoist as todoist