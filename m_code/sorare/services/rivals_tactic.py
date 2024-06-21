"""
Rivals tactics models and service functions
"""

from attrs import define
from icecream import ic

""" 
========== MODELS ========== 
"""
# ========== see models/f_rivals/upcoming.py ==========

@define
class TacticDefinitionThreshold:
    """A representation of a tactic definition treshold"""
    score: int
    threshold: int

@define
class TacticDefinition:
    """A representation of a tactic definition"""
    stat: str
    slug: str
    displayName: str
    thresholds: list[TacticDefinitionThreshold]


@define
class PlayerDetailedScore:
    """A representation of a player detailed score"""
    stat: str
    statValue:int

""" 
========== FUNCTIONS ==========
"""

def get_detailed_score_by_tactic_stat(pdsl:list[PlayerDetailedScore],tactic_stat:str) -> PlayerDetailedScore:
    
    for pds in pdsl:
        if pds.stat == tactic_stat:
            return pds
    return None

def get_threshold_score(score:float,tactic_def:TacticDefinition) -> float:
    max_score = 0
    for threshold in tactic_def.thresholds:
        if score >= threshold.threshold and threshold.score > max_score:
            max_score = threshold.score
    return max_score
""" 
========== FACTORIES ==========
"""

def build_player_detailed_score_from_api_response(api_response:dict) -> list[PlayerDetailedScore]:
    det_score_list = []
    for det_score in api_response:
        det_score_list.append(PlayerDetailedScore(stat=det_score["stat"], statValue=det_score["statValue"]))

    return det_score_list
def build_tactic_from_api_response(api_response:dict) -> TacticDefinition:
    th_list = []
    for api_th in api_response["thresholds"]:
        th_list.append(TacticDefinitionThreshold(score=api_th["score"],threshold=api_th["threshold"]))
    return TacticDefinition(stat=api_response["stat"],displayName=api_response["displayName"],thresholds=th_list,slug=api_response["slug"])

def build_tactic_list_from_api_response(api_response:list[dict]) -> list[TacticDefinition]:
    tactics_list = []
    for api_resp in api_response:
        tactics_list.append(build_tactic_from_api_response(api_resp))
    return tactics_list

""" 
========== CONVERTER ==========
"""

def conv_player_detailed_scores_to_object(player_det_score_list:list[PlayerDetailedScore]) -> dict:
    ret_obj = {}
    for pds in player_det_score_list:
        ret_obj[pds.stat] = pds.statValue
    return ret_obj

def conv_object_to_player_detailed_scores(obj:dict) -> list[PlayerDetailedScore]:
    ret_list = []
    for pds in obj:
        ret_list.append(PlayerDetailedScore(
            stat=pds,
            statValue=obj[pds]
        ))
    return ret_list
