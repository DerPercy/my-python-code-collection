import statistics
import copy
import logging
import json

from client import Client
from icecream import ic


def request_game_player_score(client:Client,game_id:str,player_slug:str) -> dict:
  param = {}
  body = """
query GameLineup {
  football {
    game(id:\""""+game_id+"""\") {
      playerGameScore(playerSlug:\""""+player_slug+"""\"){
        score
      }    
    }
  }
}"""
  result = client.request(body,param,{ "resultSelector": ["data","football","game","playerGameScore"]   })
  return result 

def request_game_by_id(client:Client,game_id:str) -> dict:
    param = {}
    body = """
query GameLineup {
  football {
    game(id:\""""+game_id+"""\") {
      date
      homeFormation{
        bench {
          slug
          position
          averageScore(type:LAST_FIFTEEN_SO5_AVERAGE_SCORE)
          displayName
        }
        startingLineup{
          position
          slug
          averageScore(type:LAST_FIFTEEN_SO5_AVERAGE_SCORE)
          displayName
        }
      }
      awayFormation{
        bench {
          slug
          position
          averageScore(type:LAST_FIFTEEN_SO5_AVERAGE_SCORE)
          displayName
        }
        startingLineup{
          position
          slug
          averageScore(type:LAST_FIFTEEN_SO5_AVERAGE_SCORE)
          displayName
        }
      }
    }
  }
}"""
    game_result = client.request(body,param,{ "resultSelector": ["data","football","game"]   })
    return game_result




def calc_team_results(games_data:list[dict],team_slug:str, result_data:list[str]):
    logging.info("Calculation team results for:"+team_slug)
    if games_data == None:
        logging.error("No games data found: could not calculate result_data")
        return
    
    logging.info(json.dumps(games_data, indent=4))
  
    for team_result in games_data:
        if team_result.get("winner") == None:
            result_data.append("D")
        elif team_result.get("winner").get("slug") == team_slug:
            result_data.append("W")
        else:
            result_data.append("L")
    logging.info(result_data)



def get_last_rivals_results(client:Client) -> list[dict]:
    param = {}
    body = """
query RivalsLastGames {
  football {
    rivals {
      pastGames {
        
        cap
        slug
        myArenaChallenge {
          awayContestant {
          	score
            manager {
              user {
                slug
              }
            }
            lineup {
              appearances {
                pictureUrl
            		player {
              		slug
                  displayName
              		averageScore(type: LAST_FIFTEEN_SO5_AVERAGE_SCORE )
            			activeClub {
                    slug
                  }
                }
            		position
            		score
          		}
            }
          }
        }
        myPointsDelta
        game {
          id
          date
        }
        myLineup {
          appearances {
            pictureUrl
            player {
              slug
              displayName
              averageScore(type: LAST_FIFTEEN_SO5_AVERAGE_SCORE )
            	activeClub {
                slug
              }
            }
            position
            score
          }
        }
      }
    }
  }
}"""
    res_last_results = client.request(body,param,{ "resultSelector": ["data","football","rivals","pastGames"]   })
    result = []
    for last_res in res_last_results:
        with_match = True
        won = None
        if last_res.get("myPointsDelta") == None:
            with_match = False
        # Check win flag
        if with_match == True:
          won = True
          if last_res.get("myPointsDelta") <= 0:
            won = False
        # My own lineup
        my_lineup = []
        for appearance in last_res.get("myLineup").get("appearances"):
            my_lineup.append({
                "pictureUrl": appearance.get("pictureUrl"),
                "score": appearance.get("score")
            })
        # My other lineup
        other_lineup = []
        if with_match == True:
          for appearance in last_res.get("myArenaChallenge").get("awayContestant").get("lineup").get("appearances"):
            other_lineup.append({
                "pictureUrl": appearance.get("pictureUrl"),
                "score": appearance.get("score")
            })
        
        result.append({
            "name": last_res.get("slug"),
            "won": won,
            "withMatch": with_match,
            "myLineup": my_lineup,
            "otherLineup": other_lineup,
            "game": {
                "id": last_res.get("game").get("id")[5:]
            }
        })
        
    return result

