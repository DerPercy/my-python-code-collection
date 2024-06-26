from attrs import define
import cattrs

from models.f_rivals.common import RivalsPlayerGameStatsScore

@define
class RivalsGameLineupPlayer:
    """A representation of a rivals game post game result"""
    player_slug:str
    player_score: float
    picture_url: str
    player_position: str
    is_captain: bool
    

@define
class RivalsGameLineup:
    """A representation of a rivals game post game result"""
    player_list: list[RivalsGameLineupPlayer]
    total_score: float
    tactic_slug: str


@define
class RivalsGamePlayerScore:
    """A representation of a rivals game post game result"""
    player_slug: str
    score: float
    detailed_score_list: list[RivalsPlayerGameStatsScore] = []

@define
class RivalsGamePostGameInfo:
    """A representation of a rivals game post game result"""
    game_id: str
    my_lineup: RivalsGameLineup
    opp_lineup: RivalsGameLineup
    player_scores: list[RivalsGamePlayerScore]
