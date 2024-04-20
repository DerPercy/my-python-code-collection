from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2, CoinStackHandler,AssetHandler, file_func
from models.tax_entry import TaxEntry
import logging
import os
from dotenv import load_dotenv
from icecream import ic
from datetime import datetime
from func_sorare_rivals import get_next_rivals_games, get_players_of_team_slug, get_rivals_player_stats, aggregate_player_stats

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})


games = get_next_rivals_games(client)
#ic(games)

result = []


def build_html():
    global result
    environment = myjinja2.get_environment()
    template = environment.get_template("rivals.jinja2")

    content = template.render(
        data = {
            "result_games": result
        }
    )
    with open("temp/sorare-rivals-report.html", mode="w", encoding="utf-8") as file:
        file.write(content)

print(len(games))
for game in games: # Max 100 entries
    result_player_home = []
    result_player_away = []
    result_games_home = []
    result_games_away = []
    
    result_game_name = game.get("game").get('homeTeam').get("name")+" vs "+game.get("game").get('awayTeam').get("name")
    result_game_date = game.get("game").get('date')
    print(result_game_name)

    # Team results
    for team_result in game.get("game").get('homeTeam').get("lastFiveGames"):
        if team_result.get("winner") == None:
            result_games_home.append("D")
        elif team_result.get("winner").get("slug") == game.get("game").get('homeTeam').get("slug"):
            result_games_home.append("W")
        else:
            result_games_home.append("L")
    for team_result in game.get("game").get('awayTeam').get("lastFiveGames"):
        if team_result.get("winner") == None:
            result_games_away.append("D")
        elif team_result.get("winner").get("slug") == game.get("game").get('awayTeam').get("slug"):
            result_games_away.append("W")
        else:
            result_games_away.append("L")

    # get players 
    players_home = get_players_of_team_slug(client,game.get("game").get('homeTeam').get("slug"))
    players_away = get_players_of_team_slug(client,game.get("game").get('awayTeam').get("slug"))
    #ic(players_home)
    for player in players_home:
        player_stats = get_rivals_player_stats(client,player.get("slug"))
        agg_stats = aggregate_player_stats(player_stats)
        #if agg_stats.get("percSubst") >= 80 and agg_stats.get("substScore_Avg") >= 32:
        if agg_stats.get("l15l5Performance") > 24:
            #ic(player.get("displayName"))
            #ic(agg_stats)
            result_player_home.append({
                "name": player.get("displayName"),
                "position": player.get("position"),
                "stats": agg_stats
            })
    for player in players_away:
        player_stats = get_rivals_player_stats(client,player.get("slug"))
        agg_stats = aggregate_player_stats(player_stats)
        #if agg_stats.get("percSubst") >= 80 and agg_stats.get("substScore_Avg") >= 32:
        if agg_stats.get("l15l5Performance") > 24:
            #ic(player.get("displayName"))
            #ic(agg_stats)
            result_player_away.append({
                "name": player.get("displayName"),
                "position": player.get("position"),
                "stats": agg_stats
            })
    if ( len(result_player_away) + len(result_player_home) ) > 5:
        result_game = {
            "name": result_game_name,
            "date": result_game_date,
            "home": result_player_home,
            "away": result_player_away,
            "homeTeamResults": result_games_home,
            "awayTeamResults": result_games_away
        }
        ic(result_game)
        result.append(result_game)
        build_html()

build_html()