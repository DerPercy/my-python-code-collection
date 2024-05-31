from client import Client as SorareClient
#from account_entry import get_account_entries
from context import myjinja2, file_func
from services import lineup_ranking,rivals_tactic

import logging, logging.handlers
import os
from dotenv import load_dotenv
from icecream import ic
from datetime import datetime
import func_sorare_rivals, api_rivals_mutations
import argparse, sys

'''
Initializing
'''
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--logfile", help="Specify the logfile destination")
parser.add_argument("--lineupfile", help="Specify the players, which should be used for lineups")

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

logging.info("Looking for upcoming games")


num_games = 15
games = func_sorare_rivals.get_next_rivals_games(client,num_games,False)

upcoming_games = []
for game in games[:num_games]:
    logging.info("Checking "+game["slug"])
    starting_player_slugs = []
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
    logging.info("Formation known! Checking lineup")
    game_details = func_sorare_rivals.request_game_by_id(client,game["game"]["id"][5:])
    game_data = file_func.read_json_from_file("./temp/rivals/games/"+game["slug"]+".json")
    
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
    
    logging.info("Found staring players")
    logging.info(starting_player_slugs)
    starting_player_data = {}
    for player in game_data["home"]:
        starting_player_data[player["slug"]] = player
    for player in game_data["away"]:
        starting_player_data[player["slug"]] = player
    ranking_players = []
    for player_slug in starting_player_slugs:
        if starting_player_data.get(player_slug,None) == None:
            logging.warn("Not enough data for "+player_slug+" found! Did not consider in lineup.")
            continue
        player_data = starting_player_data[player_slug]
        cap_score = player_data["l15"]
        if cap_score < 25:
            cap_score = 25

        player_pos = player_data["position"]
        

        ranking_players.append(lineup_ranking.Player(
            cap_score=cap_score,
            entity_data=player_data,
            position=player_pos[:1],
            score=player_data["gamesScore"],
            detailed_score_list=rivals_tactic.conv_object_to_player_detailed_scores(player_data["tempDetScores"])
        ))
    best_lineup = lineup_ranking.calculate_best_lineup(
        players=ranking_players,
        cap_limit=float(game["cap"]),
        tactic_def_list=game_tactic_def_list
    )
    top_team = best_lineup[0]
    logging.info("Lineup found:")
    for player in top_team:
        logging.info(player["slug"])
    #logging.info("Captain:")
    upcoming_games.append({
        "gameSlug": game["slug"],
        "topTeam": top_team,
        "topTeamTactics": best_lineup[1],
        "captainSlug": best_lineup[2]["slug"]
    })

    if game["shouldNotify"] == True:
        playerids = func_sorare_rivals.request_game_draftable_player_ids(client,game["slug"])
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
                    draftableObjectId=playerids[player["slug"]],
                    captain=is_captain
                )
            )
            #ic(player.keys())
            logging.info(playerids[player["slug"]])
            #ic(player.keys())
        logging.info("Captain:")
        logging.info(playerids[best_lineup[2]["slug"]])
        #ic(best_lineup[2].keys())
        logging.info("Tactic")
        logging.info(best_lineup[1])
        api_rivals_mutations.set_rivals_game_lineup(client,game["id"],lineup_player_list,best_lineup[1])
            

        
    


environment = myjinja2.get_environment()
template = environment.get_template("rivals_upcoming.jinja2")

content = template.render(
    data = {
        "upcoming_games": upcoming_games
    }
)
with open("temp/sorare-rivals-upcoming-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)