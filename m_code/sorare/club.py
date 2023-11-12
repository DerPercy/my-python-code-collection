import os
from .client import Client
from .context import file_func
from .fixture import get_current_open_gameweek


def get_club_slugs_playing_next_gw(client:Client,opts:dict = {}) -> list[str]:
    """
    List of club slugs which have a game in the next gameweek
    """
    gw = get_current_open_gameweek(client)
    body = """
query Clubs {
  football {
    clubsReady {
      slug
      domesticLeague {
        slug
      }
      upcomingGames(first:1) {
        so5Fixture {
          gameWeek
        }
      }
    }
  }
}
"""
    options = {
        "resultSelector": ["data","football","clubsReady"]
    }
    result = client.request(body,{},options)
    club_slug_list = []
    for club in result:
        if opts.get("filter",{}).get("includeLeagues",None) != None:
            if club.get("domesticLeague") == None:
                continue
            if club.get("domesticLeague",{}).get("slug","") not in opts.get("filter",{}).get("includeLeagues",[]):
                continue
        if len(club.get("upcomingGames")) == 0:
            continue
        if club.get("upcomingGames")[0].get("so5Fixture") == None:
            continue
        if club.get("upcomingGames")[0].get("so5Fixture").get("gameWeek") == gw:
            #print(club.get("domesticLeague").get("slug"))
        
            club_slug_list.append(club.get("slug"))
    return club_slug_list


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
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/club/"+club_slug+"/details.json"
    
    #"mechelen-mechelen-malines"
    body = """
query Team($slug: String!) {
  football {
    club(slug: $slug) {
      domesticLeague {
        slug
      }
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


def get_player_slugs_of_club_slug(client:Client, club_slug:str):
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/club/"+club_slug+"/player.json"
    
    body = """
query Team($slug: String!,$afterCursor: String) {
  football {
    club(slug: $slug) {
      activePlayers(first:100 after: $afterCursor) {
        nodes {
          activeClub {
            slug
          }
          age
          position
          slug
        }
        pageInfo {
            endCursor hasNextPage hasPreviousPage startCursor  
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
        "resultSelector": ["data","football","club","activePlayers","nodes"],
        "pagination": {
            "targetNumber": 1000,
            "paginationVariable": "afterCursor",
            "cursorSelector": ["data","football","club","activePlayers","pageInfo","endCursor"]
        }
    }
    result = client.request(body,variables,options)
    player_slug_list = []
    for player_dict in result:
        if player_dict.get("activeClub",None)!= None:
            if player_dict.get("activeClub",{}).get("slug") == club_slug:
                player_slug_list.append(player_dict.get("slug",None))
    file_func.write_json_to_file(result,cachefile)
    return player_slug_list
