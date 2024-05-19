from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2
from services import lineup_ranking,rivals_tactic

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

past_games = func_sorare_rivals.get_last_rivals_results(client)#[:1]
for game in past_games:
    # Add game details
    game_id = game.get("game").get("id")
    game_data = func_sorare_rivals.request_game_by_id(client,game_id)
    game["game"]["data"] = game_data
    players = []
    # Getting game tactics
    game_tactic_def_list = rivals_tactic.build_tactic_list_from_api_response(game.get("lineupTactics"))
    game["tactics"] = game_tactic_def_list
    #ic(game_tactic_def_list)
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
    # Getting tactics from players
    tactic_player_slugs = []
    tactic_payload = "detailedScore { stat statValue } score"
    for player in players:
        tactic_player_slugs.append(player["slug"])
    result = func_sorare_rivals.request_game_players_game_score(client,game_id,tactic_player_slugs,tactic_payload)
    player_det_scores = {}
    for player in players:
        det_score = rivals_tactic.build_player_detailed_score_from_api_response(result[player["slug"]]["detailedScore"])
        player_det_scores[player["slug"]] = rivals_tactic.conv_player_detailed_scores_to_object(det_score)
    game["playerDetailScores"] = player_det_scores
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
    #ic(top_team)
    
environment = myjinja2.get_environment()
template = environment.get_template("rivals_recap.jinja2")

content = template.render(
    data = {
        "past_games": past_games
    }
)
with open("temp/sorare-rivals-recap-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)