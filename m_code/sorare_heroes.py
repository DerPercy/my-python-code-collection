from sorare import Client as SorareClient
from sorare.fixture import get_latest_fixtures
from sorare.leader_board import get_leader_boards_of_fixture_slug
from sorare.func_sorare_heroes import create_leaderboard_image
from sorare.cards import get_cards_of_player

import logging
import os
from dotenv import load_dotenv
import json

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})


#get_cards_of_player(client,"walter-daniel-benitez","limited")

fixture_list = get_latest_fixtures(client)
options = []
for fixture in fixture_list:
    if fixture.aasmState == "closed":
        fixture_slug = fixture.slug
        #fixture_slug = "1-5-sep-2023" # Example data for movie
        leader_board_list = get_leader_boards_of_fixture_slug(client,fixture_slug)
        for leader_board in leader_board_list:
            try:
                option = create_leaderboard_image(client,leader_board.slug)
                options.append(option)
            except Exception as exc:
                logging.error(exc)
                logging.error(leader_board)

#print(fixture_list)

# add prices
for option in options:
    for player in option.get("player"):
        if player.get("rarity",None) in ["limited","rare"]:
            player["price_usd"] = get_cards_of_player(client,player.get("playerSlug"),player.get("rarity"))[-1].get("usd")
    
    # Writing to sample.json
    json_object = json.dumps(options, indent=4)

    with open("sorarefiles/sample_options.json", "w") as outfile:
        outfile.write(json_object)


