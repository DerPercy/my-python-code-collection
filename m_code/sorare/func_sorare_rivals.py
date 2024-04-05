from client import Client

def aggregate_player_stats(player_stats:list[dict]) -> dict:
    played_perc = 0
    subst_perc = 0
    subst_score_avg = 0
    if len(player_stats) > 0:
        for stat in player_stats:
            if stat.get("played"):
                played_perc = played_perc + 1
            if stat.get("played") and not stat.get("started"):
                subst_perc = subst_perc + 1
                subst_score_avg = subst_score_avg + stat.get("score")
        if subst_score_avg > 0:
            subst_score_avg = subst_score_avg / subst_perc
        subst_perc =  100 * subst_perc / len(player_stats)
        played_perc =  100 * played_perc / len(player_stats)
    return {
        "percPlayed": played_perc,
        "percSubst": subst_perc,
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
      allSo5Scores(first:5){
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
      upcomingGames {
        game {
          date
          homeTeam {
            __typename
          	... on TeamInterface {
              name slug
            }
          }
          awayTeam {
            __typename
          	... on TeamInterface {
              name slug
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
