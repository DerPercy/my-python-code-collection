from api_rivals_mutations import RivalsGameAppearance, set_rivals_game_lineup

from client import Client as SorareClient
import logging, logging.handlers
import os
from dotenv import load_dotenv
import argparse, sys
import api_schema


'''
Initializing
'''
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--logfile", help="Specify the logfile destination")
#parser.add_argument("--lineupfile", help="Specify the players, which should be used for lineups")
#parser.add_argument("--joinarena", help="If 'X' join the arena")
#parser.add_argument("--settingsfile", help="Path of the game settings")

args = parser.parse_args()

log_handlers = []
log_handlers.append(logging.StreamHandler(sys.stdout))
if args.logfile != None:
    log_handlers.append(logging.handlers.RotatingFileHandler(
        #args.logfile, maxBytes=(1048576*5), backupCount=7))
        args.logfile, maxBytes=(104857*5), backupCount=7))


# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',handlers=log_handlers)


# Environment variables
load_dotenv()


'''
Logic start
'''
logging.info("Starting sorare_rivals_upcoming.py")

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})


######### Classes ##########
class LineupCalculationPlayer():
    def __init__(self, score_list:list[api_schema.So5Score], draftable_player:api_schema.FootballRivalsDraftableObjectInterface, home_away:str) -> None:
        self.draftable_player = draftable_player
        self.score_list = score_list
        self.home_away = home_away
    def get_position(self) -> str:
        return str(self.draftable_player.value_position)
    def get_cap_value(self) -> float:
        return self.draftable_player.value_capValue
    def get_predicted_tactic_value(self,tactic_stat:str) -> float:
        #logging.info("Get tactic score ("+ tactic_stat + ") of "+str(self.draftable_player.value_player.value_slug))
        value = 0
        if len(self.score_list) == 0:
            #logging.info("Empty score list")
            return 0
        for score in self.score_list:
            for det_score in score.value_detailedScore:
                if det_score.value_stat == tactic_stat:
                    #logging.info("Add "+str(det_score.value_statValue))
                    value = value + det_score.value_statValue
        result = value / len(self.score_list)
        #logging.info("Result:" + str(result))
        return result
    
    def get_predicted_score(self) -> float:
        if len(self.score_list) < 3: #  At least 3 scores
            return 0
        total_score:float = 0
        for score in self.score_list:
            total_score = total_score + score.value_score
        return total_score / len(self.score_list)
    def get_name(self):
        return self.draftable_player.value_player.value_slug 
    def get_id(self) -> str:
        return self.draftable_player.value_id

