from client import Client

def get_rivals_game_result(client:Client, game_slug:str) -> dict:
    param = {}
    body_part_lineup="""
tactic { slug } 
score
appearances {
  pictureUrl
	player {
		slug
    displayName
		averageScore(type: LAST_FIFTEEN_SO5_AVERAGE_SCORE )
		activeClub {
      slug
    }
  }
	position
	score
    captain
}
"""
    body = """
query RivalsLastGames {
  football {
    rivals {
      game(slug:\"""" + game_slug + """\") {
        myArenaChallenge {
          awayContestant {
          	score
            manager {
              user {
                slug
              }
            }
            lineup {"""+body_part_lineup+"""}
          }
        }
        myLineup {"""+body_part_lineup+"""}
      }
    }
  }
}"""
    api_result = client.request(body,param,{ "resultSelector": ["data","football","rivals","game"]   })
    return api_result
