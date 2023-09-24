from .client import Client
#from ..common.file_func import write_json_to_file

def get_cards_of_player(client:Client,player_slug:str,rarity:str):
    cache = {}
    body="""
query getCardsOfPlayer($slug: String!, $rarities: [Rarity!], $endCursor: String ) { 
	player (slug:$slug) { 
		cards (rarities:$rarities, after:$endCursor, first: 200) { 
			nodes { slug notContractOwners { transferType price from priceInFiat { usd } } }
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
    transaction_list = []
    for card in result_list:
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
    return transaction_list