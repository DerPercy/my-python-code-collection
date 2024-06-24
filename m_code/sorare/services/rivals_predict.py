"""
Rivals prediction

Calculate performance scores of players based on their past performance
"""

from attrs import define

from models.rivals import RivalsGame, RivalsGamePlayer
from func_sorare_rivals import PlayerStatsCalculationRule
from context import value_aggregator

""" 
========== MODELS ========== 
"""
@define
class PlayerPredictedScore:
    player_slug:str
    calculated_score: float


""" 
========== FUNCTIONS ==========
"""

def calc_predictions_from_rivals_game(rg:RivalsGame, rule: PlayerStatsCalculationRule) -> list[PlayerPredictedScore]:
    def sub_calc_player_prediction(rgp:RivalsGamePlayer, rg:RivalsGame, rule: PlayerStatsCalculationRule, home_away:str) -> PlayerPredictedScore:
        va = value_aggregator.MyValueAggregator()
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
                
        if va.has_values( ) == False:
            return None 
        
        pps = PlayerPredictedScore(
            calculated_score=va.get_average( ),
            player_slug=rgp.slug   
        )
        return pps
            
    result_list = []
    for player in rg.away_player:
        result = sub_calc_player_prediction(
            player, rg, rule, "away"
        )
        if result != None:
            result_list.append(result)
    for player in rg.home_player:
        result = sub_calc_player_prediction(
            player, rg, rule, "home"
        )
        if result != None:
            result_list.append(result)

    return result_list        