def calc_team_off_def_indicator(games_list:list[dict]):
    """
    Calculates the team Offense/Defense indicator

    Additioanl Attributes at game:
    * homeTeamOffenseIndicator
    * homeTeamDefenseIndicator
    * awayTeamOffenseIndicator
    * awayTeamDefenseIndicator
    
    Indicator
    {
      "max": 10,
      "min":0,
      "avg": 4,
      "own": 6
    }
    """
    offense_indicator = {
      "max": 0,
      "min":0,
      "avg": 0,
      "own": 0        
    }
    defense_indicator = {
      "max": 0,
      "min":0,
      "avg": 0,
      "own": 0        
    }
    offense_scores = []
    defense_scores = []
    for game in games_list:
      offense_scores.append(game.get("homeTeamGoals")[0] * 2 + game.get("awayTeamGoals")[1])
      offense_scores.append(game.get("awayTeamGoals")[0] * 2 + game.get("homeTeamGoals")[1])
      defense_scores.append(game.get("homeTeamGoals")[1] * 2 + game.get("awayTeamGoals")[0])
      defense_scores.append(game.get("awayTeamGoals")[1] * 2 + game.get("homeTeamGoals")[0])
    offense_scores.sort()
    defense_scores.sort(reverse=True)
    #print(offense_scores)  
    #print(defense_scores)  
    offense_indicator["min"] = offense_scores[0]
    offense_indicator["max"] = offense_scores[-1]
    defense_indicator["min"] = defense_scores[0]
    defense_indicator["max"] = defense_scores[-1]
    offense_indicator["avg"] = statistics.median(offense_scores)
    defense_indicator["avg"] = statistics.median(defense_scores)

    for game in games_list:
      offense_indicator["own"] = game.get("homeTeamGoals")[0] * 2 + game.get("awayTeamGoals")[1]
      game["homeTeamOffenseIndicator"] = copy.deepcopy(offense_indicator)
      defense_indicator["own"] = game.get("homeTeamGoals")[1] * 2 + game.get("awayTeamGoals")[0]
      game["homeTeamDefenseIndicator"] = copy.deepcopy(defense_indicator)
      offense_indicator["own"] = game.get("awayTeamGoals")[0] * 2 + game.get("homeTeamGoals")[1]
      game["awayTeamOffenseIndicator"] = copy.deepcopy(offense_indicator)
      defense_indicator["own"] = game.get("awayTeamGoals")[1] * 2 + game.get("homeTeamGoals")[0]
      game["awayTeamDefenseIndicator"] = copy.deepcopy(defense_indicator)
    return games_list

def calculate_goals_of_team(team_slug:str, games_list:list[dict]) -> tuple[int,int]:
    """
    returns tuple[scored_goals,received_goals]
    """
    goals_own = 0
    goals_other = 0
    for game in games_list:
        if game.get("homeTeam").get("slug") == team_slug:
            goals_own = goals_own + game.get("homeGoals")
        else:
            goals_other = goals_other + game.get("homeGoals")
        if game.get("awayTeam").get("slug") == team_slug:
            goals_own = goals_own + game.get("awayGoals")
        else:
            goals_other = goals_other + game.get("awayGoals")

    return (goals_own,goals_other)

def aggregate_player_stats(player_stats:list[dict]) -> dict:
    played_perc = 0
    subst_perc = 0
    subst_score_avg = 0
    score_avg = 0
    l15_played_perc = 0
    l15_score_avg = 0
    l15_l5_performance = 0
    
    if len(player_stats) > 0:
        for stat in player_stats[:5]:
            if stat.get("played"):
                played_perc = played_perc + 1
                score_avg = score_avg + stat.get("score")
            if stat.get("played") and not stat.get("started"):
                subst_perc = subst_perc + 1
                subst_score_avg = subst_score_avg + stat.get("score")
        if subst_score_avg > 0:
            subst_score_avg = subst_score_avg / subst_perc
        if score_avg > 0:
            score_avg = score_avg / played_perc
        subst_perc =  100 * subst_perc / len(player_stats[:5])
        played_perc =  100 * played_perc / len(player_stats[:5])
        #L15
        for stat in player_stats[:15]:
            if stat.get("played"):
                l15_played_perc = l15_played_perc + 1
                l15_score_avg = l15_score_avg + stat.get("score")
        if l15_score_avg > 0:
            l15_score_avg = l15_score_avg / l15_played_perc

        if l15_score_avg > 0:
            l15_l5_performance = int((( score_avg / l15_score_avg ) - 1 ) * 100)
    return {
        "percPlayed": played_perc,
        "percSubst": subst_perc,
        "scoreAvg": score_avg,
        "l15ScoreAvg": l15_score_avg,
        "l15l5Performance": l15_l5_performance,
        "substScore_Avg": subst_score_avg
    }

