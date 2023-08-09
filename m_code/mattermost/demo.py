import os
#from . import Client
import client
import json

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


cl = client.Client({
    'url': os.getenv('MATTERMOST_URL'),
    'token': os.getenv('MATTERMOST_TOKEN'),
    'port': 443,
    'assigneePropNames': ['Assignee']
})
tasks = cl.getTasks()
#print(json.dumps(tasks,indent=2))