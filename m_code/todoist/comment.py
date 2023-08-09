from todoist_api_python.api import TodoistAPI, Task, Comment
import logging
import re
import json

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


class ClientComment:
    def __init__(self, api: TodoistAPI, data: dict = {}):
        self.comment_data = data
        self.task_id = None
        self.api = api
        
    def is_meta_data(self):
        return self.get_meta_data() != None

    def get_content(self):
        return self.comment_data.get("content","")

    def get_meta_data(self):
        return get_comment_meta_data(self.get_content())
    def get_meta_data_value(self,key:str):
        md = get_comment_meta_data(self.get_content())
        if md is None:
            return None 
        return md.get(key,None)
    def set_metadata(self, metadata:dict):
        self.comment_data["content"] = create_todoist_comment_from_meta_data(metadata)
        
    def set_task_id(self,taskid):
        self.task_id = taskid

    def save(self):
        logging.info("Save comment")
        if self.comment_data.get("id",None) is None:
            logging.info("No comment ID: create")
            self.comment_data = addComment(self.api, self.task_id, self.get_content())
        else:
            logging.info("comment ID exists: update")
            self.comment_data = updateComment(self.api, self.comment_data)


def create_todoist_comment_from_meta_data(meta_data:dict) -> str:
    content = "`"+json.dumps(meta_data,indent=2)+"`"
    return content

def create_comment_from_todoist(todoist_comment):
    logging.debug(todoist_comment)
    metadata = get_comment_meta_data(todoist_comment.get("content"))
    return ClientComment(todoist_comment.get("content"), metadata)

def get_comment_meta_data(content):
    """
    Get Metadata of a todoist comment
    Metadata is a codeblock with json
    """
    logging.debug("Check if comment is metadata:"+content)
    x = re.search(r"^[\s]*`(.*)`[\s]*$", content,re.DOTALL) #re.DOTALL to allow line breaks in JSON
    if x is not None:
        data = x.groups()[0]
        logging.debug("comment matches pattern. Result:"+data)
        try:
            datajson = json.loads(data)
            logging.debug("result is json. Is metadata")
            logging.debug(datajson)
            return datajson
        except json.decoder.JSONDecodeError:
            logging.debug('result is no json')
    else:
        logging.debug("comment did not match pattern")
    return None

def get_comments_from_task(api: TodoistAPI, task_id: str):
    """As an error in default API, use a workaround"""
    endpoint = get_rest_url(COMMENTS_ENDPOINT)
    comments = get(api._session, endpoint, api._token, { "task_id": task_id } )
    client_comments = []
    for comment in comments:
        c_comment = ClientComment(api, comment)
        client_comments.append(c_comment)
    logging.debug(client_comments)
    return client_comments

def addComment(api: TodoistAPI, task_id:str, content:str):
    payload = {
        "task_id": task_id,
        "content": content
    }
    endpoint = get_rest_url(COMMENTS_ENDPOINT)
    return post(api._session, endpoint, api._token, payload)
        
def updateComment(api: TodoistAPI, comment_data:dict):
    #logging.info("Update comment")
    #logging.info(comment_data)
    endpoint = get_rest_url(COMMENTS_ENDPOINT+"/"+comment_data.get("id",None))
    return post(api._session, endpoint, api._token, comment_data)
        