class Lineup():
    captain: LineupCalculationPlayer | None = None
    tactic_slug = None
    tactic_score = 0
    missions = None
    def __init__(self, player1:LineupCalculationPlayer, player2:LineupCalculationPlayer, player3: LineupCalculationPlayer, player4: LineupCalculationPlayer, player5:LineupCalculationPlayer,tactics:list[api_schema.FootballRivalsLineupTactic],missions:list[dict]):
        self.player1 = player1
        self.player2 = player2
        self.player3 = player3
        self.player4 = player4
        self.player5 = player5
        self.tactics = tactics
        self.tactic_slug = None
        self.tactic_score = 0
        self.missions = missions

    
    def valid_positions(self) -> bool:
        pos_list:list[str] = []
        pos_list.append(self.player1.get_position()[0])
        pos_list.append(self.player2.get_position()[0])
        pos_list.append(self.player3.get_position()[0])
        pos_list.append(self.player4.get_position()[0])
        pos_list.append(self.player5.get_position()[0])
        team_list:list[str] = []
        team_list.append(self.player1.home_away)
        team_list.append(self.player2.home_away)
        team_list.append(self.player3.home_away)
        team_list.append(self.player4.home_away)
        team_list.append(self.player5.home_away)
        for mission in self.missions:
            if mission.get("homeTeamMin",None) != None:
                if team_list.count("home") < mission.get("homeTeamMin",None):
                    return False
                if team_list.count("away") < mission.get("awayTeamMin",None):
                    return False
        if pos_list.count("G") != 1: # Only one Goalkeeper
            return False
        if pos_list.count("D") < 1 or pos_list.count("D") > 2: # One or two Defender
            return False
        if pos_list.count("M") < 1 or pos_list.count("M") > 2: # One or two Midfielder
            return False
        if pos_list.count("F") < 1 or pos_list.count("F") > 2: # One or two Forwards
            return False
        return True

    def met_cap(self, cap_value: float) -> bool:
        return cap_value >= self.player1.get_cap_value() + self.player2.get_cap_value() + self.player3.get_cap_value() + self.player4.get_cap_value() + self.player5.get_cap_value()

    def calculate_tactics(self):
        for tactic in self.tactics:
            stat_count = 0
            if self.tactic_slug == None:
                self.tactic_slug = tactic.value_slug
            stat_count = self.player1.get_predicted_tactic_value(tactic.value_stat)
            stat_count = stat_count + self.player2.get_predicted_tactic_value(tactic.value_stat)
            stat_count = stat_count + self.player3.get_predicted_tactic_value(tactic.value_stat)
            stat_count = stat_count + self.player4.get_predicted_tactic_value(tactic.value_stat)
            stat_count = stat_count + self.player5.get_predicted_tactic_value(tactic.value_stat)
            for th in tactic.value_thresholds:
                if th.value_score > self.tactic_score and th.value_threshold < stat_count:
                    self.tactic_score = th.value_score
                    self.tactic_slug = tactic.value_slug
        
    def get_tactic_score(self) -> float:
        if self.tactic_slug == None:
            self.calculate_tactics()
        return self.tactic_score
    def get_tactic_slug(self) -> str:
        if self.tactic_slug == None:
            self.calculate_tactics()
        return self.tactic_slug
    
    def get_predicted_score(self) -> float:
        score:float = 0
        score = score + self.player1.get_predicted_score()
        score = score + self.player2.get_predicted_score()
        score = score + self.player3.get_predicted_score()
        score = score + self.player4.get_predicted_score()
        score = score + self.player5.get_predicted_score()
        # Calculate tactics
        score = score + self.get_tactic_score()            
        return score    
    def get_captain(self) -> LineupCalculationPlayer | None:
        if self.captain == None:
            self.captain = self.player1
            if self.captain.get_predicted_score() < self.player2.get_predicted_score():
                self.captain = self.player2
            if self.captain.get_predicted_score() < self.player3.get_predicted_score():
                self.captain = self.player3
            if self.captain.get_predicted_score() < self.player4.get_predicted_score():
                self.captain = self.player4
            if self.captain.get_predicted_score() < self.player5.get_predicted_score():
                self.captain = self.player5
        return self.captain
    def get_appearances(self) -> list[api_schema.FootballRivalsAppearanceInput]:
        ret_list = []
        #ret_list.append(api_schema.FootballRivalsAppearanceInput(captain=True,draftableObjectId=self.player1.draftable_player.value_id))
        return ret_list

########## Functions ##########

def calculate_best_lineup(cap_value: float,player: list[LineupCalculationPlayer], tactics:list[api_schema.FootballRivalsLineupTactic], missions:list[dict]) -> Lineup | None:
    best_lineup:Lineup | None = None
    for idx1, player1 in enumerate(player):
        for idx2, player2 in enumerate(player[(idx1+1):]):
            for idx3, player3 in enumerate(player[(idx1+idx2+2):]):
                for idx4, player4 in enumerate(player[(idx1+idx2+idx3+3):]):
                    for idx5, player5 in enumerate(player[(idx1+idx2+idx3+idx4+4):]):
                        lineup = Lineup(player1,player2,player3,player4,player5,tactics,missions)
                        if lineup.met_cap( cap_value) and lineup.valid_positions():
                            if best_lineup == None:
                                best_lineup = lineup
                            elif best_lineup.get_predicted_score() < lineup.get_predicted_score():
                                best_lineup = lineup
    return best_lineup
    
