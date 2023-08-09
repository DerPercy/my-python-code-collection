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

        r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v2/teams", headers=headers)
        logging.debug("Teams")
        logging.debug(r.content)
        teams = r.json()

        for team in teams:
            logging.debug(" ========== Team "+team.get("title","")+" ==========")
            r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v2/teams/"+team.get("id",None)+"/boards", headers=headers)
            logging.debug("Boards:")
            logging.debug(json.dumps(r.json(),indent=2))
            
            r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v2/teams/"+team.get("id",None)+"/categories", headers=headers)
            logging.debug("Categories of Team "+team.get("title",None))
            logging.debug(json.dumps(r.json(),indent=2))

            for category in r.json():
                for board_metadata in category.get("boardMetadata",[]):
                    r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v2/boards/"+board_metadata.get("boardID",None)+"/blocks?all=true", headers=headers)
                    logging.debug("Blocks")
                    #logging.debug(r.content)      
                    blocks = r.json()
                    #print("==========")
                    #print(json.dumps(blocks,indent=2))
                    for block in blocks:
                        if block.get("type",None) == "card":
                            self.tasks.append(mm_task_to_client_task(category.get("name",""), block))
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


def mm_task_to_client_task(workspaceName,mmTask):
    """ Convert Mattermost task structure to an internal task structure """
    logging.debug(json.dumps(mmTask,indent=2))
    task = {
        "title": mmTask.get("title",None),
        "icon": mmTask.get("fields",{}).get("icon",""),
        "workspace": workspaceName,
        "id": mmTask.get("id",None),
        "createAt":  mmTask.get("createAt",None),
        "updateAt": mmTask.get("updateAt",None),
        "deleteAt": mmTask.get("deleteAt",None),
    }
    return task