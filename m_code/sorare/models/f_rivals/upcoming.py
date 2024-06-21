from attrs import define
import cattrs
from context import file_func

# ========== see rivals_tactic.py ==========
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
class LineupPlayer:
    slug: str
    position: str
    cap_score: float
    id: str




@define
class RivalsGamePreGameInfo:
    """A representation of a rivals game"""
    cap: int
    lineup_tactics: list[TacticDefinition]
    home_lineup: list[LineupPlayer]
    home_bench: list[LineupPlayer]
    away_lineup: list[LineupPlayer]
    away_bench: list[LineupPlayer]

    def save_on_filessystem(self,filepath:str):
        file_name = filepath+"/pregame_info.json"

        file_func.write_json_to_file(
            filename=file_name,
            json_data=cattrs.unstructure(self)
        )

def create_lineups(game_details:dict,draftable_player_map:dict) -> tuple[
        list[LineupPlayer], # home lineup
        list[LineupPlayer], # home bench
        list[LineupPlayer], # away lineup
        list[LineupPlayer]  # away bench
    ]:

    def create_lineup_player(draftable_player_map:dict,game_det_entry:dict) -> LineupPlayer:
        for dp in draftable_player_map:
            if dp["player"]["slug"] == game_det_entry["slug"]:
                return LineupPlayer(
                    cap_score=dp["capValue"],
                    position=game_det_entry["position"],
                    slug=game_det_entry["slug"],
                    id=dp["id"]
                )
    home_bench_list = []
    home_lineup_list = []
    away_bench_list = []
    away_lineup_list = []
    for home_bench in game_details["homeFormation"]["bench"]:
        home_bench_list.append(create_lineup_player(draftable_player_map,home_bench))
    for away_bench in game_details["awayFormation"]["bench"]:
        away_bench_list.append(create_lineup_player(draftable_player_map,away_bench))
    for player_list in game_details["homeFormation"]["startingLineup"]:
        for player in player_list:
            home_lineup_list.append(create_lineup_player(draftable_player_map,player))
    for player_list in game_details["awayFormation"]["startingLineup"]:
        for player in player_list:
            away_lineup_list.append(create_lineup_player(draftable_player_map,player))
    return (home_lineup_list,home_bench_list,away_lineup_list,away_bench_list)
    