def filter_scores(all_scores: list[api_schema.So5Score], teams_slug: str, home_away:str) -> list[api_schema.So5Score]:
    result_list:list[api_schema.So5Score] = []
    for score in all_scores:
        # Filter out not started games
        if score.value_playerGameStats.value_gameStarted != True:
            continue 
        # Filter home/away
        if home_away == "home" and score.value_game.value_homeTeam.value_slug != teams_slug:
            continue
        if home_away == "away" and score.value_game.value_awayTeam.value_slug != teams_slug:
            continue
        result_list.append(score)
    return result_list

def get_scores_from_player_slug_list(client:SorareClient, player_slug_list:list[str])-> list[api_schema.Player]:
    max_items:int = 7

    if len(player_slug_list) > max_items:
        ret_list:list[api_schema.Player] = []
        while len(player_slug_list) > 0:
            sub_list = player_slug_list[:max_items]
            ret_list.extend(get_scores_from_player_slug_list(client=client,player_slug_list=sub_list))
            del player_slug_list[:max_items]
        return ret_list
    def slug_to_query(slug:str) -> str:
        result = slug.replace("-","_")
        return result
    query = api_schema.Query()
    result_list:list[api_schema.Player] = []
    print(len(player_slug_list))
    for player_slug in player_slug_list:
        query_player = query.football().player( slug= player_slug, _param_name = 'player_'+slug_to_query(player_slug))
        query_player.slug()
        query_player.displayName()
        query_scores = query_player.allSo5Scores(first=20, last=None, before=None, after=None, position=None).nodes()
        query_scores.playerGameStats().gameStarted()
        query_scores.score()
        query_game = query_scores.game()
        query_game.homeTeam().slug()
        query_game.awayTeam().slug()
        query_det_score = query_scores.detailedScore()
        query_det_score.category()
        query_det_score.points()
        query_det_score.stat()
        query_det_score.statValue()
        query_det_score.totalScore()
        

    client.query_request(query)

    for player_slug in player_slug_list:
        result_list.append(getattr(query.value_football,"value_player_"+slug_to_query(player_slug)))
    return result_list

