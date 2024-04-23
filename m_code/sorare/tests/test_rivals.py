"""Test rivals functions"""
import json
from context import func_sorare_rivals

def test_dummy():
    """ calculate the scored and taken goald based on the results """
    scores_json = json.loads(scores_payload)

    scores = func_sorare_rivals.calculate_goals_of_team("union-comercio-nueva-cajamarca",scores_json.get("lastFiveGames"))
    assert scores == (4,11)
    




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