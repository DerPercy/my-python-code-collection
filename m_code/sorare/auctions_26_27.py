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
player_slugs = [
	# Heidenheim
	"frank-feller", 	# TW
	#"patrick-mainka", 	# Def


	# Dresden
	"alexander-rossipal", # Def
	"jonas-sterner", # Def
	"thomas-leon-keller", #  Def
	"ben-bobzien", # FW

	# Fürth
	"gian-luca-itter", #Def
	"krisztian-keresztes", #Def
	"paul-will", # MF
	"aaron-keller", #ST

	# Hertha
	"marton-dardai", #Def
	"julian-eitschberger", #Def

	# Tomble94Follows => 2.BL
	"tobias-muller",
	"ivan-nekic",
	"moritz-broni-kwarteng",
	"falko-michel",
	"hans-christian-bernat",
	"alessandro-adriano-crimaldi",
	"johan-gomez",
	"jacob-rasmussen",
	"tim-schreiber",
	"moritz-broschinski",
	"tim-siersleben",
	"michael-steinwender",
	"josip-brekalo",
	"robert-wagner",
	"samuele-di-benedetto",
	"jan-urbich",
	"jan-schoppner",
	"anselmo-garcia-mcnulty",
	"aleksandar-vukotic",
	"torben-musel",
	"ron-torben-hoffmann",
	"mathias-rasmussen",
	"kevin-ehlers",
	"daniel-mesenholer",
	"mergim-berisha",
	"herbert-bockhorn",
	"thomas-leon-keller",
	"mathias-honsak",
	"paul-seguin",
	"elias-bethke",
	"david-nemeth",
	"timo-horn",
	"marcel-hartel",
	"luka-mikael-hyrylainen",
	"mats-henry-pannewig",

	
				
]


