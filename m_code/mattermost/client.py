from mattermostdriver import Driver
from .task import Task
from .models.team import Team 

from .api import read as api_read
import os
import requests
import json
import logging

class Client:

    def __init__(self, options=None):
        self.tasks = []
        self.api_url = options.get("url")
        
        logging.debug(os.getenv('MATTERMOST_URL'))
        foo = Driver({ 
            'url': options.get("url"),
            'token': options.get("token"),
            'port': options.get("port"),
            'debug': False
        })

        foo.login()
        logging.debug(foo.client._token)

        userID = foo.client.userid
        logging.debug("My userID"+userID)

        headers = foo.client.auth_header()

        headers["X-Requested-With"] = "XMLHttpRequest"

        self.api_headers = headers

    def get_teams(self):
        return api_read.fill_teams(self.api_url,self.api_headers)

    def getTasks(self):
        tasks = []
        for team in self.get_teams():
            for category in api_read.get_categories_from_team(self.api_url,self.api_headers,team):
                for board in category.boards:
                    tasks.extend(api_read.get_tasks_from_board(self.api_url,self.api_headers,board))
        return tasks
