from client import Client
from models.transaction import Transaction

def get_current_user_slug(client:Client) -> str:
    options = {
    }
    variables = {
    }
    body = """
query CurrentUserQuery { 
    currentUser { slug email id  }
}
"""
    result = client.request(body,variables,options)
    #print(result)
    return result.get("data").get("currentUser").get("slug")

def get_account_entries(client:Client) -> list[Transaction]:
    options = {
       "resultSelector": ["data","currentUser","accountEntries","nodes"],  
       "pagination": {
            "targetNumber": 1000000,
            "paginationVariable": "endCursor",
            "cursorSelector": ["data","currentUser","accountEntries","pageInfo","endCursor"]
        }  
    }
    variables = {
        "before": ""
    }
    body = """
query CurrentUserQuery($endCursor: String ) { 
    currentUser { slug email id accountEntries(first:100, after:$endCursor) { pageInfo { hasNextPage hasPreviousPage endCursor startCursor  } nodes { 
                amount amountInFiat { eur }
				entryType date id provisional 
                tokenOperation { __typename 
                    ... on TokenMonetaryReward {
                        amounts {
                            referenceCurrency
                        }
                    }
                    ... on TokenOffer { id 
                        sender { __typename ... on User { slug } } 
                        receiver { __typename ... on User { slug } }
                        senderSide { cards { __typename 
                            ...on Card {
                                name id slug rarity
                            } 
                        } } 
                        receiverSide { cards { __typename 
                            ...on Card {
                                name id slug rarity
                            } 
                        } }  
                    }
                    ... on TokenBid { auction { cards { __typename 
                            ...on Card {
                                name id slug rarity
                            } 
                    } } }
                }
    } } }
}
"""
    result = client.request(body,variables,options)
    result.reverse()
    current_user = get_current_user_slug(client)
    transaction_list = []
    for transaction in result:
        transaction_list.append(Transaction(payload=transaction,current_user_slug=current_user).process_payload())
        
    
    #print(transaction_list)
    return transaction_list
