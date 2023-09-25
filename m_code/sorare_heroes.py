from sorare import Client as SorareClient
from sorare.fixture import get_latest_fixtures
from sorare.leader_board import get_leader_boards_of_fixture_slug
from sorare.func_sorare_heroes import create_leaderboard_image, get_price_of_player
from sorare.cards import get_cards_of_player 

import logging
import os
from dotenv import load_dotenv
import json
import traceback

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})


def ranking_filter(ranking:dict):
    #print(ranking.get("ranking"))
    #print(ranking)
    #if ranking.get("ranking") > 3:
    #    return False
    if ranking.get("eligibleForReward") == True:
        reward_found = False
        for rw in ranking.get("eligibleRewards",[]):
            #print(rw)
            if rw.get("usdAmount",None) != None:
                reward_found = True
            if rw.get("cards",None) != None:
                reward_found = True   
        return reward_found    
    return False

#get_cards_of_player(client,"walter-daniel-benitez","limited")

fixture_list = get_latest_fixtures(client)
options = []

for fixture in fixture_list:
    print(fixture.aasmState)
    if fixture.aasmState == "closed":
        fixture_slug = fixture.slug
        #fixture_slug = "1-5-sep-2023" # Example data for movie
        fixture_date = fixture.startDate
        leader_board_list = get_leader_boards_of_fixture_slug(client,fixture_slug)
        for leader_board in leader_board_list:
            if leader_board.rarity not in ["limited","rare"]:
                continue
            def ranking_sorter(ranking):
                """Attention: lowest value will be used"""
                lineup_price = 0
                for lineup_player in ranking.get("so5Lineup").get("so5Appearances"):
                    player_slug = lineup_player.get("card").get("player").get("slug")
                    player_price = get_price_of_player(client,player_slug,lineup_player.get("card").get("rarity"),fixture_date)
                    if player_price != None:
                        lineup_price = lineup_price + player_price
                return lineup_price
            try:
                option = create_leaderboard_image(client,leader_board.slug,ranking_filter,ranking_sorter)
                # => Default Sorare Heroes
                #option = create_leaderboard_image(client,leader_board.slug)
                
                options.append(option)
            except Exception as exc:
                logging.error(exc)
                logging.error(traceback.format_exc())
                logging.error(leader_board)

#print(fixture_list)

# add prices
for option in options:
    for player in option.get("player"):
        player["price_usd"] = get_price_of_player(client,player.get("playerSlug"),player.get("rarity"),fixture_date)
    
    # Writing to sample.json
    json_object = json.dumps(options, indent=4)

    with open("sorarefiles/sample_options.json", "w") as outfile:
        outfile.write(json_object)



