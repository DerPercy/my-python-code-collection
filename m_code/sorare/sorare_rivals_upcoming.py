from client import Client as SorareClient
#from account_entry import get_account_entries
from context import myjinja2, file_func, hash_map
from services import lineup_ranking,rivals_tactic
from services.rivals_predict import calc_predictions_from_rivals_game,PlayerPredictedScore,StrategyContainer

import logging, logging.handlers
import os
from dotenv import load_dotenv
from icecream import ic
from datetime import datetime
import func_sorare_rivals, api_rivals_mutations
import argparse, sys
import cattrs
from models.rivals import RivalsGame, read_rivals_game_from_fileSystem

'''
Initializing
'''
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--logfile", help="Specify the logfile destination")
parser.add_argument("--lineupfile", help="Specify the players, which should be used for lineups")
parser.add_argument("--joinarena", help="If 'X' join the arena")
parser.add_argument("--settingsfile", help="Path of the game settings")

args = parser.parse_args()

log_handlers = []
log_handlers.append(logging.StreamHandler(sys.stdout))
if args.logfile != None:
    log_handlers.append(logging.handlers.RotatingFileHandler(
        args.logfile, maxBytes=(1048576*5), backupCount=7))


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

settings_file = "./temp/comp_settings.json"
if args.settingsfile != None:
    settings_file = args.settingsfile
game_settings_map = file_func.read_json_from_file(settings_file)


my_lineups = []
logging.info("Checking, if lineup file exists")
if args.lineupfile == None:
    logging.info("No lineup file provided")
else:
    logging.info("Lineup file provided")
    lines=[]
    with open(args.lineupfile, mode="r", encoding="utf-8") as file:
        lines = file.readlines()
        for line in lines:
            splitted = line.split(",",1)
            entry = []
            entry.append(splitted[0])
            entry.append(splitted[1].split(","))
            my_lineups.append(entry)
    
    logging.info(my_lineups)
        #file.write(content)

join_arena = False
logging.info("Checking joinarena flag")
if args.joinarena == 'X':
    logging.info("joinarena = X: Auto join arena")
    join_arena = True

logging.info("Looking for upcoming games")


# Read lineups, which should be automatically posted
post_lineups = []
with open("temp/notify_lineups.txt", mode="r", encoding="utf-8") as file:
    post_lineups = file.readlines()
logging.info(post_lineups)

num_games = 10
games = func_sorare_rivals.get_next_rivals_games(client,num_games,False)

upcoming_games = []
lineup_games = []
    
