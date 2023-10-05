import os
from .client import Client
from .context import file_func


def determine_opponent_club(own_club_slug:str, game:dict):
    home = False
    if game.get("homeTeam").get("slug") == own_club_slug:
        home = True
        opponent = game.get("awayTeam").get("slug")
    else:
        home = False
        opponent = game.get("homeTeam").get("slug")
        
    return {
        "home": home,
        "opponent": opponent
    }
def get_club_details(client:Client, club_slug:str):
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/club/"+club_slug+".json"
    
    #"mechelen-mechelen-malines"
    body = """
query Team($slug: String!) {
  football {
    club(slug: $slug) {
      upcomingGames(first: 5) {
        competition {
          name
          slug
        }
        so5Fixture {
          gameWeek
          eventType
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
      }
    }
  }
}
"""
    variables = {
        "slug": club_slug
    }
    options = {
        "resultSelector": ["data","football","club"]
    }
    result = client.request(body,variables,options)
    file_func.write_json_to_file(result,cachefile)
    return result