def get_rivals_player_stats(client:Client, player_slug:str,team_slug:str,home_away:str) -> list[dict]:
# Get leaderboard data
    param = {
		"playerSlug": player_slug
	}
    body = """
query RivalsTeamPlayerScore($playerSlug: String!) {
  football {
    player(slug:$playerSlug) {
      averageScore(type:LAST_FIFTEEN_SO5_AVERAGE_SCORE)
      position
      displayName
      allSo5Scores(first:40){
        nodes {
          game { homeTeam { slug } awayTeam { slug } so5Fixture { gameWeek startDate } }
          playerGameStats {
            gameStarted
          }
          score
          decisiveScore {
            category points stat statValue totalScore
          }
          detailedScore {
            category points stat statValue totalScore
          }
          allAroundStats {
            category points stat statValue totalScore  
          }
        }
      }
    }
  }
}
"""
    #leaderBoardResult = json.loads(context["rootHandler"].external().getRequestHandler().request("sorareHeroesGetRankings",param))
    player_data = client.request(body,param,{ "resultSelector": ["data","football","player"]   })
    unfiltered_score_list = player_data.get("allSo5Scores").get("nodes")
    
    # Filter scores START
    score_list = []
    for score_entry in unfiltered_score_list:
      # only games where the player started
      if score_entry.get("playerGameStats").get("gameStarted") == None:
          continue
      # respect home/away scores
      if home_away == "home" and score_entry.get("game").get("homeTeam").get("slug") != team_slug:
          continue
      if home_away == "away" and score_entry.get("game").get("awayTeam").get("slug") != team_slug:
          continue
      score_list.append(score_entry)
    # Filter scores END

    avg_score = 0
    all_around_avg_score = 0
    num_played = 0
    num_games = len(score_list)
    tactic_acc_pass = 0
    score_performance = 0
    l15 = player_data.get("averageScore","???")
    detailed_scores = {}
    for score in score_list:
        if score.get("score") > 0:
            num_played = num_played + 1
            avg_score = avg_score + score.get("score")
            all_around_avg_score = all_around_avg_score + score.get("score") - score.get("decisiveScore").get("totalScore")
            tactic_acc_pass = tactic_acc_pass + get_detailed_score_count(score.get("detailedScore"),"accurate_pass")
            for det_score in score.get("detailedScore"):
                if detailed_scores.get(det_score.get("stat"),None) == None:
                    detailed_scores[det_score.get("stat")] = 0
                detailed_scores[det_score.get("stat")] = detailed_scores[det_score.get("stat")] + det_score.get("statValue")

    if num_played > 0:
      avg_score = avg_score / num_played
      all_around_avg_score = all_around_avg_score / num_played
      tactic_acc_pass = tactic_acc_pass / num_played
      if l15 > 0:
        score_performance = ( ( avg_score / l15 ) - 1 ) * 100 
      for det_score_id in detailed_scores:
          detailed_scores[det_score_id] = detailed_scores[det_score_id] / num_played

    result = {
        "name": player_data.get("displayName","???"),
        "position": player_data.get("position","???"),
        "l15": l15,
        "numGames": num_games,
        "gamesScore": avg_score,
        "scorePerformance": score_performance,
        "avgAllAroundScore": all_around_avg_score,
        "tempDetScores": detailed_scores,
        "tactic":{
            "accuratePass": tactic_acc_pass,
            "dribblings": detailed_scores.get("won_contest",0),
            "shotsOnGoal": detailed_scores.get("ontarget_scoring_att",0),
            "clearance": detailed_scores.get("effective_clearance",0),
            "duelWon": detailed_scores.get("duel_won",0)
        }
    }
    
