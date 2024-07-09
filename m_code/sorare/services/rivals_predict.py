"""
Rivals prediction

Calculate performance scores of players based on their past performance
"""
import logging

from attrs import define

from models.rivals import RivalsGame, RivalsGamePlayer
from func_sorare_rivals import PlayerStatsCalculationRule
from context import value_aggregator, hash_map

""" 
========== MODELS ========== 
"""
@define
class PlayerPredictedScore:
    player_slug:str
    calculated_score: float
    stats_map: hash_map.MyHashMap[value_aggregator.MyValueAggregator] = []
    game_slugs: list[str] = []

    def get_average_count_for_stat(self,key:str) -> float:
        if self.stats_map.get_item(key) == None:
            return 0
        return self.stats_map.get_item(key).get_average( )


""" 
========== FUNCTIONS ==========
"""

def get_calc_rule_by_competition_slug(comp_slug:str) -> PlayerStatsCalculationRule:
    calc_rule = PlayerStatsCalculationRule(numberOfGames=100, respectHomeAway=True)
    if comp_slug == "european-championship":
        # EM-2024: Didnot consider home/away and only the latest 5 games 
        calc_rule = PlayerStatsCalculationRule(numberOfGames=3, respectHomeAway=False)
    return calc_rule

def calc_predictions_from_rivals_game(rg:RivalsGame, rule: PlayerStatsCalculationRule = None, game_settings: dict = {}) -> list[PlayerPredictedScore]:
    if rule == None:
        rule = get_calc_rule_by_competition_slug(rg.competition_slug)
    def sub_calc_player_prediction(rgp:RivalsGamePlayer, rg:RivalsGame, rule: PlayerStatsCalculationRule, home_away:str,game_settings: dict) -> PlayerPredictedScore:
        va = value_aggregator.MyValueAggregator()
        stats_map = hash_map.MyHashMap[value_aggregator.MyValueAggregator]()
        games_list = []
        for game in rgp.games_list:
            if game.game_started != True: # Only respect games, where the player started
                continue
            if rule.respectHomeAway == True:
                if home_away == "home" and game.home_team_slug != rgp.team_slug:
                    continue
                if home_away == "away" and game.away_team_slug != rgp.team_slug:
                    continue
            else:
                if game.away_team_slug != rgp.team_slug and game.home_team_slug != rgp.team_slug:
                    # if current team not in match (f.e. national match in club prediction)
                    continue
            if va.count( ) >= rule.numberOfGames:
                continue
            va.add_value(game.game_score)
            games_list.append(game.rivals_game_slug)
            for score_key in game.get_detailed_score_keys():
                if stats_map.get_item(score_key) == None:
                    stats_map.set_item(k=score_key,v=value_aggregator.MyValueAggregator())
                stats_map.get_item(score_key).add_value(game.get_detailed_score_count(score_key))
            #game.get_detailed_score_value("accurate_pass")
            #"won_contest"
            #"ontarget_scoring_att"
            #"effective_clearance"
            #"duel_won"
                
        if va.has_values( ) == False:
            return None 
        
        game_bet_rate = 1
        rate_home = float(game_settings.get("rate_home",1))
        rate_away = float(game_settings.get("rate_away",1))
        if home_away == "home":
            game_bet_rate = rate_away / rate_home
        else:
            game_bet_rate = rate_home / rate_away
        # Abschwächen
        game_bet_rate = game_bet_rate**(1/4)
        pps = PlayerPredictedScore(
            calculated_score=va.get_average( ) * game_bet_rate,
            player_slug=rgp.slug,
            stats_map=stats_map,
            game_slugs= games_list  
        )
        return pps
            
    result_list = []
    for player in rg.away_player:
        result = sub_calc_player_prediction(
            player, rg, rule, "away",game_settings
        )
        if result != None:
            result_list.append(result)
    for player in rg.home_player:
        result = sub_calc_player_prediction(
            player, rg, rule, "home",game_settings
        )
        if result != None:
            result_list.append(result)

    return result_list        