def get_lineup_from_game(client:SorareClient, game : api_schema.FootballRivalsGame, missions:list[dict], create_game: bool = False) -> api_schema.footballRivalsLineupUpsertInput:
    """
    Calculate the best lineup for a game
    """
    logging.info("Getting lineup for game "+str(game.value_slug))
    
    # Query game details
    query = api_schema.Query()
    query_rivals_game = query.football().rivals().game(slug=game.value_slug)
    ## Draftable player
    query_dp = query_rivals_game.draftablePlayers()
    query_dp.player().slug()
    query_dp.id()
    query_dp.capValue()
    query_dp.position()
    
    ## Tactics
    query_lt = query_rivals_game.lineupTactics()
    query_lt.id()
    query_lt.slug()
    query_lt.stat()
    query_theshold = query_lt.thresholds()
    query_theshold.score()
    query_theshold.threshold()
    ## Underlying game
    query_game = query_rivals_game.game()
    ### Formations
    query_game.homeFormation().startingLineup().slug()
    query_game.awayFormation().startingLineup().slug()
    ### Any Player
    query_game_anyplayer = query_game.anyPlayers()
    query_game_anyplayer.slug()
    query_game_anyplayer.activeClub().slug()
    ### Home/Away Team
    query_game.homeTeam().slug()
    query_game.awayTeam().slug()
    client.query_request(query)

    # Determine relevant players
    home_player_slugs = []
    away_player_slugs = []
    ## Formation known
    if game.value_formationKnown:
        for home_area in query.value_football.value_rivals.value_game.value_game.value_homeFormation.value_startingLineup:
            for home_player in home_area:
                home_player_slugs.append(home_player.value_slug)
        for away_area in query.value_football.value_rivals.value_game.value_game.value_awayFormation.value_startingLineup:
            for away_player in away_area:
                away_player_slugs.append(away_player.value_slug)    
    else:
    ## Formation not known
        for player in query.value_football.value_rivals.value_game.value_game.value_anyPlayers:
            if player.value_activeClub.value_slug ==  query.value_football.value_rivals.value_game.value_game.value_homeTeam.value_slug:
                home_player_slugs.append(player.value_slug)
            elif player.value_activeClub.value_slug ==  query.value_football.value_rivals.value_game.value_game.value_awayTeam.value_slug:
                away_player_slugs.append(player.value_slug)
            else:
                logging.error("Could not map player to team")

    # Query player stats
    lineup_player:list[LineupCalculationPlayer] = []
    ## Home team        
    home_player_list = get_scores_from_player_slug_list(client,home_player_slugs)
    for home_player in home_player_list:
        player_games = filter_scores(
            all_scores=home_player.value_allSo5Scores.value_nodes,
            teams_slug=str(query.value_football.value_rivals.value_game.value_game.value_homeTeam.value_slug),
            home_away="home"
        )
        for d_player in query.value_football.value_rivals.value_game.value_draftablePlayers:
            if d_player.value_player.value_slug == home_player.value_slug:
                lcp = LineupCalculationPlayer( score_list=player_games, draftable_player=d_player, home_away="home")
                lineup_player.append(lcp)
                break
    ## Away team
    away_player_list = get_scores_from_player_slug_list(client,away_player_slugs)
    for away_player in away_player_list:
        player_games = filter_scores(
            all_scores=away_player.value_allSo5Scores.value_nodes,
            teams_slug=str(query.value_football.value_rivals.value_game.value_game.value_awayTeam.value_slug),
            home_away="away"
        )
        for d_player in query.value_football.value_rivals.value_game.value_draftablePlayers:
            if d_player.value_player.value_slug == away_player.value_slug:
                lcp = LineupCalculationPlayer( score_list=player_games, draftable_player=d_player, home_away="away")
                lineup_player.append(lcp)
                break
    
     
    lineupTactics:list[api_schema.FootballRivalsLineupTactic] = []
    # Filter tactics by missions
    for tactic in query.value_football.value_rivals.value_game.value_lineupTactics:
        for mission in missions:
            if mission.get("tacticSlug",None) != None:
                if tactic.value_slug == mission.get("tacticSlug",None):
                    lineupTactics.append(tactic)            
        #    pass
        #lineupTactics.append(tactic)
    #print(len(lineupTactics))
    if len(lineupTactics) == 0:
        lineupTactics = query.value_football.value_rivals.value_game.value_lineupTactics

    lineup = calculate_best_lineup(
        cap_value= float(game.value_cap),
        player=lineup_player,
        tactics=lineupTactics,
        missions=missions
    )
    if lineup != None:
        print(lineup.player1.get_name()+" > "+ lineup.player1.get_position()+" > "+str(lineup.player1.get_predicted_score()))
        print(lineup.player2.get_name()+" > "+ lineup.player2.get_position()+" > "+str(lineup.player2.get_predicted_score()))
        print(lineup.player3.get_name()+" > "+ lineup.player3.get_position()+" > "+str(lineup.player3.get_predicted_score()))
        print(lineup.player4.get_name()+" > "+ lineup.player4.get_position()+" > "+str(lineup.player4.get_predicted_score()))
        print(lineup.player5.get_name()+" > "+ lineup.player5.get_position()+" > "+str(lineup.player5.get_predicted_score()))
        print("Captain:"+lineup.get_captain().get_name())
        print("Taktik:"+lineup.get_tactic_slug()+ ""+str(lineup.get_tactic_score()))
        print(lineup.player1.home_away)
        print(lineup.player2.home_away)
        print(lineup.player3.home_away)
        print(lineup.player4.home_away)
        print(lineup.player5.home_away)
        
        # Set lineup
        if create_game:
            player_list: list[RivalsGameAppearance] = []
            player_list.append(RivalsGameAppearance(draftableObjectId=lineup.player1.get_id(),captain=lineup.player1 == lineup.get_captain()))
            player_list.append(RivalsGameAppearance(draftableObjectId=lineup.player2.get_id(),captain=lineup.player2 == lineup.get_captain()))
            player_list.append(RivalsGameAppearance(draftableObjectId=lineup.player3.get_id(),captain=lineup.player3 == lineup.get_captain()))
            player_list.append(RivalsGameAppearance(draftableObjectId=lineup.player4.get_id(),captain=lineup.player4 == lineup.get_captain()))
            player_list.append(RivalsGameAppearance(draftableObjectId=lineup.player5.get_id(),captain=lineup.player5 == lineup.get_captain()))
            set_rivals_game_lineup(
                client=client,
                game_id=game.value_id,
                player=player_list,
                tactic_slug=lineup.get_tactic_slug()
            )
    # Simulation
    #query = api_schema.Query()
    #query_rivals_game = query.football().rivals().game(slug=game.value_slug)
    #query_rivals_game.onboardingLineupSimulation(appearances=lineup.get_appearances() , tacticSlug=lineup.get_tactic_slug())
    #client.query_request(query)
    return None


