from sorare import Client as SorareClient
from sorare.fixture import get_fixture_slug_of_gameweek
from sorare.leader_board import get_leader_boards_of_fixture_slug
from sorare.rankings import get_rankings_of_leader_board_slug

import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


print(os.getenv('SORARE_EMAIL'))
print(os.getenv('SORARE_PASSWORD'))

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

               
game_weeks = list(range(301,401))
game_weeks = list(range(301,302))
for game_week in game_weeks:
    print(game_week)
    fixture_slug = get_fixture_slug_of_gameweek(client,game_week)
    leader_boards = get_leader_boards_of_fixture_slug(client,fixture_slug)
    for leader_board in leader_boards:
        top100  = get_rankings_of_leader_board_slug(client,leader_board.slug,100)
        print(leader_board.rarity)
