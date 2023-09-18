from .client import Client
from .models.ranking import Ranking

import json

def get_rankings_of_leader_board_slug(client:Client,leader_board_slug:str,number: int) -> list[Ranking]:
    body = """
query RankingsQuery($leaderBoardSlug: String!, $afterCursor: String) {
  football {
    so5 {
      so5Leaderboard( slug: $leaderBoardSlug ) {
        so5Rankings( first: 50 after: $afterCursor) {
          pageInfo {
            endCursor hasNextPage hasPreviousPage startCursor 
          }
          nodes {
            ranking
            id
            so5Lineup {
              user {
                id
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
        "leaderBoardSlug": leader_board_slug
    }
    options = {
        "resultSelector": ["data","football","so5","so5Leaderboard","so5Rankings","nodes"],
        "pagination": {
            "targetNumber": number,
            "paginationVariable": "afterCursor",
            "cursorSelector": ["data","football","so5","so5Leaderboard","so5Rankings","pageInfo","endCursor"]
        }
    }
    result_list = client.request(body,variables,options)
    ranking_list = []
    for result in result_list:
        ranking_list.append(build_model_from_api_result(result))
    
    return ranking_list


def build_model_from_api_result(api_result) -> Ranking:
    #print(json.dumps(api_result,indent=2))   
    return Ranking(api_result.get("id"),api_result.get("so5Lineup").get("user").get("id"),api_result.get("ranking"))