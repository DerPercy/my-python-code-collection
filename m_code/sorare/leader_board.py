from .client import Client
from .models.leader_board import LeaderBoard

import json

def get_leader_boards_of_fixture_slug(client:Client,fixture_slug:str) -> list[LeaderBoard]:
    leader_boards = []
    result= client.request("""
query LeaderBoardsQuery($slug: String!) {
    football { so5 { so5Fixture(slug: $slug) {  
        so5Leaderboards {
		    slug rarityType seasonality 
	    }
    } } }
}
""",{"slug": fixture_slug})
    for leader_board_data in result.get("data",{}).get("football",{}).get("so5",{}).get("so5Fixture",{}).get("so5Leaderboards",[]):
        leader_boards.append(build_model_from_api_result(leader_board_data))
    return leader_boards

def build_model_from_api_result(api_result) -> LeaderBoard:
    #print(json.dumps(api_result,indent=2))   
    return LeaderBoard(api_result.get("slug"),api_result.get("rarityType"),seasonality=api_result.get("seasonality"))