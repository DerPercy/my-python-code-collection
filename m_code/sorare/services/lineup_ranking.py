"""
Lineup Ranking

Calculate the best lineup based on a list of players
"""

from attrs import define

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


""" 
========== FUNCTIONS ==========
"""

def calculate_best_lineup(players:list[Player],cap_limit:float) -> list[str]:
    """
    Returns a list of the player entity_data of the best lineup
    """
    player_list = []
    #print(players)
    max_score = 0
    for idx1, player1 in enumerate(players):
        for idx2, player2 in enumerate(players[(idx1+1):]):
            for idx3, player3 in enumerate(players[(idx1+idx2+2):]):
                for idx4, player4 in enumerate(players[(idx1+idx2+idx3+3):]):
                    for idx5, player5 in enumerate(players[(idx1+idx2+idx3+idx4+4):]):
                        try:
                            check_cap_requirement(player1,player2,player3,player4,player5,cap_limit)
                            score = get_lineup_score(player1,player2,player3,player4,player5)
                            #print(player1.entity_data+"->"+player2.entity_data+"->"+player3.entity_data+"->"+player4.entity_data+"->"+player5.entity_data)
                            #print(score)
                            if score > max_score:
                                player_list = [player1.entity_data,player2.entity_data,player3.entity_data,player4.entity_data,player5.entity_data]
                                max_score = score
                        except Exception as e:
                            #print(e)
                            # Invalid lineup: ignore
                            pass    
    #print(player_list)                    
    return player_list

def get_lineup_score(p1:Player,p2:Player,p3:Player,p4:Player,p5:Player) -> float:
    if not valid_lineup_position([p1.position,p2.position,p3.position,p4.position,p5.position]):
        raise Exception("Invalid position combination")
    return p1.score + p2.score + p3.score + p4.score + p5.score 
    

def valid_lineup_position(positions:list[str]) -> bool:
    """
    Checks, if the combination of plaer positions is valid
    """
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