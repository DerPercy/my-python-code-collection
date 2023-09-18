from sorare import Client as SorareClient
from sorare.fixture import get_fixture_slug_of_gameweek
from sorare.leader_board import get_leader_boards_of_fixture_slug
from sorare.rankings import get_rankings_of_leader_board_slug

import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_user_entry(userId):
    return {
        "user": userId,
        "1st": 0,
        "top10": 0,
        "top100": 0
    }

print(os.getenv('SORARE_EMAIL'))
print(os.getenv('SORARE_PASSWORD'))

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

# Example UserID: User:16ebc838-fee5-44de-b495-b56efd6d2ea4

               
game_weeks = list(range(301,401))
rarity = "limited"
#game_weeks = list(range(301,302))

def is_better_than(a,b):
    if a["1st"] > b["1st"]:
        return True
    if a["1st"] < b["1st"]:
        return False
    if a["top10"] > b["top10"]:
        return True
    if a["top10"] < b["top10"]:
        return False
    if a["top100"] > b["top100"]:
        return True
    return False
def sort_rankings(rankings_unsorted,sort_function:callable): 
    ranking_sorted = []
    for value in rankings_unsorted.values():
        count = 0
        found = False
        for sorted_entry in ranking_sorted:
            if sort_function(value,sorted_entry) == True:
                ranking_sorted.insert(count,value)
                found = True
                break
            count = count + 1
        if found == False:
            ranking_sorted.append(value)
    return ranking_sorted
user_rankings = {}
for game_week in game_weeks:
    print(game_week)
    fixture_slug = get_fixture_slug_of_gameweek(client,game_week)
    leader_boards = get_leader_boards_of_fixture_slug(client,fixture_slug)
    for leader_board in leader_boards:
        if leader_board.rarity == rarity:
            top100  = get_rankings_of_leader_board_slug(client,leader_board.slug,100)
            for ranking in top100:
                if user_rankings.get(ranking.user_id) == None:
                    user_rankings[ranking.user_id] = create_user_entry(ranking.user_id)
                entry = user_rankings.get(ranking.user_id)
                if ranking.position == 1:
                    entry["1st"] = entry["1st"] + 1
                elif ranking.position <= 10:
                    entry["top10"] = entry["top10"] + 1
                elif ranking.position <= 100:
                    entry["top100"] = entry["top100"] + 1
                
        #print(top100)
        #print(leader_board.rarity)

    print(sort_rankings(user_rankings,is_better_than)[:10])