#    result = []
#    for score in scores:
#        started = score.get("playerGameStats").get("gameStarted") != None
#        played = score.get("score") > 0
#        result.append({
#            "started": started,
#
#            "played": played,
#            "score": score.get("score")
#        }) 
    return result

def get_detailed_score_count(detailed_score_list:dict,key:str) -> float:
    for det_score in detailed_score_list:
        if det_score.get("stat") == key:
            return det_score.get("statValue")
    return 0


def get_players_of_team_slug(client:Client,team_slug:str) ->list[dict]:
    # Get leaderboard data
    param = {
		"teamSlug": team_slug
	}
    body = """
query RivalsTeamPlayer($teamSlug: String!) {
  football {
    club(slug: $teamSlug) {
      activePlayers(first:100){
        nodes {
          slug
          displayName
          position
        }
      }
    }
  }
}
"""
    #leaderBoardResult = json.loads(context["rootHandler"].external().getRequestHandler().request("sorareHeroesGetRankings",param))
    players = client.request(body,param,{ "resultSelector": ["data","football","club","activePlayers","nodes"]   })
    return players

def get_next_rivals_games(client:Client,num:int) -> list[dict]:
    # Get leaderboard data
    param = {
		
	}
    game_payload = """
  date
  winner { slug }
  homeTeam { slug }
  homeGoals
  awayTeam { slug }
  awayGoals
"""
    body = """
query Rivals {
  football {
    rivals {
#      upcomingGames(query: "Bundesliga") {
      upcomingGames {
        cap slug
        game {
          date
          homeTeam {
            __typename
          	... on TeamInterface {
              name slug lastFiveGames{
                """+ game_payload+"""
              }
            }
          }
          awayTeam {
            __typename
          	... on TeamInterface {
              name slug lastFiveGames{
                """+ game_payload+"""
              }
            }
          }
        }
      }
    }
  }
}
"""
    #leaderBoardResult = json.loads(context["rootHandler"].external().getRequestHandler().request("sorareHeroesGetRankings",param))
    games = client.request(body,param,{ "resultSelector": ["data","football","rivals","upcomingGames"]   })
    # Add last 15 games
    for game in games[:num]:
        home_team_slug = game.get("game").get("homeTeam").get("slug")
        home_team_results = request_latest_games_of_team(client,home_team_slug,12,game_payload)
        home_team_result_list = []
        for home_team_result in home_team_results:
            if home_team_result.get("homeTeam").get("slug") == home_team_slug:
              home_team_result_list.append(home_team_result)
        game.get("game").get("homeTeam")["lastFiveGamesHomeAway"] = home_team_result_list[:5]
        game.get("game").get("homeTeam")["lastFiveGamesHomeAway"].reverse()

        away_team_slug = game.get("game").get("awayTeam").get("slug")
        away_team_results = request_latest_games_of_team(client,away_team_slug,12,game_payload)
        away_team_result_list = []
        for away_team_result in away_team_results:
            if away_team_result.get("awayTeam").get("slug") == away_team_slug:
              away_team_result_list.append(away_team_result)
        
        game.get("game").get("awayTeam")["lastFiveGamesHomeAway"] = away_team_result_list[:5]
        game.get("game").get("awayTeam")["lastFiveGamesHomeAway"].reverse()
    return games

def request_latest_games_of_team(client:Client, team_slug:str, number_games:int, game_payload:str) -> list[dict]:
  body = """
query Team {
  football {
    club(slug: \""""+team_slug+"""\") {
      latestGames(first: """+str(number_games)+"""){
        nodes {
          """+game_payload+"""
        }
      }
    }
  }
}
"""
  games = client.request(body,{},{ "resultSelector": ["data","football","club","latestGames","nodes"]   })
  logging.info(json.dumps(games, indent=4))
  return games
