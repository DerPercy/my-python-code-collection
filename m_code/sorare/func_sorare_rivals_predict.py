from attrs import define
from context import file_func
import logging
from services import lineup_ranking,rivals_tactic
import func_sorare_rivals
from func_sorare_rivals import calculate_rivals_player_stats, PlayerStats
from context import hash_map
"""
Functions for Lineup predictions
"""


def predict_best_lineup_of_game( game_slug:str) -> tuple[list[str],str]:
    game = file_func.read_json_from_file(
        filename="./temp/rivals/games_upcoming/"+game_slug+"/game_info.json",
    )
    if game.get("slug",None) == None:
        logging.info("No game info on filesystem found! Exit.")
        return
    logging.info("Checking "+game["slug"])
    starting_player_slugs = []
#    if game["formationKnown"] != True:
#        lu_found = False
#        if lu_found == False:
#            continue
    
    draftable_player_map = file_func.read_json_from_file(
        filename="./temp/rivals/games_upcoming/"+game["slug"]+"/draftable_player_map.json"
    )
    draftable_player_map = func_sorare_rivals.draftable_player_ids_to_hashmap(draftable_player_map)
    
    
    logging.info("Formation known! Checking lineup")
    #game_details = func_sorare_rivals.request_game_by_id(client,game["game"]["id"][5:])
    game_details = file_func.read_json_from_file(
        filename="./temp/rivals/games_upcoming/"+game["slug"]+"/game_details.json"
    )
    
    game_data = file_func.read_json_from_file("./temp/rivals/games/"+game["slug"]+".json")
    
    logging.info("Get tactics")
    game_tactic_def_list = rivals_tactic.build_tactic_list_from_api_response(game.get("lineupTactics"))
    #logging.info(game_tactic_def_list)
    if len(starting_player_slugs) > 0:
        logging.info("Already manual lineup found. Did not consider data from sorare.")
    else:
        for position in game_details["homeFormation"]["startingLineup"]:
            for player in position:
                starting_player_slugs.append(player["slug"])
        for position in game_details["awayFormation"]["startingLineup"]:
            for player in position:
                starting_player_slugs.append(player["slug"])
    
    player_stats_map = hash_map.MyHashMap[PlayerStats]()

    logging.info("Found staring players")
    logging.info(starting_player_slugs)
    starting_player_data = {}
    for player in game_data["home"]:
        starting_player_data[player["slug"]] = player
        #player_stats_map.set_item(
        #    k=player["slug"],
        #    v=calculate_rivals_player_stats(
        #        calc_rule=
        #        home_away=
        #        player_data_model=
        #        team_slug=
        #        unfiltered_score_list=
        #    )
        #)
    for player in game_data["away"]:
        starting_player_data[player["slug"]] = player
    ranking_players = []
    for player_slug in starting_player_slugs:
        if starting_player_data.get(player_slug,None) == None:
            logging.warn("Not enough data for "+player_slug+" found! Did not consider in lineup.")
            continue
        player_data = starting_player_data[player_slug]
        
        cap_score = draftable_player_map.get_item(player_slug).capValue
        
        #if cap_score < 25:
        #    cap_score = 25

        player_pos = player_data["position"]

        #calculate_rivals_player_stats(calc_rule=)
        #player["unfilteredScores"]
        ranking_players.append(lineup_ranking.Player(
            cap_score=cap_score,
            entity_data=player_data,
            position=player_pos[:1],
            score=player_data["gamesScore"], # <<<<<< Need to be calculated by strategy
            #score=player_stats_map.get_item(player_slug).gamesScore, # <<<<<< Need to be calculated by strategy
            detailed_score_list=rivals_tactic.conv_object_to_player_detailed_scores(player_data["tempDetScores"])
        ))
    best_lineup = lineup_ranking.calculate_best_lineup(
        players=ranking_players,
        cap_limit=float(game["cap"]),
        tactic_def_list=game_tactic_def_list
    )
    top_team = best_lineup[0]
    if len(top_team) == 0:
        logging.warning("No lineup found")
    else:
        logging.info("Lineup found:")
        for player in top_team:
            logging.info(player["name"])
        logging.info("Captain:")
    return best_lineup
        #logging.info(best_lineup[2])
        #upcoming_games.append({
        #    "gameSlug": game["slug"],
        #    "topTeam": top_team,
        #    "topTeamTactics": best_lineup[1],
        #    "captainSlug": best_lineup[2]["slug"]
        #})