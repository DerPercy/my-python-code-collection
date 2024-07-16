from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2,file_func,value_aggregator
from services import lineup_ranking,rivals_tactic
from func_sorare_rivals_predict import predict_best_lineup_of_game
from models.rivals import RivalsGame, read_rivals_game_from_fileSystem

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

competition_summary = []
past_games = func_sorare_rivals.get_last_rivals_results(client)
for game in past_games:
    #if game["withMatch"] == False:
    #    continue
    logging.info("Handling game:"+game.get("name"))
    rg = read_rivals_game_from_fileSystem("./temp/rivals/games/",game["slug"])
    if rg == None:
        logging.warning("No rivals game data found!")
    

    # Add game details
    game_id = game.get("game").get("id")
    game_data = func_sorare_rivals.request_game_by_id(client,game_id)
    if game_data == None:
        logging.error("No game data found!")
        continue
    game["game"]["data"] = game_data
    players = []
    players_det_score = []
    # Getting game tactics
    game_tactic_def_list = rivals_tactic.build_tactic_list_from_api_response(game.get("lineupTactics"))
    game["tactics"] = game_tactic_def_list
    #ic(game_tactic_def_list)
    # add player scores
    for player in game_data["homeFormation"]["bench"]:
        player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
        player["playerScore"] = player_score
        players_det_score.append(player)
    for player in game_data["awayFormation"]["bench"]:
        player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
        player["playerScore"] = player_score
        players_det_score.append(player)
    for area in game_data["awayFormation"]["startingLineup"]:
        for player in area:
            player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
            player["playerScore"] = player_score
            players.append(player)
            players_det_score.append(player)
    
    for area in game_data["homeFormation"]["startingLineup"]:
        for player in area:
            player_score = func_sorare_rivals.request_game_player_score(client,game_id,player["slug"])
            player["playerScore"] = player_score
            players.append(player)
            players_det_score.append(player)
    
    # Getting tactics from players
    tactic_player_slugs = []
    tactic_payload = "detailedScore { stat statValue } score"
    for player in players_det_score:
        tactic_player_slugs.append(player["slug"])
    result = func_sorare_rivals.request_game_players_game_score(client,game_id,tactic_player_slugs,tactic_payload)
    player_det_scores = {}
    for player in players_det_score:
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
            score=float(player["playerScore"]["score"]),
            detailed_score_list=rivals_tactic.conv_object_to_player_detailed_scores(player_det_scores[player["slug"]])
        ))
    best_lineup_result = lineup_ranking.calculate_best_lineup(
        players=ranking_players,
        cap_limit=float(game["cap"]),
        tactic_def_list=game_tactic_def_list
    )
    game["topTeam"] = best_lineup_result[0]
    game["topTeamTactic"] = best_lineup_result[1]
    game["topTeamScore"] = best_lineup_result[3]

    if best_lineup_result[3] == 0:
        game["maxScorePercentage"] = 0
    else:    
        game["maxScorePercentage"] = int( game["myLineupScore"]  * 100 / best_lineup_result[3] ) 
    
    comp_found = False
    win_value = 0
    if game["won"] == True:
        win_value = 100

    for com_summary_entry in competition_summary:
        if com_summary_entry["slug"] == game["game"]["competitionSlug"]:
            comp_found = True
            if game["withMatch"] == True:
                com_summary_entry["winRate"].add_value(win_value)
            com_summary_entry["numGames"] = com_summary_entry["numGames"] + 1
            com_summary_entry["avgScoreTotal"] = com_summary_entry["avgScoreTotal"] + game["maxScorePercentage"]
            com_summary_entry["avgScorePerc"] = com_summary_entry["avgScoreTotal"] / com_summary_entry["numGames"]
    
    if comp_found == False:
        win_rate = value_aggregator.MyValueAggregator()
        win_rate.add_value(win_value)
            
        competition_summary.append({
            "numGames": 1,
            "avgScoreTotal": game["maxScorePercentage"],
            "avgScorePerc": game["maxScorePercentage"],
            "slug": game["game"]["competitionSlug"],
            "winRate": win_rate
        })

    # Strategies here
    game_data = file_func.read_json_from_file("./temp/rivals/games/"+game.get("slug")+".json")
    if game_data.get("name",None) != None: # Entry exists
        logging.info("Found game info from filesystem: Calculate strategies")
#        # Get stats from player list
        try:
            strategy_lineup_result = predict_best_lineup_of_game(game.get("slug"))
            if strategy_lineup_result != None:
                game["strategyTeam"] = strategy_lineup_result[0]
                game["strategyTeamTactic"] = strategy_lineup_result[1]
                game["strategyTeamScore"] = strategy_lineup_result[3]
        except Exception as e:
            logging.exception(e)
    
        
environment = myjinja2.get_environment()
template = environment.get_template("rivals_recap.jinja2")

content = template.render(
    data = {
        "past_games": past_games,
        "competition_summary": competition_summary
    }
)
with open("temp/sorare-rivals-recap-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)