from client import Client
from attrs import define
import logging, cattrs, json
    
@define
class RivalsGameAppearance:
    draftableObjectId: str
    captain:bool

def set_rivals_game_lineup(client:Client,game_id:str,player: list[RivalsGameAppearance], tactic_slug:str) -> None:
    params = {
        "input":{
            "gameId": game_id,
            "tacticSlug": tactic_slug,
            "joinArena": False,
            "appearances": cattrs.unstructure(player)
        }
    }
    body = """
mutation SetRivalsLineups($input: footballRivalsLineupUpsertInput! ){
  footballRivalsLineupUpsert(input: $input ) {
    errors {
      message
      code
    }
  }
}
"""
    #result = client.request(body,{},{ "resultSelector": ["data","footballRivalsLineupUpsert","errors"]   })
    logging.info("Set Lineup")
    result = client.request(body,params)
    logging.info("Result")
    logging.info(result)
