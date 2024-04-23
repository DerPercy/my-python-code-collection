from client import Client
from icecream import ic


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

def get_rivals_player_stats(client:Client, player_slug:str) -> list[dict]:
# Get leaderboard data
    param = {
		"playerSlug": player_slug
	}
    body = """
query RivalsTeamPlayerScore($playerSlug: String!) {
  football {
    player(slug:$playerSlug) {
      allSo5Scores(first:15){
        nodes {
          game { so5Fixture { gameWeek } }
          playerGameStats {
            gameStarted
          }
          score
        }
      }
    }
  }
}
"""
    #leaderBoardResult = json.loads(context["rootHandler"].external().getRequestHandler().request("sorareHeroesGetRankings",param))
    scores = client.request(body,param,{ "resultSelector": ["data","football","player","allSo5Scores","nodes"]   })
    result = []
    for score in scores:
        started = score.get("playerGameStats").get("gameStarted") != None
        played = score.get("score") > 0
        result.append({
            "started": started,
            "played": played,
            "score": score.get("score")
        }) 
    return result

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

def get_next_rivals_games(client:Client) -> list[dict]:
    # Get leaderboard data
    param = {
		
	}
    body = """
query Rivals {
  football {
    rivals {
#      upcomingGames(query: "Bundesliga") {
      upcomingGames {
         game {
          date
          homeTeam {
            __typename
          	... on TeamInterface {
              name slug lastFiveGames{
                winner{ slug }
                homeTeam { slug }
                homeGoals
                awayTeam { slug }
                awayGoals
              }
            }
          }
          awayTeam {
            __typename
          	... on TeamInterface {
              name slug lastFiveGames{
                winner { slug }
                homeTeam { slug }
                homeGoals
                awayTeam { slug }
                awayGoals

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
    return games
