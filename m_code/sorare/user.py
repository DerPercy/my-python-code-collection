from .client import Client
from .models.user import User

import json


def get_player_slugs_of_current_user(client:Client):
    body = """
query UserQuery($endCursor: String) {
  currentUser {
    paginatedCards(rarities: [ limited ] after:$endCursor ) {
        nodes {
            player {
                slug
            }
        }
        pageInfo {
            endCursor hasNextPage hasPreviousPage startCursor  
        }
    
    }
  }
}

"""
    options = {
        "resultSelector": ["data","currentUser","paginatedCards","nodes"],
        "pagination": {
            "targetNumber": 100000,
            "paginationVariable": "endCursor",
            "cursorSelector": ["data","currentUser","paginatedCards","pageInfo","endCursor"]
        }
    }
    result = client.request(body,{},options)
    slug_list = []
    for card in result:
        slug_list.append(card.get("player").get("slug"))
    #print(result)
    #print(len(result))
    return slug_list


def get_user_from_user_id(client:Client,  user_id:str) -> User:
    #print(user_id)
    if user_id.startswith("User:"):
        user_id = user_id[5:]
    #print(user_id)
    body = """
query UserQuery($userID: String!) {
  userById( id: $userID) {
    id
    nickname
  }
}
"""
    variables = {
        "userID": user_id
    }
    options = {
        "resultSelector": ["data","userById"],
    }
    result = client.request(body,variables,options)
    #print(result)
    return User(result.get("id"),result.get("nickname"))

