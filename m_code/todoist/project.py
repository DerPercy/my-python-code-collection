from todoist_api_python.api import TodoistAPI, Project
from todoist_api_python.http_requests import delete, get, post
from todoist_api_python.endpoints import (
    COLLABORATORS_ENDPOINT,
    COMMENTS_ENDPOINT,
    LABELS_ENDPOINT,
    PROJECTS_ENDPOINT,
    QUICK_ADD_ENDPOINT,
    SECTIONS_ENDPOINT,
    SHARED_LABELS_ENDPOINT,
    SHARED_LABELS_REMOVE_ENDPOINT,
    SHARED_LABELS_RENAME_ENDPOINT,
    TASKS_ENDPOINT,
    get_rest_url,
    get_sync_url,
)
from .task import ClientTask
from .exception import ClientException
from .comment import create_comment_from_todoist, create_todoist_comment_from_meta_data
import logging

class ClientProject():
    api: TodoistAPI
    def __init__(self, api: TodoistAPI, project: Project):
        self.api = api
        self.project = project
    
    def create_task(self) -> ClientTask:
        return ClientTask(self.api,self.project) 

    def get_task_by_meta_data(self, key:str, id:str) -> ClientTask:
        logging.info("Looking for task with metadata:"+key+"="+id)
        tasks = self.api.get_tasks( project_id=self.project.id)
        
        for task in tasks:
            logging.debug(task)
            c_task = ClientTask(self.api, self.project, task)
            meta_data_comment = c_task.get_meta_data_comment()
            if meta_data_comment is not None:
                if meta_data_comment.get_meta_data_value(key) == id:
                    logging.info("Task found")
                    return c_task
        logging.info("No task found")
        return None
    
    def add_task(self, title:str, meta_data: dict):
        logging.info("Create task in todoist")
        new_task = self.api.add_task(
            content=title,
            project_id=self.project.id
        )
        if new_task is not None:
            self.myAddComment(new_task.id,create_todoist_comment_from_meta_data(meta_data))

        #raise ClientException('add_task not implemented yet')
    
    def myAddComment(self, task_id:str, content:str):
        payload = {
            "task_id": task_id,
            "content": content
        }
        endpoint = get_rest_url(COMMENTS_ENDPOINT)
        post(self.api._session, endpoint, self.api._token, payload)
        pass
    def myGetComments(self, **kwargs):
        """As an error in default API, use a workaround"""
        endpoint = get_rest_url(COMMENTS_ENDPOINT)
        comments = get(self.api._session, endpoint, self.api._token, kwargs)
        client_comments = []
        for comment in comments:
            client_comments.append(create_comment_from_todoist(comment))
        logging.debug(client_comments)
        return client_comments