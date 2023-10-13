import os
from .client import Client
from .fixture import get_latest_fixtures
from .context import file_func
from .club import get_club_details,determine_opponent_club


def calc_percentageplayed(raw_data):
    return scoreboard_get_percentageplayed(raw_data.get("scores"),5)

def calc_averagescore(raw_data):
    l15_score = scoreboard_get_averageScore(raw_data.get("scores"),15)
    if l15_score == 0:
        return 0
    l5_score = scoreboard_get_averageScore(raw_data.get("scores"),5)
  
    return ((l5_score * 100) / l15_score ) - 100 


def eval_percentageplayed(value):
    """ 
    100 % => 10 
    0% => 0
    """
    return value / 10

def eval_averagescore(value):
    """ 
    +20 % => 10 
    0% => 0
    """
    if value > 20:
        return 10
    if value <= 0:
        return 0
    return value / 2

def calc_nextopponent(raw_data):
    l15_score = scoreboard_get_averageScore(raw_data.get("scores"),15)
    if l15_score == 0:
        return 0
    
    oppAverage = 0 
    if raw_data.get("nextTeamScores",None) == None:
        return None
    if len(raw_data.get("nextTeamScores")) == 0:
        return None
    for oppScore in raw_data.get("nextTeamScores"):
        oppAverage = oppAverage + oppScore
    oppAverage = oppAverage / len(raw_data.get("nextTeamScores"))

    return ((oppAverage * 100) / l15_score ) - 100 

def eval_nextopponent(value):
    """ 
    +20 % => 10 
    0% => 0
    """
    if value > 20:
        return 10
    if value <= 0:
        return 0
    return value / 2

def data_reader_nextopponent(raw_data,score):
   score["gw"] = raw_data.get("nextOpponentGW")
   return


def get_player_scoreboard(client:Client,player_slug:str):
    fixture = get_latest_fixtures(client)[0]
    cachefile_scores_plus = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/player/"+player_slug+"/scores_plus.json"
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/player/"+player_slug+"/scoreboard.json"
    
    raw_data = get_scores_of_player(client,player_slug)
    scores = raw_data.get("scores")
    next_opponent = None
      
    # Next games of team
    if raw_data.get("head").get("activeClub",None) == None:
      my_club_slug = None
    else:
      my_club_slug = raw_data.get("head").get("activeClub").get("slug")
      clubDetails = get_club_details(client,my_club_slug)
      next_opponent = None
      next_opp_gw = None
      for upcomingGame in clubDetails.get("upcomingGames"):
        if upcomingGame.get("so5Fixture").get("gameWeek") < fixture.gameWeek:
           continue
        opponent = determine_opponent_club(my_club_slug,upcomingGame)
        next_opp_gw = upcomingGame.get("so5Fixture").get("gameWeek")
        print(opponent)
        next_opponent = opponent.get("opponent")
        break
      if next_opponent != None:
        print("Next opponent:"+next_opponent)
        last_3_scores = []
        for score in raw_data.get("scores"):
          if len(last_3_scores) >= 3:
            break
          opp = determine_opponent_club(my_club_slug,score.get("game")).get("opponent")
          #print(opp)
          if opp == next_opponent:
            last_3_scores.append(score.get("score"))
            #print(">>>>>>>>"+str(score.get("score")))
        #print(last_3_scores)
        raw_data["nextTeamScores"] = last_3_scores
        raw_data["nextOpponentSlug"] = opponent.get("opponent")
        raw_data["nextOpponentGW"] = next_opp_gw
    file_func.write_json_to_file(raw_data,cachefile_scores_plus)  
    #print(scoreboard_get_percentageplayed(scores,5))
    #print(scoreboard_get_percentageplayed(scores,15))
    #print(scoreboard_get_averageScore(scores,5))
    #print(scoreboard_get_averageScore(scores,15))
    scoreboard = [{
        "description": "Percentage played",
        "calculator": calc_percentageplayed,
        "evaluator": eval_percentageplayed,
        "weight": 0.5
    },{
        "description": "Score improvement",
        "calculator": calc_averagescore,
        "evaluator": eval_averagescore,
        "weight": 0.5
    },{
        "description": "Next opponent",
        "dataReader": data_reader_nextopponent,
        "calculator": calc_nextopponent,
        "evaluator": eval_nextopponent,
        "weight": 0.5
    }]
    sum = 0
    weight_sum = 0
    for score in scoreboard:
        if score.get("dataReader") != None:
           score.get("dataReader")(raw_data,score)
           del score["dataReader"]
        
        score["calculated"] = score["calculator"](raw_data)
        del score["calculator"]
        if score["calculated"] != None:
          weight_sum = weight_sum + score["weight"]
          score["evaluated"] = score["evaluator"](score["calculated"])
        del score["evaluator"]
    for score in scoreboard:
      if score["calculated"] != None:
        sum = sum +  ( score["evaluated"] * ( score["weight"]  / weight_sum ) )
    
    
    #print(scoreboard)
    #print(sum)
    cache = {
        "player": {
           "slug": player_slug,
           "name": raw_data.get("head").get("displayName"),
           "position": raw_data.get("head").get("position"),
           "age": raw_data.get("head").get("age"),           
        },
        "team": {
           "slug": my_club_slug
        },
        "nextGame": next_opponent,
        "scoreboard": scoreboard,
        "scoreboard_total": sum
    }
    file_func.write_json_to_file(cache,cachefile)
    return cache


