from typing import List, Dict, Any, Optional
import os
import sys
import time
import json
import subprocess

from client import Client

import requests
from dotenv import load_dotenv


load_dotenv()

client = Client({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})


def get_my_cards(client:Client):
    QUERY = '''
        query MyCardsPrices($endCursor: String) {
            currentUser {
                cards(rarities: [limited] after: $endCursor ) {
                    pageInfo{
                        endCursor
                    }
                    nodes {
                        slug
                        anyPlayer {
                            slug
                        }
                        ownershipHistory {
                            user {
                                slug
                            }
                            amounts {
                                eurCents
                            }
                        }
                    }
                }
            }
        }

    '''
    options = {
        "resultSelector": ["data","currentUser","cards","nodes"],  
        "pagination": {
            "targetNumber": 50000,
            "paginationVariable": "endCursor",
            "cursorSelector": ["data","currentUser","cards","pageInfo","endCursor"]
        }  
    }
    variables = {
        "before": ""
    }
    result = client.request(QUERY,variables,options)	
    cards = []
    for card in result:
        price_in_cents = 0
        for owner in card["ownershipHistory"]:
            if owner["user"]["slug"] == "lizsummer":
                try:
                    price_in_cents = owner.get("amounts",{}).get("eurCents",0)
                except Exception:
                    price_in_cents = 0
        cards.append({
            "slug": card["slug"],
            "priceInCents": price_in_cents ,
            "playerSlug": card["anyPlayer"]["slug"],
        })
    #print(cards)
    return cards 

cards = get_my_cards(client)
for card in cards:
    print(card["slug"]+":"+str(card["priceInCents"])+" ("+card["playerSlug"]+")")