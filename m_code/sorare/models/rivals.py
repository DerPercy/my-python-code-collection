from attrs import define
import cattrs
import os
import logging
from cattrs.gen import make_dict_unstructure_fn, override
from context import file_func

from .f_rivals.upcoming import RivalsGamePreGameInfo,TacticDefinition,create_lineups


# ==> see (and use) common.py
@define
class RivalsPlayerGameStatsScore:
    category: str
    points: float
    stat: str
    statValue: float
    totalScore: float


@define
class RivalsGamePlayerGameStats:
    home_team_slug: str
    rivals_game_slug: str
    away_team_slug: str
    gameweek: int
    start_date: str
    game_started: bool
    game_score: float
    detailed_score_list: list[RivalsPlayerGameStatsScore] = []

    def save_on_filessystem(self,filepath:str):
        file_name = filepath+"/info.json"
        file_func.write_json_to_file(
            filename=file_name,
            json_data=cattrs.unstructure(self)
        )

    def get_detailed_score_value(self,stat_key:str) -> float:
        """
        get the value of a detailed score based on the key
        """
        for dsl in self.detailed_score_list:
            if stat_key == dsl.stat:
                return dsl.totalScore
    def get_detailed_score_count(self,stat_key:str) -> float:
        """
        get the count of a detailed score based on the key
        """
        for dsl in self.detailed_score_list:
            if stat_key == dsl.stat:
                return dsl.statValue
        
    def get_detailed_score_keys(self) -> list[str]:
        return_list = []
        for dsl in self.detailed_score_list:
            return_list.append(dsl.stat)
        return return_list

def create_rivals_game_player_games_list_from_api_response(json:dict) -> list[RivalsGamePlayerGameStats]:
    result_list = []
    for game in json:
        if game["game"].get("rivalsGame",{}) == None:
            rivals_game_slug = ""
        else:    
            rivals_game_slug = game["game"].get("rivalsGame",{}).get("slug","")
        if game["game"]["so5Fixture"] == None:
            gameWeek = 0
            startDate = ""
        else:
            gameWeek = game["game"]["so5Fixture"]["gameWeek"]
            startDate = game["game"]["so5Fixture"]["startDate"]
        rg = RivalsGamePlayerGameStats(
            home_team_slug= game["game"]["homeTeam"]["slug"],
            away_team_slug= game["game"]["awayTeam"]["slug"],
            rivals_game_slug= rivals_game_slug,
            gameweek= gameWeek,
            start_date=startDate,
            game_started=(game["playerGameStats"].get("gameStarted",0) == 1),
            game_score=game["score"],
            detailed_score_list=cattrs.structure(game["detailedScore"],list[RivalsPlayerGameStatsScore])
        )
        result_list.append(rg)
    return result_list

@define
class RivalsGamePlayer:
    name: str
    slug: str
    position: str
    team_slug: str
    l15: float
    games_list: list[RivalsGamePlayerGameStats] = None

    def get_games(self)->list[RivalsGamePlayerGameStats]:
        pass
    def save_on_filessystem(self,filepath:str):
        for idx,game in enumerate(self.games_list):
            game_file_name = filepath+self.slug+"/"+"games/"+"{:04d}".format(idx)+"_"+game.rivals_game_slug+"/"
            game.save_on_filessystem(game_file_name)

        file_name = filepath+self.slug+"/info.json"
        c = cattrs.Converter()
        unst_hook = make_dict_unstructure_fn(RivalsGamePlayer, c, games_list=override(omit=True))
        c.register_unstructure_hook(RivalsGamePlayer, unst_hook)
        
        file_func.write_json_to_file(
            filename=file_name,
            json_data=c.unstructure(self)
        )
        
def create_rivals_game_player_list_from_api_response(json:dict) -> list[RivalsGamePlayer]:
    result_list = []
    
    for player in json:
        rgp = RivalsGamePlayer(
            name= player["name"],
            slug=player["slug"],
            position=player["position"],
            team_slug=player["teamSlug"],
            l15=player["l15"],
            games_list=create_rivals_game_player_games_list_from_api_response(player["unfilteredScores"])
        )
        result_list.append(rgp)
    return result_list

