from .client import Client
from .models.user import User

import json


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

