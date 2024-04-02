import os
from .client import Client
from .context import file_func
from icecream import ic


#from ..common.file_func import write_json_to_file

def get_cards_of_player(client:Client,player_slug:str,rarity:str,season:str = "ALL_SEASONS"):
    """
    season: 
    -   ALL_SEASONS or None     => all cards
    -   IN_SEASON               => just current season
    """
    if rarity in ["common"]:
        return []
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/cards/"+player_slug+"/"+rarity+"/"+season+".json"
    
    body="""
query getCardsOfPlayer($slug: String!, $rarities: [Rarity!], $endCursor: String ) { 
	player (slug:$slug) { 
		cards (rarities:$rarities, after:$endCursor, first: 200) { 
			nodes { slug inSeasonEligible notContractOwners { transferType price from priceInFiat { usd } } }
			pageInfo { endCursor hasNextPage hasPreviousPage startCursor }
		} 
	}
}
"""	
    variables = {
        "slug": player_slug,
        "rarities": [rarity]
    }
    options = {
        "resultSelector": ["data","player","cards","nodes"],
        "pagination": {
            "targetNumber": 100000,
            "paginationVariable": "endCursor",
            "cursorSelector": ["data","player","cards","pageInfo","endCursor"]
        }
    }
    result_list = client.request(body,variables,options)
    card_result_list = []
    transaction_list = []
    for card in result_list:
        #ic(card)
        if season == "IN_SEASON" and card.get("inSeasonEligible") == False:
            continue
        card_result_list.append(card)
        for transaction in card.get("notContractOwners",[]):
            if transaction.get("price","0") != "0":
                sale = {
					"datetime": transaction.get("from",None),
					"usd": transaction["priceInFiat"]["usd"]
				}
                transaction_list.append(sale)
    def get_datetime(elem):
        return elem.get("datetime")
    transaction_list.sort(key=get_datetime)
    #print(result_list)
    #print(transaction_list)
    cache = {
        "cards": card_result_list,
        "transactions": transaction_list
    }
    file_func.write_json_to_file(cache,cachefile)
    return transaction_list