from ..models.team import Team
from ..models.category import Category
from ..models.board import Board
from ..task import Task

import requests
import logging
import attr

def fill_teams(base_url: str, headers: dict):

    teams = []
    r = requests.get("https://"+base_url+"/plugins/focalboard/api/v2/teams", headers=headers)
    #logging.debug("Teams")
    #logging.debug(r.content)
    teams_json = r.json()
    for team in teams_json:
        teams.append(Team(team.get("id",None)))
    return teams

def get_categories_from_team(base_url: str, headers: dict, team:Team) -> list[Category]:
    categories = []
    r = requests.get("https://"+base_url+"/plugins/focalboard/api/v2/teams/"+team.id+"/categories", headers=headers)
    for category in r.json():
        logging.info(category)
        category_model = Category(category.get("id",None),category.get("name",None))
        boards = []
        for board_meta in category.get("boardMetadata",[]):
            boards.append(get_board_by_id(base_url, headers,board_meta.get("boardID",None), category_model))
        category_model.boards = boards
        categories.append(category_model)
    logging.info(categories)
    return categories

def get_board_by_id(base_url: str, headers: dict, board_id:str, category: Category):
    #r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v2/boards/"+board_metadata.get("boardID",None), headers=headers)
    #logging.debug(json.dumps(r.json(),indent=2))               
    return Board(id=board_id, category_dict=attr.asdict(category))

def get_tasks_from_board(base_url: str, headers: dict, board:Board) -> list[Task]:
    tasks = []
    r = requests.get("https://"+base_url+"/plugins/focalboard/api/v2/boards/"+board.id+"/blocks?all=true", headers=headers)
    for block in r.json():
        if block.get("type",None) == "card":
            tasks.append(mm_task_to_client_task(board.category_dict.get("name",""), block))
        elif block.get("type",None) == "text": # Comments
            pass
        elif block.get("type",None) == "board": # Board (with Property names)
            pass
        else:
            pass
    return tasks

def mm_task_to_client_task(category_name:str, mmTask:dict):
    """ Convert Mattermost task structure to an internal task structure """
    #logging.debug(json.dumps(mmTask,indent=2))
    t = Task(
        project     = category_name, 
        title       = mmTask.get("title",None),
        id          = mmTask.get("id",None),
        createAt    = mmTask.get("createAt",None),
        updateAt    = mmTask.get("updateAt",None),
        deleteAt    = mmTask.get("deleteAt",None),
        icon        = mmTask.get("fields",{}).get("icon","")
    )
    #logging.info(t)
    return t