from todoist_api_python.api import TodoistAPI, Task, Project, Comment
from .comment import get_comments_from_task, ClientComment

import logging

class ClientTask():
    def __init__(self, api: TodoistAPI, project: Project, task: Task = None ):
        self.api = api
        self.task = task
        self.metadata_comment = None
        self.project = project
        #self.title = task.content

        pass
    def set_metadata(self, metadata:dict):
        self.get_meta_data_comment().set_metadata(metadata)
    
    def set_title(self, title:str):
        self.title = title
    
    def get_meta_data_comment(self) -> ClientComment:
        if self.metadata_comment is not None:
            return self.metadata_comment
        if self.task == None: # No unterlying task
            self.metadata_comment = ClientComment(self.api)
            return self.metadata_comment
        c_comment_list = get_comments_from_task(self.api,self.task.id)
        for c_comment in c_comment_list:
            if c_comment.is_meta_data() is True:
                self.metadata_comment = c_comment
                return c_comment
        self.metadata_comment = ClientComment(self.api)
        return self.metadata_comment

    def save(self):
        logging.info("Save task")
        logging.info(self.title)
        
        if self.task is not None:
            logging.info("Task already exists: update")
            self.api.update_task(task_id=self.task.id, content=self.title)
        else:
            logging.info("New Task: create")
            new_task = self.api.add_task( project_id=self.project.id, content=self.title)
            logging.info(new_task)
            if self.metadata_comment is not None:
                logging.info("Add new task id to comment")
                self.metadata_comment.set_task_id( new_task.id)

        if self.metadata_comment is not None:
            logging.info("Also save Metadata comment")
            self.metadata_comment.save()
        pass

