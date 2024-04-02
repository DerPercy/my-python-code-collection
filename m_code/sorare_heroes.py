from sorare import Client as SorareClient
from sorare.fixture import get_latest_fixtures
from sorare.leader_board import get_leader_boards_of_fixture_slug
from sorare.func_sorare_heroes import create_leaderboard_image, get_price_of_player, get_leaderboard_data
from sorare.cards import get_cards_of_player 
from sorare.player import get_player_scoreboard
from sorare.user import get_player_slugs_of_current_user
from sorare.context import file_func
from sorare.club import get_club_slugs_playing_next_gw
from sorare.models.fixture import Fixture


import logging
import os
from dotenv import load_dotenv
import json
import traceback
import sys
from icecream import ic

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})
#print(get_club_slugs_playing_next_gw(client))

#def sort_score(entry):
#    return entry.get("scoreboard_total")
#score_list = []
#player_slug_list = get_player_slugs_of_current_user(client)
#for player_slug in player_slug_list:
#    print(player_slug)
#    score_list.append(get_player_scoreboard(client,player_slug))
#score_list.sort(key=sort_score,reverse=True)
#print(score_list)
#cachefile = os.path.dirname(os.path.abspath(__file__))+"/../temp/sorare/scoreboard.json"
    
#file_func.write_json_to_file(score_list,cachefile)

#quit()

scenario = "winner"
if len(sys.argv) < 2:
    logging.info("No arguments found. Use default scenario (winner)")
elif sys.argv[1] == 'budget':
    logging.info("Budget argument found.")
    scenario = "budget"
elif sys.argv[1] == 'pricepreload':
    logging.info("Price preload argument found.")
    scenario = "pricepreload"
else:
    logging.info("Unknown argument found. Use default scenario (winner)")

leader_board_rarities = ["limited","rare","super_rare","unique"]
if scenario in ["budget","pricepreload"] :
    leader_board_rarities = ["limited","rare"]
    

def store_options(options,client:SorareClient):
    # add prices

    for option in options:
        for player in option.get("player"):
            player["price_usd"] = get_price_of_player(client,player.get("playerSlug"),player.get("rarity"),fixture_date)
    
    # Writing to sample.json
    json_object = json.dumps(options, indent=4)

    with open("sorarefiles/sample_options.json", "w") as outfile:
        outfile.write(json_object)

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

def create_ranking_sorter(fixture_date, season:str):
    def ranking_sorter(ranking):
        """Attention: lowest value will be used"""
        lineup_price = 0
        #ic(ranking)
        logging.info("Get price for players of #"+str(ranking.get("ranking"))+" of total "+str(ranking.get("rankingMax")))
        for idx, lineup_player in enumerate(ranking.get("so5Lineup").get("so5Appearances")):
            # >> To prevent lineups without games (image renderer stuck on this)
            #if lineup_player.get("game") == None:
            #    logging.info("Player without game found. Ignore from lineups")
            #    lineup_price = lineup_price + 100000
            # ^^
            player_slug = lineup_player.get("card").get("player").get("slug")
            player_price = get_price_of_player(client,player_slug,lineup_player.get("card").get("rarity"),fixture_date,season)
            if player_price != None:
                lineup_price = lineup_price + player_price
        return lineup_price
    return ranking_sorter
   
#get_cards_of_player(client,"walter-daniel-benitez","limited")

fixture_list = get_latest_fixtures(client)
options = []
ic(fixture_list)
#fixture_list = [
#    Fixture(
# #       slug= "22-26-oct",
#        aasmState= "closed",
#        startDate= "2021-10-22T10:00:00Z",
#        gameWeek= 212
#    )
#]
ic(fixture_list)

for fixture in fixture_list:
    print(fixture.aasmState)
    if scenario == "pricepreload" and fixture.aasmState == "started":
        leader_board_list = get_leader_boards_of_fixture_slug(client,fixture.slug)
        for leader_board in leader_board_list:
            if leader_board.rarity not in leader_board_rarities:
                continue
            season = "ALL_SEASONS"
            #ic(leader_board)
            if leader_board.seasonality == True:
                season = "IN_SEASON"
            get_leaderboard_data(client,leader_board.slug,ranking_filter,create_ranking_sorter(fixture.startDate,season))
            #get_leaderboard_data(client,leader_board.slug,ranking_filter,create_ranking_sorter(fixture.startDate,"IN_SEASON"))
        quit()

    if fixture.aasmState == "closed":
        fixture_slug = fixture.slug
        #fixture_slug = "1-5-sep-2023" # Example data for movie
        fixture_date = fixture.startDate
        leader_board_list = get_leader_boards_of_fixture_slug(client,fixture_slug)
        for leader_board in leader_board_list:
            if leader_board.rarity not in leader_board_rarities:
                continue
            season = "ALL_SEASONS"
            #ic(leader_board)
            if leader_board.seasonality == True:
                season = "IN_SEASON"
            #def ranking_sorter(ranking):
            #    """Attention: lowest value will be used"""
            #    lineup_price = 0
            #    for lineup_player in ranking.get("so5Lineup").get("so5Appearances"):
            #        # >> To prevent lineups without games (image renderer stuck on this)
            #        #if lineup_player.get("game") == None:
            #        #    logging.info("Player without game found. Ignore from lineups")
            #        #    lineup_price = lineup_price + 100000
            #        # ^^
            #        player_slug = lineup_player.get("card").get("player").get("slug")
            #        player_price = get_price_of_player(client,player_slug,lineup_player.get("card").get("rarity"),fixture_date)
            #        if player_price != None:
            #            lineup_price = lineup_price + player_price
            #    return lineup_price
            try:
                if scenario == "budget":
                    option = create_leaderboard_image(client,leader_board.slug,ranking_filter,create_ranking_sorter(fixture.startDate,season),0)
                    #options.append(option)
                    #option = create_leaderboard_image(client,leader_board.slug,ranking_filter,create_ranking_sorter(fixture.startDate),1)
                    #options.append(option)
                    #option = create_leaderboard_image(client,leader_board.slug,ranking_filter,create_ranking_sorter(fixture.startDate),2)
                else:
                    option = create_leaderboard_image(client,leader_board.slug)
                
                options.append(option)
                store_options(options,client)
            except Exception as exc:
                logging.error(exc)
                logging.error(traceback.format_exc())
                logging.error(leader_board)

#print(fixture_list)

store_options(options,client)



