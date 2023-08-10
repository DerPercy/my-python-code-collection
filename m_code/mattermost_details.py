from mattermost import Client as MMClient

import os
import json

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


mm_client = MMClient({
    'url': os.getenv('MATTERMOST_URL'),
    'token': os.getenv('MATTERMOST_TOKEN'),
    'port': 443,
    'assigneePropNames': ['Assignee']
})

#logging.info(mm_client.get_teams())
mm_tasks = mm_client.getTasks();
#logging.debug(mm_tasks)