logging.info("Starting rivals upcoming")
# Read lineups, which should be automatically posted
post_lineups = []
lineup_games = []
with open("temp/notify_lineups.txt", mode="r", encoding="utf-8") as file:
    post_lineups = file.readlines()


class QueryContentTiles(api_schema.GraphQLObject):
    def _create_query_code(self, check_parent = True):
        return """
 ... on ManagerProgressionMissionContentTile {
    mission {
        name
        description
        progress
    }
}
"""

########## Code ##########
query = api_schema.Query()
rivals = query.football().rivals()
rivals._add_to_query("contentTiles","contentTiles",QueryContentTiles(rivals))
up_games = rivals.upcomingGames( query = None)
up_games.id()
up_games.slug()
up_games.cap()
up_games.formationKnown()
up_games.shouldNotify()
game = up_games.game()
game.id()
#game.homeTeam().slug()
#game.awayTeam().slug()

client.query_request(query)

mission_config = {
    "RIVALS_BUY_CARD": {
        "irrelevant": True,
    },
    "WIN_ARENA_SUBSTITUTION": { # Win a match with a substitution
        "irrelevant": True,    
    },
    "WIN_ARENA_DIFFERENCE_LESS_20": { # Win a match with less than 20 points difference
        "irrelevant": True,        
    },
    "WIN_ARENA_JOGA_BONITO": {
        "tacticSlug": "joga_bonito"
    },
    "WIN_ARENA_DIFFERENT_TEAMS_HARD": {
        "homeTeamMin": 2,
        "awayTeamMin": 2,
    }
}
missions = []
#invalid_missions = ["RIVALS_BUY_CARD"]
for mission in getattr(query.value_football.value_rivals,"value_contentTiles"):
    if hasattr(mission,"value_mission"):
        if mission_config.get(mission.value_mission.value_name,None) == None:
            logging.warning("No info for mission "+mission.value_mission.value_name+". Skipping!")
            logging.warning(mission.value_mission.value_description)
        elif mission_config.get(mission.value_mission.value_name).get("irrelevant",False) == False and mission.value_mission.value_progress == 0:
            missions.append(mission_config.get(mission.value_mission.value_name,None))
        
#get_lineup_from_game(client,query.value_football.value_rivals.value_upcomingGames[0],missions)
#exit()
for game in query.value_football.value_rivals.value_upcomingGames:
    #print(game.value_slug)
    if game.value_shouldNotify ==True:
        lineup_games.append(game.value_slug)
        
                
    
    if game.value_formationKnown:
        for post_lu in post_lineups:
            if game.value_slug == post_lu.strip():
                get_lineup_from_game(client,game,missions, True)
                print(game.value_slug)

with open("temp/notify_lineups.txt", mode="w", encoding="utf-8") as file:
    for line in lineup_games:
        file.write(f"{line}\n")
