from mattermostdriver import Driver
import os
import requests
import json
import logging

class Client:

    def __init__(self, options=None):
        self.tasks = []
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

        r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v1/workspaces", headers=headers)
        logging.debug("Workspaces")
        logging.debug(r.json())
        workspaces = r.json()

        for workspace in workspaces:
            if workspace.get("boardCount",0) > 0:
                wsID = workspace.get("id")
                r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v1/workspaces/"+wsID+"/blocks?all=true", headers=headers)
                blocks = r.json()
                #print("==========")
                #print(json.dumps(blocks,indent=2))
                for block in blocks:
                    if block.get("type",None) == "card":
                        self.tasks.append(mm_task_to_client_task(workspace, block))
                    elif block.get("type",None) == "text": # Comments
                        #print(json.dumps(block,indent=2))
                        pass
                    elif block.get("type",None) == "board": # Board (with Property names)
                        #print(json.dumps(block,indent=2))
                        pass
                    else:
                        #print(block.get("type",None)+" not handled at the moment")
                        pass
    
    def getTasks(self):
        return self.tasks


def mm_task_to_client_task(workspace,mmTask):
    """ Convert Mattermost task structure to an internal task structure """
    logging.debug(json.dumps(mmTask,indent=2))
    task = {
        "title": mmTask.get("title",None),
        "workspace": workspace.get("title",None),
        "id": mmTask.get("id",None),
        "createAt":  mmTask.get("createAt",None),
        "updateAt": mmTask.get("updateAt",None),
        "deleteAt": mmTask.get("deleteAt",None),
    }
    return task