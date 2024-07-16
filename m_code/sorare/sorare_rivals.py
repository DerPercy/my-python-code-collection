from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2, CoinStackHandler,AssetHandler, file_func,hash_map
from models.tax_entry import TaxEntry
import logging, logging.handlers
import os
from dotenv import load_dotenv
from icecream import ic
from datetime import datetime
import func_sorare_rivals
from func_sorare_rivals import get_next_rivals_games, get_players_of_team_slug, get_rivals_player_stats, aggregate_player_stats
import func_sorare_rivals
import argparse, sys
import cattrs
from models.rivals import RivalsGame,create_rivals_game_from_api_response, read_rivals_game_from_fileSystem
from services.rivals_predict import calc_predictions_from_rivals_game, PlayerPredictedScore, PlayerStatsCalculationRule,calc_strategy_container
'''
Initializing
'''
# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--logfile", help="Specify the logfile destination")
parser.add_argument("--settingsfile", help="Path of the game settings")

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
logging.info("Starting sorare_rivals.py")

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

settings_file = "./temp/comp_settings.json"
if args.settingsfile != None:
    #logging.info("File found")
    settings_file = args.settingsfile
game_settings_map = file_func.read_json_from_file(settings_file)
#logging.info(game_settings_map)


num_games = 27
games = get_next_rivals_games(client,num_games)
#ic(games)

result = []

def build_html():
    global result
    global game_settings_map
    environment = myjinja2.get_environment()
    template = environment.get_template("rivals.jinja2")

    content = template.render(
        data = {
            "result_games": result,
            "game_settings_map": game_settings_map
        }
    )
    with open("temp/sorare-rivals-report.html", mode="w", encoding="utf-8") as file:
        file.write(content)

