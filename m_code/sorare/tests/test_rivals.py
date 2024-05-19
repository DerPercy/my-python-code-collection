"""Test rivals functions"""
import json
from context import func_sorare_rivals

def test_team_offense_defense_ranking():
    teams_json = json.loads(teams_payload)
    teams_with_ranking = func_sorare_rivals.calc_team_off_def_indicator(teams_json)
    assert teams_with_ranking[0].get("homeTeamOffenseIndicator") == { "max": 19, "min": 5, "avg": 11, "own":5 }
    assert teams_with_ranking[0].get("awayTeamOffenseIndicator") == { "max": 19, "min": 5, "avg": 11, "own":10 }
    #assert teams_with_ranking[0].get("homeTeamDefenseIndicator") == { "max": 4, "min": 12, "avg": 6.5, "own":7 }
    #assert teams_with_ranking[0].get("awayTeamDefenseIndicator") == { "max": 4, "min": 12, "avg": 6.5, "own":4 }
    #assert teams_with_ranking[1].get("homeTeamOffenseIndicator") == { "max": 12, "min": 4, "avg": 6.5, "own":6 }
    #assert teams_with_ranking[1].get("awayTeamOffenseIndicator") == { "max": 12, "min": 4, "avg": 6.5, "own":6 }
    #assert teams_with_ranking[1].get("homeTeamDefenseIndicator") == { "max": 4, "min": 12, "avg": 6.5, "own":6 }
    #assert teams_with_ranking[1].get("awayTeamDefenseIndicator") == { "max": 4, "min": 12, "avg": 6.5, "own":6 }

def test_scores():
    """ calculate the scored and taken goald based on the results """
    scores_json = json.loads(scores_payload)

    scores = func_sorare_rivals.calculate_goals_of_team("union-comercio-nueva-cajamarca",scores_json.get("lastFiveGames"))
    assert scores == (4,11)
    

teams_payload = """
[{
    "homeTeamGoals": [1,4],
    "awayTeamGoals": [3,3]
},{
    "homeTeamGoals": [4,0],
    "awayTeamGoals": [6,2]
},{
    "homeTeamGoals": [5,5],
    "awayTeamGoals": [7,2]
}]
"""


scores_payload = """
{
"lastFiveGames": [
                  {
                    "winner": null,
                    "homeTeam": {
                      "slug": "sport-huancayo-huancayo"
                    },
                    "homeGoals": 2,
                    "awayTeam": {
                      "slug": "union-comercio-nueva-cajamarca"
                    },
                    "awayGoals": 2
                  },
                  {
                    "winner": {
                      "slug": "deportivo-garcilaso-cuzco"
                    },
                    "homeTeam": {
                      "slug": "union-comercio-nueva-cajamarca"
                    },
                    "homeGoals": 0,
                    "awayTeam": {
                      "slug": "deportivo-garcilaso-cuzco"
                    },
                    "awayGoals": 4
                  },
                  {
                    "winner": {
                      "slug": "real-garcilaso-cuzco"
                    },
                    "homeTeam": {
                      "slug": "real-garcilaso-cuzco"
                    },
                    "homeGoals": 1,
                    "awayTeam": {
                      "slug": "union-comercio-nueva-cajamarca"
                    },
                    "awayGoals": 0
                  },
                  {
                    "winner": null,
                    "homeTeam": {
                      "slug": "union-comercio-nueva-cajamarca"
                    },
                    "homeGoals": 2,
                    "awayTeam": {
                      "slug": "cesar-vallejo-trujillo"
                    },
                    "awayGoals": 2
                  },
                  {
                    "winner": {
                      "slug": "alianza-atletico-sullana"
                    },
                    "homeTeam": {
                      "slug": "alianza-atletico-sullana"
                    },
                    "homeGoals": 2,
                    "awayTeam": {
                      "slug": "union-comercio-nueva-cajamarca"
                    },
                    "awayGoals": 0
                  }
                ]
}
"""