for game in games[:num_games]:
    file_func.write_json_to_file(
        filename="./temp/rivals/games_upcoming/"+game["slug"]+"/game_info.json",
        json_data=game
    )
    logging.info("Checking "+game["slug"])
    starting_player_slugs = []
    if game["shouldNotify"] == True:
        lineup_games.append(game["slug"])
        logging.info("Game "+game["slug"]+" should auto lineup")
    #rg = read_rivals_game_from_fileSystem("./temp/rivals/games/",game["slug"])
    
    if game["formationKnown"] != True:
        lu_found = False
        for man_lu in my_lineups:
            if man_lu[0] == game["slug"]:
                logging.info("Manual lineup found")
                lu_found = True
                for player_slug in man_lu[1]:
                    starting_player_slugs.append(player_slug.strip())
        if lu_found == False:
            continue
    
    draftable_player_map_1 = func_sorare_rivals.request_game_draftable_player_ids(client,game["slug"])
    file_func.write_json_to_file(
        filename="./temp/rivals/games_upcoming/"+game["slug"]+"/draftable_player_map.json",
        json_data=draftable_player_map_1
    )
    draftable_player_map = func_sorare_rivals.draftable_player_ids_to_hashmap(draftable_player_map_1)
    
    logging.info("Formation known! Checking lineup")
    game_details = func_sorare_rivals.request_game_by_id(client,game["game"]["id"][5:])
    file_func.write_json_to_file(
        filename="./temp/rivals/games_upcoming/"+game["slug"]+"/game_details.json",
        json_data=game_details
    )
    
    #if rg != None:
    pre_game_info =  RivalsGame.add_pre_game_info(
            game_info=game,
            game_details=game_details,
            draftable_player_map=draftable_player_map_1
        )
    #game_data = file_func.read_json_from_file("./temp/rivals/games/"+game["slug"]+".json")
    
    logging.info("Get tactics")
    game_tactic_def_list = rivals_tactic.build_tactic_list_from_api_response(game.get("lineupTactics"))
    #logging.info(game_tactic_def_list)
    if len(starting_player_slugs) > 0:
        logging.info("Already manual lineup found. Did not consider data from sorare.")
    else:
        for position in game_details["homeFormation"]["startingLineup"]:
            for player in position:
                starting_player_slugs.append(player["slug"])
        for position in game_details["awayFormation"]["startingLineup"]:
            for player in position:
                starting_player_slugs.append(player["slug"])
    
    # Strategy
    json = file_func.read_json_from_file("./temp/rivals/games/"+game.get("slug")+"/strategies.json")
    
    strategy = hash_map.prepare_converter(cattrs.GenConverter()).structure(json,StrategyContainer)
    
    
    logging.info("Found staring players")
    logging.info(starting_player_slugs)
    ranking_players = []
    
    pred_map = strategy.get_player_pred_score_map("default")
    for player_slug in starting_player_slugs:
        
        if pred_map.has_item(player_slug) == False:
            logging.warning("Not enough data for "+player_slug+" found! Did not consider in lineup.")
            continue
        player_score = pred_map.get_item(player_slug).calculated_score
                   
        
        cap_score = draftable_player_map.get_item(player_slug).capValue
        
        ranking_players.append(lineup_ranking.Player(
            cap_score=cap_score,
            entity_data=pre_game_info.get_player_by_slug(player_slug), # Maybe here more details
            position=pre_game_info.get_position_of_player(player_slug)[:1],
            score=player_score,
            detailed_score_list=pred_map.get_item(player_slug).get_player_detailed_score_list()
        ))
    logging.info("Cap limit"+str(game["cap"]))
    best_lineup = lineup_ranking.calculate_best_lineup(
        players=ranking_players,
        cap_limit=float(game["cap"]),
        tactic_def_list=game_tactic_def_list
    )
    top_team = best_lineup[0]
    if len(top_team) == 0:
        logging.warning("No lineup found")
    else:
        logging.info("Lineup found:")
        for player in top_team:
            logging.info(player)
        logging.info("Captain:")
        logging.info(best_lineup[2])
        logging.info(top_team)
        upcoming_games.append({
            "gameSlug": game["slug"],
            "topTeam": top_team,
            "topTeamTactics": best_lineup[1],
            "captainSlug": best_lineup[2].slug        })

        for post_lu in post_lineups:
            if game["slug"] == post_lu.strip():
                #draftable_player_map = func_sorare_rivals.request_game_draftable_player_ids(client,game["slug"])
                lineup_player_list = []

                logging.info("Notify flag: set lineup")
                logging.info("Game:")
                logging.info(game["id"])    
                logging.info("Player:")
                for player in top_team:
                    is_captain = False
                    if best_lineup[2]["slug"] == player["slug"]:
                        is_captain = True
                    lineup_player_list.append(
                        api_rivals_mutations.RivalsGameAppearance(
                            draftableObjectId=draftable_player_map.get_item(player["slug"]).id,
                            captain=is_captain
                        )
                    )
                    #ic(player.keys())
                    logging.info(draftable_player_map.get_item(player["slug"]).id)
                    #ic(player.keys())
                logging.info("Captain:")
                logging.info(draftable_player_map.get_item(best_lineup[2]["slug"]).id)
                #ic(best_lineup[2].keys())
                logging.info("Tactic")
                logging.info(best_lineup[1])
                api_rivals_mutations.set_rivals_game_lineup(client,game["id"],lineup_player_list,best_lineup[1],join_arena)
            

        
    


environment = myjinja2.get_environment()
template = environment.get_template("rivals_upcoming.jinja2")

content = template.render(
    data = {
        "upcoming_games": upcoming_games
    }
)
with open("temp/sorare-rivals-upcoming-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)

with open("temp/notify_lineups.txt", mode="w", encoding="utf-8") as file:
    for line in lineup_games:
        file.write(f"{line}\n")