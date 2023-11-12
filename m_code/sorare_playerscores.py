from sorare import Client as SorareClient
from sorare.fixture import get_fixture_slug_of_gameweek, get_fixture_from_slug,get_current_open_gameweek
from sorare.leader_board import get_leader_boards_of_fixture_slug
from sorare.func_sorare_heroes import create_leaderboard_image, get_price_of_player, get_leaderboard_data
from sorare.cards import get_cards_of_player 
from sorare.player import get_player_scoreboard, is_player_slug_in_scoreboard_list
from sorare.user import get_player_slugs_of_current_user
from sorare.context import file_func
from sorare.club import get_club_slugs_playing_next_gw, get_player_slugs_of_club_slug

import logging
import os
from dotenv import load_dotenv
import json
import traceback
import sys

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

scenario = "all"
if len(sys.argv) < 2:
    logging.info("No arguments found. Use default scenario (all)")
elif sys.argv[1] == 'own':
    logging.info("Scan own lineup")
    scenario = "own"


clubs_options = {
    "filter": {
        "includeLeagues" : ["bundesliga-de"]
    }
}
playing_clubs = get_club_slugs_playing_next_gw(client,clubs_options)

logging.info(str(len(playing_clubs))+" playing clubs found")
player_slug_list = []
if scenario == "all":
    for club_slug in playing_clubs:
        club_players = get_player_slugs_of_club_slug(client,club_slug)
        player_slug_list.extend(club_players)

def sort_score(entry):
    return entry.get("scoreboard_total")
score_list = []
if scenario == "own":
    player_slug_list = get_player_slugs_of_current_user(client)

logging.info(str(len(player_slug_list))+" players found")

fixture = get_fixture_from_slug(client,get_fixture_slug_of_gameweek(client,get_current_open_gameweek(client)))
cachefile = os.path.dirname(os.path.abspath(__file__))+"/../temp/sorare/scoreboard_"+ scenario +"_"+str(get_current_open_gameweek(client))+".json"

score_list = file_func.read_json_from_file(cachefile)
if len(score_list) == 0:
    score_list = []


scoreboard_options = {
    "includeAge": True
}
if scenario == "own":
    scoreboard_options["includeAge"] = False
    
for player_slug in player_slug_list:
    if is_player_slug_in_scoreboard_list(player_slug,score_list) == True:
        logging.info(player_slug+" in cache. Skip.")
        continue
    logging.info("Getting scoreboard of player:"+player_slug)
    player_scoreboard = get_player_scoreboard(client,player_slug,scoreboard_options)
    if player_scoreboard.get("team",{}).get("slug",None) in playing_clubs:
        if scenario == "all":
            price = get_price_of_player(client,player_slug,"limited",fixture.startDate)
            player_scoreboard["price"] = price 
        score_list.append(player_scoreboard)
        score_list.sort(key=sort_score,reverse=True)
        file_func.write_json_to_file(score_list,cachefile)

#if scenario == "all":
#    # Add prices to scores
#    for score in score_list:
#        player_slug = score.get("player").get("slug")
#        price = get_price_of_player(client,player_slug,"limited",fixture.startDate)
#        score["price"] = price 
#        file_func.write_json_to_file(score_list,cachefile)

file_func.write_json_to_file(score_list,cachefile)
