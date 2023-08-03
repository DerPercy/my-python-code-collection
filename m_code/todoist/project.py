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
from .comment import create_comment_from_todoist

class ClientProject():
    def __init__(self, api: TodoistAPI, project: Project):
        self.api = api
        self.project = project

    def get_task_by_external_id(self, id:str) -> ClientTask:
        tasks = self.api.get_tasks( project_id=self.project.id)
        
        for task in tasks:
            print(task)
            if task.comment_count > 0:
                print('========== Comments ==========')
                print(task.id)

                self.myGetComments(task_id = task.id)

                #comments = self.api.get_comments( task_id = task.id )
                #comments = self.api.get_comments( )
                #print(comments)
            
        #raise ClientException('Task with id '+id+' not found')
        raise ClientException('get_task_by_external_id  not implemented yet')
    def myGetComments(self, **kwargs):
        """As an error in default API, use a workaround"""
        endpoint = get_rest_url(COMMENTS_ENDPOINT)
        comments = get(self.api._session, endpoint, self.api._token, kwargs)
        client_comments = []
        for comment in comments:
            client_comments.append(create_comment_from_todoist(comment))
        print(client_comments)