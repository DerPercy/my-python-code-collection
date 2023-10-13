from sorare import Client as SorareClient
from sorare.fixture import get_fixture_slug_of_gameweek, get_fixture_from_slug,get_current_open_gameweek
from sorare.leader_board import get_leader_boards_of_fixture_slug
from sorare.func_sorare_heroes import create_leaderboard_image, get_price_of_player, get_leaderboard_data
from sorare.cards import get_cards_of_player 
from sorare.player import get_player_scoreboard
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
playing_clubs = get_club_slugs_playing_next_gw(client)
print(playing_clubs)
player_slug_list = []
for club_slug in playing_clubs:
    club_players = get_player_slugs_of_club_slug(client,club_slug)
    player_slug_list.extend(club_players)
print(str(len(player_slug_list)))

def sort_score(entry):
    return entry.get("scoreboard_total")
score_list = []
#player_slug_list = get_player_slugs_of_current_user(client)

fixture = get_fixture_from_slug(client,get_fixture_slug_of_gameweek(client,get_current_open_gameweek(client)))
cachefile = os.path.dirname(os.path.abspath(__file__))+"/../temp/sorare/scoreboard_all.json"

for player_slug in player_slug_list:
    print(player_slug)
    player_scoreboard = get_player_scoreboard(client,player_slug)
    if player_scoreboard.get("team",{}).get("slug",None) in playing_clubs:
        score_list.append(player_scoreboard)
        score_list.sort(key=sort_score,reverse=True)
        file_func.write_json_to_file(score_list,cachefile)

# Add prices to scores

for score in score_list:
    player_slug = score.get("player").get("slug")
    price = get_price_of_player(client,player_slug,"limited",fixture.startDate)
    score["price"] = price 
    file_func.write_json_to_file(score_list,cachefile)

