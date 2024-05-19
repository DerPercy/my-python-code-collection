from client import Client as SorareClient
#from account_entry import get_account_entries
from context import myjinja2, file_func
from services import lineup_ranking,rivals_tactic

import logging, logging.handlers
import os
from dotenv import load_dotenv
from icecream import ic
from datetime import datetime
import func_sorare_rivals
import argparse, sys

'''
Initializing
'''
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--logfile", help="Specify the logfile destination")

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

logging.info("Looking for upcoming games")

num_games = 5
games = func_sorare_rivals.get_next_rivals_games(client,num_games,False)

upcoming_games = []
for game in games[:num_games]:
    logging.info("Checking "+game["slug"])
    if game["formationKnown"] != True:
        continue
    logging.info("Formation known! Checking lineup")
    game_details = func_sorare_rivals.request_game_by_id(client,game["game"]["id"][5:])
    game_data = file_func.read_json_from_file("./temp/rivals/games/"+game["slug"]+".json")
    starting_player_slugs = []
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

        ranking_players.append(lineup_ranking.Player(
            cap_score=cap_score,
            entity_data=player_data,
            position=player_data["position"][:1],
            score=player_data["gamesScore"]
        ))
    top_team = lineup_ranking.calculate_best_lineup(players=ranking_players,cap_limit=float(game["cap"]))
    logging.info("Lineup found:")
    for player in top_team:
        logging.info(player["slug"])
    
    upcoming_games.append({
        "gameSlug": game["slug"],
        "topTeam": top_team
    })
    


environment = myjinja2.get_environment()
template = environment.get_template("rivals_upcoming.jinja2")

content = template.render(
    data = {
        "upcoming_games": upcoming_games
    }
)
with open("temp/sorare-rivals-upcoming-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)