logging.info(len(games))
games = games[:num_games] # Max 100 entries
for game in games: 
    result_player_home = []
    result_player_away = []
    result_games_home = []
    result_games_away = []
    result_goals_home = (0,0)
    result_goals_away = (0,0)
    result_games_home_all = []
    result_games_away_all = []
    
    result_game_name = game.get("game").get('homeTeam').get("name")+" vs "+game.get("game").get('awayTeam').get("name")
    result_game_date = game.get("game").get('date')
    logging.info(result_game_name)
    if game_settings_map.get(game.get("slug")) == None:
        game_settings_map[game.get("slug")] = {
            "rate_home": 1,
            "rate_away": 1
        }

    # Team results
    func_sorare_rivals.calc_team_results(
        game.get("game").get('homeTeam').get("lastFiveGamesHomeAway"),
        game.get("game").get('homeTeam').get("slug"),
        result_games_home
    )
    func_sorare_rivals.calc_team_results(
        game.get("game").get('awayTeam').get("lastFiveGamesHomeAway"),
        game.get("game").get('awayTeam').get("slug"),
        result_games_away
    )
    func_sorare_rivals.calc_team_results(
        game.get("game").get('homeTeam').get("lastFiveGames"),
        game.get("game").get('homeTeam').get("slug"),
        result_games_home_all
    )
    func_sorare_rivals.calc_team_results(
        game.get("game").get('awayTeam').get("lastFiveGames"),
        game.get("game").get('awayTeam').get("slug"),
        result_games_away_all
    )

    # Team goals
    result_goals_home = func_sorare_rivals.calculate_goals_of_team(game.get("game").get('homeTeam').get("slug"),game.get("game").get('homeTeam').get("lastFiveGamesHomeAway"))
    result_goals_away = func_sorare_rivals.calculate_goals_of_team(game.get("game").get('awayTeam').get("slug"),game.get("game").get('awayTeam').get("lastFiveGamesHomeAway"))
    #logging.info(result_goals_home)
    #logging.info(result_goals_away)
    # get players 
    players_home = get_players_of_team_slug(client,game.get("game").get('homeTeam').get("slug"))
    players_away = get_players_of_team_slug(client,game.get("game").get('awayTeam').get("slug"))
    #ic(players_home)

    def player_sorter(player:func_sorare_rivals.PlayerStats):
        pos = player.position
        if pos == "Goalkeeper":
            return 1
        elif pos == "Defender":
            return 2
        elif pos == "Midfielder":
            return 3
        elif pos == "Forward":
            return 4
        return 5
    
    calc_rule = func_sorare_rivals.PlayerStatsCalculationRule(numberOfGames=100, respectHomeAway=True)

    if game.get("game").get("competition").get("slug") == "european-championship":
        # EM-2024: Didnot consider home/away and only the latest 5 games 
        calc_rule = func_sorare_rivals.PlayerStatsCalculationRule(numberOfGames=3, respectHomeAway=False)

    #if game.get("game").get("competition").get("slug") in []:
    #    logging.info("Game in a special competition: ignore home/away player logic")
    #    calc_rule.respectHomeAway = False

    for player in players_home:
        player_stats = get_rivals_player_stats(client,player.get("slug"),game.get("game").get('homeTeam').get("slug"),"home",calc_rule)
        if player_stats.numGames > 0:
            result_player_home.append(player_stats)
    result_player_home.sort(key=player_sorter)
    for player in players_away:
        player_stats = get_rivals_player_stats(client,player.get("slug"),game.get("game").get('awayTeam').get("slug"),"away",calc_rule)
        if player_stats.numGames > 0:
            result_player_away.append(player_stats)
    result_player_away.sort(key=player_sorter)
    
    #if ( len(result_player_away) + len(result_player_home) ) > -1: #5:
    result_game = {
        "name": result_game_name,
        "competitionSlug": game.get("game").get("competition").get("slug"),
        "slug": game.get("slug"),
        "date": result_game_date,
        "homeTeamSlug": game.get("game").get("homeTeam").get("slug"),
        "awayTeamSlug": game.get("game").get("awayTeam").get("slug"),        
        "home": cattrs.unstructure(result_player_home),
        "away": cattrs.unstructure(result_player_away),
        "homeTeamResults": result_games_home,
        "awayTeamResults": result_games_away,
        "homeTeamResultsAll": result_games_home_all,
        "awayTeamResultsAll": result_games_away_all,
        "homeTeamGoals": result_goals_home,
        "awayTeamGoals": result_goals_away
    }
    #ic(result_game)
    #file_func.write_json_to_file(result_game,"./temp/rivals/games/"+game.get("slug")+".json")
    rg = create_rivals_game_from_api_response(result_game)
    #rg.save_on_filessystem("./temp/rivals/games/")
    #rg = read_rivals_game_from_fileSystem("./temp/rivals/games/",game.get("slug"))
    list_predictions = calc_predictions_from_rivals_game(rg,calc_rule,game_settings_map[game.get("slug")])
    pred_map = hash_map.create_from_list(
        map_type=PlayerPredictedScore,
        entry_list=list_predictions,
        key_field="player_slug"
    )
    result_game["pred_map"] = pred_map


    # Strategies
    calc_map = hash_map.MyHashMap[PlayerStatsCalculationRule]()
    calc_map.set_item(
        k="default",
        v=calc_rule
    )
    calc_map.set_item(
        k="l5_ha",
        v=PlayerStatsCalculationRule(respectHomeAway=True,numberOfGames=5)
    )
    calc_map.set_item(
        k="l5",
        v=PlayerStatsCalculationRule(respectHomeAway=False,numberOfGames=5)
    )
    calc_map.set_item(
        k="l15_ha",
        v=PlayerStatsCalculationRule(respectHomeAway=True,numberOfGames=15)
    )
    
    strategy = calc_strategy_container(rg,calc_map)

    result_game["strategies"] = strategy

    json = hash_map.prepare_converter(cattrs.GenConverter()).unstructure(strategy)
    file_func.write_json_to_file(json,"./temp/rivals/games/"+game.get("slug")+"/strategies.json")
    

    result.append(result_game)


    # Calculate stats
    # Team score_index
    result = func_sorare_rivals.calc_team_off_def_indicator(result)
    build_html()

build_html()