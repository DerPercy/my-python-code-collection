from todoist_api_python.api_async import TodoistAPIAsync
from todoist_api_python.api import TodoistAPI
import os



# Fetch tasks asynchronously
async def get_tasks_async():
    api = TodoistAPIAsync(os.getenv('TODOIST_API_KEY'))
    try:
        tasks = await api.get_tasks()
        print(tasks)
    except Exception as error:
        print(error)

get_tasks_async()
# Fetch tasks synchronously
def get_tasks_sync():
    api = TodoistAPI(os.getenv('TODOIST_API_KEY'))
    try:
        #tasks = api.get_tasks( filter="@PROJEKT" )
        tasks = api.get_tasks(  )
        print(tasks)
        for task in tasks:
            print(task.content)
            print(task.id)
        print(api.get_task("8431372168"))
    except Exception as error:
        print(error)
get_tasks_sync()