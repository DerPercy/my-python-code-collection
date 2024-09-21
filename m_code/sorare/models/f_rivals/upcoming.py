from attrs import define
import cattrs
from context import file_func
import logging

log = logging.getLogger(__name__)

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
    name: str




@define
class RivalsGamePreGameInfo:
    """A representation of a rivals game"""
    cap: int
    lineup_tactics: list[TacticDefinition]
    home_lineup: list[LineupPlayer]
    home_bench: list[LineupPlayer]
    away_lineup: list[LineupPlayer]
    away_bench: list[LineupPlayer]

    def get_position_of_player(self,player_slug) -> str:
        for player in self.home_lineup:
            if player.slug == player_slug:
                return player.position
        for player in self.away_lineup:
            if player.slug == player_slug:
                return player.position
        logging.error("No position found for"+player_slug)

    def get_player_by_slug(self,player_slug) -> LineupPlayer:
        for player in self.home_lineup:
            if player.slug == player_slug:
                return player
        for player in self.away_lineup:
            if player.slug == player_slug:
                return player
        logging.error("No player found for"+player_slug)

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

    def create_lineup_player(draftable_player_map:dict,game_det_entry:dict,game_details:dict) -> LineupPlayer:
        for dp in draftable_player_map:
            if dp["player"]["slug"] == game_det_entry["slug"]:
                position = game_det_entry["position"]
                try:
                    #log.info("Position of player: "+position)
                    for formation in ["homeFormation","awayFormation"]:
                        for area in game_details[formation]["startingLineup"]:
                            for player in area:
                                if player["slug"] == game_det_entry["slug"]:
                                    if player["position"] != position:
                                        log.warning("Different positions found")
                                        log.warning("Old position:"+position)
                                        position = player["position"]
                                        log.warning("New position:"+position)
                except Exception as exc:
                    log.exception(exc)
                 
                #logging.info(game_details)
                return LineupPlayer(
                    cap_score=dp["capValue"],
                    position=position,
                    slug=game_det_entry["slug"],
                    id=dp["id"],
                    name=game_det_entry["displayName"]
                )
    home_bench_list = []
    home_lineup_list = []
    away_bench_list = []
    away_lineup_list = []
    for home_bench in game_details["homeFormation"]["bench"]:
        home_bench_list.append(create_lineup_player(draftable_player_map,home_bench,game_details))
    for away_bench in game_details["awayFormation"]["bench"]:
        away_bench_list.append(create_lineup_player(draftable_player_map,away_bench,game_details))
    for player_list in game_details["homeFormation"]["startingLineup"]:
        for player in player_list:
            home_lineup_list.append(create_lineup_player(draftable_player_map,player,game_details))
    for player_list in game_details["awayFormation"]["startingLineup"]:
        for player in player_list:
            away_lineup_list.append(create_lineup_player(draftable_player_map,player,game_details))
    return (home_lineup_list,home_bench_list,away_lineup_list,away_bench_list)
    