client = Client({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

class PlayerAlreadyOwnedException(Exception):
    pass
class NotEnoughAuctionsException(Exception):
    pass

def get_running_auctions(client:Client):
	"""
	"""
	QUERY = '''
		query ActiveAuctions($endCursor: String){
  			tokens {
    			liveAuctions(sport: FOOTBALL after: $endCursor ){
      				totalCount
      				pageInfo {
        				endCursor
      				}
      				nodes{
        				id
        				endDate
        				minNextBid
        				currentPrice
        				anyCards {
          					slug
							anyPositions
							rarityTyped
          					anyPlayer {
            					slug
          					}
        				}
      				}
    			}
  			}
		}
		'''
	options = {
		   "resultSelector": ["data","tokens","liveAuctions","nodes"],  
		   "pagination": {
				"targetNumber": 50000,
				"paginationVariable": "endCursor",
				"cursorSelector": ["data","tokens","liveAuctions","pageInfo","endCursor"]
			}  
	}
	variables = {
			"before": ""
	}
	result = client.request(QUERY,variables,options)	
	#print( result )
	return result 

def get_minimum_auction_bet(client:Client,player_slug:str):
	"""
	Get the minimum price of the last 10 auctions of the player
	
	Returns: 
		{
			"minBid": int (EUR cents)
		}

	Raises:
        PlayerAlreadyOwnedException: The player was already bought.
        NotEnoughAuctionsException: There are not enough auctions to calculate the minimum bid.
	"""  
	

	QUERY = '''
	query LatestAuctionsOfPlayer($playerSlug: String!) {
	  anyPlayer(slug: $playerSlug) {
	    ownedCardsCount(rarity: limited) 
	    tokenPrices(rarity: limited seasonEligibility: IN_SEASON last: 80 includePrivateSales: false) {
	       nodes {
	        deal {
	          ... on TokenAuction {
	            bestBid {
	              amounts {
	                eurCents
	              }
	            }
	          }

	        }
	        date
	        card {
	          slug
	        }

	       }

	    }
	  }
	}
	'''
	resp = client.request(QUERY,variables={"playerSlug": player_slug})
	#print(resp)
	owned_cards = resp.get("data",{}).get("anyPlayer",{}).get("ownedCardsCount",-1)
	print(owned_cards)
	if owned_cards > 0:
		raise PlayerAlreadyOwnedException()
	best_bid_list = []
	for transaction in resp.get("data",{}).get("anyPlayer",{}).get("tokenPrices",{}).get("nodes",[]):
		bestBid = transaction.get("deal",{}).get("bestBid",{}).get("amounts",{}).get("eurCents",None)
		if bestBid != None:
			#print(bestBid)
			best_bid_list.append(bestBid)

	if len( best_bid_list ) < 10:
		raise NotEnoughAuctionsException()
	min_bid = min(best_bid_list[-10:])
	#print(best_bid_list)
	#print(best_bid_list[-10:])
	print(min_bid)
	#print(resp)

	return {
		"minBid": min_bid
	}

def get_player_slug_list_in_current_auctions(client:Client):
	"""
	
	"""
	QUERY = '''
	query MyRunningAuctions {
  		currentUser {
    		buyingTokenAuctions(sport: [FOOTBALL]) {
      			anyCards {
        			anyPlayer {
          				slug
        			}
      			}
    		}
  		}
	}
	'''
	resp = client.request(QUERY,variables={})
	slug_list = []
	#for auction in resp.get("data",{}).get("currentUser",{}).get("buyingTokenAuctions",[]):
	#	slug_list.append(auction.get("anyCards",{}).get("anyPlayer",{}).get("slug",""))
	
	return slug_list

def get_eur_wei_exchange_rate(client:Client):
	"""
		
	"""
	QUERY = '''
	query GetExchangeRate {
  		config {
    		exchangeRate {
      			id
      			rates
    		}
  		}
	}
	'''
	resp = client.request(QUERY,variables={})
	return resp.get("data").get("config").get("exchangeRate").get("rates").get("wei").get("eur")

def bid_on_auction(client:Client,bid:str,auction_id:str):
	# Running Node js script
	p = subprocess.Popen(['node', 'nodejs/bidAuction.js', 
						'--auctionId' , auction_id, #.split(":",1)[1], # remove 'EnglishAuction:' before id
						'--euramount' , bid,
						'--private-key', os.getenv('SORARE_STARKWARE_PRIVATE'),
						'--token', client.get_jwt(),
						'--jwt-aud', 'myPrivateApp'
					], stdout=subprocess.PIPE)
	out = p.stdout.read()
	print(out)

def get_position_price_modificator(positions:list[str]):
	print("Get modificator for:")
	[print(a) for a in positions]
	mod = 1
	if "Forward" in positions:
		mod = 1.000
	elif "Defender" in positions:
		mod = 1.000
	elif "Midfielder" in positions:
		mod = 1.040
	elif "Goalkeeper" in positions:
		mod = 1.040
	return mod

if len(sys.argv) == 3:
	bid_on_auction(client,sys.argv[1],sys.argv[2])
	exit()
#p = subprocess.Popen(['node', 'nodejs/bidAuction.js', '--auctionId' , 'a' ], stdout=subprocess.PIPE)
#out = p.stdout.read()
#print(out)


#get_running_auctions(
#	client=client
#)
player_bids = {}
for player_slug in player_slugs:
	print("Processing:"+player_slug)
	try:
		bid_data = get_minimum_auction_bet(client=client, player_slug=player_slug)
		player_bids[player_slug] = bid_data
	except NotEnoughAuctionsException:
		print("Not enough auctions for this player to determine price")
		continue
	except PlayerAlreadyOwnedException:
		print("Player already owned")
		continue
#print(player_bids)
# Check in current open auctions, if a bid on this player is active already
for auction_slug in get_player_slug_list_in_current_auctions(client=client):
	print(auction_slug + " in current auctions found. Remove entry")
	player_bids.__delitem__(auction_slug)
print(player_bids)
if len(player_bids) > 0:
	exch_rate = get_eur_wei_exchange_rate(client=client)

	for auction  in get_running_auctions( client=client ):
		cards = auction.get("anyCards",[])
		if len(cards) == 1:
			if cards[0].get("rarityTyped","limited") != "limited":
				continue

			player_slug = cards[0].get("anyPlayer",{}).get("slug","")
			if player_bids.get(player_slug,None) != None:
				#bid = int(( player_bids.get(player_slug).get('minBid',0) * 0.73 / 100 ) / exch_rate)
				bid = int(( player_bids.get(player_slug).get('minBid',0) * 0.7727 * get_position_price_modificator(cards[0].get("anyPositions",[]))) )
				auction_id = auction.get("id","???")
				print("Bid "+str(bid)+" on auction "+ auction_id + " for player " + player_slug )
				bid_on_auction(client=client, bid=str(bid), auction_id=auction_id)

