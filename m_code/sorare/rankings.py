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
    result= client.request(body,variables,options)
    print(len(result))
    pass