def scoreboard_get_percentageplayed(score_list,number):
    scores = score_list[:number]
    count = 0
    for score in scores:
        if score.get("playerGameStats").get("minsPlayed") != None :
            if score.get("playerGameStats").get("minsPlayed") != 0:
              count =count + 1
    return (count * 100) / number

def scoreboard_get_averageScore(score_list,number):
    scores = score_list[:number]
    sum = 0
    count = 0
    for score in scores:
        if score.get("score") > 0:
            sum = sum + score.get("score")
            count = count + 1
    if count == 0:
        return 0
    return sum / count

def get_scores_of_player(client:Client,player_slug:str):
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/player/"+player_slug+"/scores.json"
    
    body = """
query Player($endCursor: String $slug: String! $first: Int!) {
  football {
    player(slug: $slug) {
      displayName
      age
      averageScore(type: LAST_FIFTEEN_SO5_AVERAGE_SCORE)
      position
      activeClub {
        slug
        name
      }
      activeNationalTeam {
        slug
      }
      activeSuspensions {
        reason
        competition {
          slug
        }
      }
      activeInjuries {
        kind
        expectedEndDate
      }
      
      allSo5Scores (first:$first after:$endCursor){
        pageInfo { endCursor hasNextPage hasPreviousPage startCursor }
        nodes {
          score
          decisiveScore {
            totalScore
          }
          game {
            status
            so5Fixture {
              gameWeek
            }
             homeTeam {
          __typename ... on TeamInterface {
            name
            slug
          }
        }
        awayTeam {
          __typename ... on TeamInterface {
            name
            slug
          }
        }
            competition {
          name
          slug
        }
          }
          playerGameStats {
            goals
            minsPlayed
            team {
              __typename ... on TeamInterface {
                name
                id
                slug
              }
            }
          }
        }
      }
    }
  }
}

"""
    variables = {
        "slug": player_slug,
        "first": 50
    }
    options = {
        "resultSelector": ["data","football","player","allSo5Scores","nodes"],
        "pagination": {
            "targetNumber": 100000,
            "paginationVariable": "endCursor",
            "cursorSelector": ["data","football","player","allSo5Scores","pageInfo","endCursor"]
        }
    }
    result_list = client.request(body,variables,options)
    head_data = client.request(body,{
        "slug": player_slug,
        "first": 0
    },{
        "resultSelector": ["data","football","player"],
    })
    cache = {
        "head": head_data,
        "scores": result_list,
    }
    file_func.write_json_to_file(cache,cachefile)

    return cache