@define
class RivalsGame:
    """A representation of a rivals game"""
    name: str
    slug: str
    competition_slug: str
    date: str
    home_team_slug: str
    away_team_slug: str
    home_player: list[RivalsGamePlayer] = None
    away_player: list[RivalsGamePlayer] = None
    pre_game_info: RivalsGamePreGameInfo = None
    fs_location: str = None # location in Filesystem

    def get_home_player(self)-> list[RivalsGamePlayer]:
        pass

    def get_away_player(self)-> list[RivalsGamePlayer]:
        pass
    def save_on_filessystem(self,filepath:str):
        for player in self.home_player:
            player.save_on_filessystem(filepath=filepath+self.slug+"/player/")
        for player in self.away_player:
            player.save_on_filessystem(filepath=filepath+self.slug+"/player/")
        file_name = filepath+self.slug+"/info.json"

        c = cattrs.Converter()
        #unst_hook = make_dict_unstructure_fn(RivalsGame, c, home_player=override(omit=True))
        #c.register_unstructure_hook(RivalsGame, unst_hook)
        unst_hook = make_dict_unstructure_fn(RivalsGame, c, 
            away_player=override(omit=True),
            home_player=override(omit=True),
            pre_game_info=override(omit=True),
            fs_location=override(omit=True) 
        )
        c.register_unstructure_hook(RivalsGame, unst_hook)
        file_func.write_json_to_file(
            filename=file_name,
            json_data=c.unstructure(self)
        )
    def add_pre_game_info(self,game_info:dict,game_details:dict,draftable_player_map:dict):
        lineups = create_lineups(game_details=game_details, draftable_player_map=draftable_player_map)
        self.pre_game_info = RivalsGamePreGameInfo(
            cap=game_info["cap"],
            lineup_tactics=cattrs.structure(game_info["lineupTactics"],list[TacticDefinition]),
            home_lineup= lineups[0],
            home_bench=lineups[1],
            away_lineup=lineups[2],
            away_bench=lineups[3]
        )
        if self.fs_location == None:
            logging.error("Could not store RivalsPreGameInfo on Filesystem")
        else:
            self.pre_game_info.save_on_filessystem(self.fs_location)
        

def create_rivals_game_from_api_response(json:dict) -> RivalsGame:
    home_player = create_rivals_game_player_list_from_api_response(json["home"])
    away_player = create_rivals_game_player_list_from_api_response(json["away"])
    rg = RivalsGame(
        name= json["name"],
        slug=json["slug"],
        competition_slug=json["competitionSlug"],
        date=json["date"],
        away_player=away_player,
        home_player=home_player,
        home_team_slug=json["homeTeamSlug"],
        away_team_slug=json["awayTeamSlug"]
    )
    return rg

def read_rivals_game_from_fileSystem(filepath:str,game_slug:str) -> RivalsGame:
    def sub_read_player_from_fs(filepath:str,rg:RivalsGame):
        def sub_read_game_from_fs(filepath:str,rgp:RivalsGamePlayer):
            game_payload = file_func.read_json_from_file(filepath+"/info.json")
            rgpg = cattrs.structure(game_payload,RivalsGamePlayerGameStats)
            rgp.games_list.append(rgpg)
            
        payload = file_func.read_json_from_file(filepath+"/info.json")
        rgp = cattrs.structure(payload,RivalsGamePlayer)
        rgp.games_list = []
        files_dir = [
            f for f in os.listdir(filepath+"/games") if os.path.isdir(os.path.join(filepath+"/games", f))
        ]
        files_dir.sort()
        #logging.info(files_dir)
        
        for game_folder in files_dir:
            sub_read_game_from_fs(filepath+"/games/"+game_folder,rgp)
        if rgp.team_slug == rg.home_team_slug:
            rg.home_player.append(rgp)
        elif rgp.team_slug == rg.away_team_slug:
            rg.away_player.append(rgp)
        else:
            logging.error("Could not assign player because no teams slug matches")
    file_name = filepath+game_slug+"/info.json"
    payload = file_func.read_json_from_file(file_name)
    if payload.get("slug") != None:
        rg = cattrs.structure(payload,RivalsGame)
        rg.fs_location = filepath+game_slug
        rg.away_player = []
        rg.home_player = []
        # Read player
        files_dir = [
            f for f in os.listdir(filepath+game_slug+"/player") if os.path.isdir(os.path.join(filepath+game_slug+"/player", f))
        ]
        for player_slug in files_dir:
            player_filepath = filepath+game_slug+"/player/"+player_slug
            sub_read_player_from_fs(player_filepath,rg)
        #logging.info(files_dir)
        return rg
    
    return None