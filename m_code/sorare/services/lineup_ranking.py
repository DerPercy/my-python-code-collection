"""
Lineup Ranking

Calculate the best lineup based on a list of players
"""

from attrs import define
from . import rivals_tactic
import logging
from icecream import ic

#from models.rivals import RivalsGame

""" 
========== MODELS ========== 
"""
@define
class Player:
    """A representation of a player"""
    entity_data: dict
    position: str #G,D,M,F
    cap_score: float
    score: float
    detailed_score_list: list[rivals_tactic.PlayerDetailedScore] = []
    home_away: str = None # "home" or "away" or None


""" 
========== FUNCTIONS ==========
"""

class LineupCheck:
    def lineupMatches(self,players:list[Player]):
        pass

class LineupCheckGoalkeeperHome(LineupCheck):
    def lineupMatches(self, players: list[Player]):
        for player in players:
            if player.position == 'G':
                if player.home_away == None:
                    return None
                return player.home_away == "home"
        return None

class LineupCheckNumberPlayerInTeam(LineupCheck):
    home_away = None
    num_player = None
    def __init__(self, home_away:str, num_player:int) -> None:
        super().__init__()
        self.home_away = home_away
        self.num_player = num_player

    def lineupMatches(self, players: list[Player]):
        calc_num_player = 0
        for player in players:
            if player.home_away == self.home_away:
                calc_num_player = calc_num_player + 1
        if calc_num_player == self.num_player:
            return True
        return None


class LineupCheckGKAndDefSameTeam(LineupCheck):
    def lineupMatches(self, players: list[Player]):
        gk_team = None
        def_team = None
        for player in players:
            if player.position == 'G':
                gk_team = player.home_away
            if player.position == 'D':
                def_team = player.home_away
            if gk_team != None and def_team != None:
                return gk_team == def_team
            
        return None

def calculate_best_lineup(players:list[Player],cap_limit:float, tactic_def_list: list[rivals_tactic.TacticDefinition] = None) -> tuple[list[str],str]:
    """
    Returns a list of the player entity_data of the best lineup
    """
    player_list = []
    tactic_slug = None
    #print(players)
    max_score = 0
    max_tactic_slug = None
    max_captain = None
    for idx1, player1 in enumerate(players):
        for idx2, player2 in enumerate(players[(idx1+1):]):
            for idx3, player3 in enumerate(players[(idx1+idx2+2):]):
                for idx4, player4 in enumerate(players[(idx1+idx2+idx3+3):]):
                    for idx5, player5 in enumerate(players[(idx1+idx2+idx3+idx4+4):]):
                        try:

                            check_cap_requirement(player1,player2,player3,player4,player5,cap_limit)
                            captain = get_lineup_captain(player1,player2,player3,player4,player5)
                            score = get_lineup_score(player1,player2,player3,player4,player5,captain)
                            tactics_score = 0
                            #logging.info("Score "+str(score)+" found")
                            if tactic_def_list != None:
                                tactics_result = get_tactics_score(player1,player2,player3,player4,player5,tactic_def_list)
                                tactic_slug = tactics_result[1]
                                tactics_score = tactics_result[0]
                                score = score + tactics_score
                            if score > max_score:
                                
                                player_list = [player1.entity_data,player2.entity_data,player3.entity_data,player4.entity_data,player5.entity_data]
                                max_score = score
                                max_tactic_slug = tactic_slug
                                max_captain =captain.entity_data
                        except Exception as e:
                            #logging.info(e)
                            pass    
    return (player_list,        # List of players in mx lineup
            max_tactic_slug,    # Slug of the best tactic
            max_captain,        # The captain
            max_score           # the score of the lineup
    )


def get_tactics_score(p1:Player,p2:Player,p3:Player,p4:Player,p5:Player,tdl:list[rivals_tactic.TacticDefinition]) -> tuple[float,str]:
    max_score = 0
    tactic_slug = "???"
    for tactic in tdl:
        tactic_score = 0
        pds = rivals_tactic.get_detailed_score_by_tactic_stat(p1.detailed_score_list,tactic.stat)
        if pds != None:
            tactic_score = tactic_score + pds.statValue
        pds = rivals_tactic.get_detailed_score_by_tactic_stat(p2.detailed_score_list,tactic.stat)
        if pds != None:
            tactic_score = tactic_score + pds.statValue
        pds = rivals_tactic.get_detailed_score_by_tactic_stat(p3.detailed_score_list,tactic.stat)
        if pds != None:
            tactic_score = tactic_score + pds.statValue
        pds = rivals_tactic.get_detailed_score_by_tactic_stat(p4.detailed_score_list,tactic.stat)
        if pds != None:
            tactic_score = tactic_score + pds.statValue
        pds = rivals_tactic.get_detailed_score_by_tactic_stat(p5.detailed_score_list,tactic.stat)
        if pds != None:
            tactic_score = tactic_score + pds.statValue
        th_score = rivals_tactic.get_threshold_score(tactic_score,tactic)
        if th_score >= max_score:
            max_score = th_score
            tactic_slug = tactic.slug
    return [max_score,tactic_slug]

def get_lineup_score(p1:Player,p2:Player,p3:Player,p4:Player,p5:Player, captain: Player) -> float:
    if not valid_lineup_position([p1.position,p2.position,p3.position,p4.position,p5.position]):
        raise Exception("Invalid position combination")
    return p1.score + p2.score + p3.score + p4.score + p5.score  + ( captain.score * 0.2 )

def get_lineup_captain(p1:Player,p2:Player,p3:Player,p4:Player,p5:Player) -> dict:
    captain = p1
    if p2.score > captain.score:
        captain = p2
    if p3.score > captain.score:
        captain = p3
    if p4.score > captain.score:
        captain = p4
    if p5.score > captain.score:
        captain = p5
    return captain 


def valid_lineup_position(positions:list[str]) -> bool:
    """
    Checks, if the combination of plaer positions is valid
    """
    #logging.info(positions)
    if positions.count("G") != 1: # Only one Goalkeeper
        return False
    if positions.count("D") < 1 or positions.count("D") > 2: # One or two Defender
        return False
    if positions.count("M") < 1 or positions.count("M") > 2: # One or two Midfielder
        return False
    if positions.count("F") < 1 or positions.count("F") > 2: # One or two Forwards
        return False
    return True

def check_cap_requirement(p1:Player,p2:Player,p3:Player,p4:Player,p5:Player,cap: float) -> None:
    if p1.cap_score + p2.cap_score + p3.cap_score + p4.cap_score + p5.cap_score > cap:
        raise Exception("Too expensive")

""" 
========== FACTORIES ==========
"""
