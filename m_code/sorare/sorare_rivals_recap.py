from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2
from services import lineup_ranking

import logging, logging.handlers
import os
from dotenv import load_dotenv
from icecream import ic
from datetime import datetime
import func_sorare_rivals
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
logging.info("Starting sorare_rivals_recap.py")

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

past_games = func_sorare_rivals.get_last_rivals_results(client)
for game in past_games:
    # Add game details
    game_id = game.get("game").get("id")
    game_data = func_sorare_rivals.request_game_by_id(client,game_id)
    game["game"]["data"] = game_data
    players = []
    # add player scores
    for player in game_data["homeFormation"]["bench"]:
        player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
        player["playerScore"] = player_score
    for player in game_data["awayFormation"]["bench"]:
        player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
        player["playerScore"] = player_score
    for area in game_data["awayFormation"]["startingLineup"]:
        for player in area:
            player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
            player["playerScore"] = player_score
            players.append(player)
    for area in game_data["homeFormation"]["startingLineup"]:
        for player in area:
            player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
            player["playerScore"] = player_score
            players.append(player)
    # Determining best possible lineup
    ranking_players = []
    for player in players:
        ranking_players.append(lineup_ranking.Player(
            cap_score=float(player["averageScore"]),
            entity_data=player,
            position=player["position"][:1],
            score=float(player["playerScore"]["score"])
        ))
    top_team = lineup_ranking.calculate_best_lineup(players=ranking_players,cap_limit=float(game["cap"]))
    game["topTeam"] = top_team
    ic(top_team)
    
environment = myjinja2.get_environment()
template = environment.get_template("rivals_recap.jinja2")

content = template.render(
    data = {
        "past_games": past_games
    }
)
with open("temp/sorare-rivals-recap-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)