from mattermost import Client as MMClient
from todoist import Client as TDClient
from todoist import ClientTask as TDTask
from todoist import ClientException as TodoistException
#from .code.mattermost import Client
import os
import json

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def update_todoist_task_from_mm(td_task: TDTask, mm_task: dict ):
    """
    Updates a Todoist task based on a Mattermost task
    Returns, if the todoist task needs to be updated in Todoist
    """
    
    meta_data = {
        "mm_id": mm_task.id,
        "mm_updateAt": mm_task.updateAt
    }
    td_task.set_metadata( meta_data )
    td_task.set_title("["+mm_task.project+"] "+mm_task.icon+ "" +mm_task.title)
    #t_project.add_task("["+mm_task.get("workspace")+"]"+mm_task.get("title"),meta_data)
    
    return True

mm_client = MMClient({
    'url': os.getenv('MATTERMOST_URL'),
    'token': os.getenv('MATTERMOST_TOKEN'),
    'port': 443,
    'assigneePropNames': ['Assignee']
})

mm_tasks = mm_client.getTasks()
logging.debug(mm_tasks)


todoist_client = TDClient({
    'apiKeyClient': os.getenv('TODOIST_API_KEY')
})

try:
    t_project = todoist_client.get_project("Mattermost")
    for mm_task in mm_tasks:
        t_task = t_project.get_task_by_meta_data("mm_id",mm_task.id)
        if t_task is None:
            logging.info("No task at todoist found -> create one")
            t_task = t_project.create_task( )
        
        if update_todoist_task_from_mm(t_task,mm_task) == True:
            t_task.save()
           
            

except TodoistException as err:
    logging.error(err)
