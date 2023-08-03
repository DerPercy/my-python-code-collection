from mattermost import Client as MMClient
from todoist import Client as TDClient
from todoist import ClientException as TodoistException
#from .code.mattermost import Client
import os
import json

mm_client = MMClient({
    'url': os.getenv('MATTERMOST_URL'),
    'token': os.getenv('MATTERMOST_TOKEN'),
    'port': 443,
    'assigneePropNames': ['Assignee']
})

mm_tasks = mm_client.getTasks();
print(json.dumps(mm_tasks,indent=2))

todoist_client = TDClient({
    'apiKeyClient': os.getenv('TODOIST_API_KEY')
})

try:
    t_project = todoist_client.get_project("Mattermost")
    for mm_task in mm_tasks:
        t_task = t_project.get_task_by_external_id(mm_task.get("id"))
except TodoistException as err:
    print(err)
