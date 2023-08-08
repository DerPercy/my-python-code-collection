from todoist_api_python.api import TodoistAPI, Task, Project, Comment
import logging

class ClientTask():
    def __init__(self, api: TodoistAPI, project: Project, task: Task = None, metadata_comment: Comment = None):
        self.api = api
        self.task = task
        self.title = task.content

        pass
    def set_metadata(self, metadata:dict):
        logging.error("set_metadata not implemented")
        logging.error(metadata)
        pass
    
    def set_title(self, title:str):
        self.title = title

    def save(self):
        logging.info("Save task")
        logging.info(self.title)
        
        if self.task is not None:
            logging.info("Task already exists: update")
            self.api.update_task(task_id=self.task.id, content=self.title)
        else:
            logging.info("New Task: create")
            logging.critical("Not implemented")
        
        pass

