from .client import Client
from .cards import get_cards_of_player
from .context import file_func
#from..common.file_func import write_json_to_file, read_json_from_file
import logging
import json
import os
import urllib
import time

def get_player_pos_value(player):
    #logging.error(player)
    ret_value = -1
    if player.get("position",None) == None:
        logging.error("Player has no known position")
        ret_value = -1
    
    if player.get("position") == "Forward":
        return 4
    if player.get("position") == "Midfielder":
        return 3
    if player.get("position") == "Defender":
        return 2
    if player.get("position") == "Goalkeeper":
        return 1
    else:
        logging.error("Position "+player.get("position","")+" unknown")
        return 5
    return ret_value     

def calc_captain_bonus(options):
    score = options.get("score")
    player_score_sum = 0
    for player in options.get("player",[]):
        player_score = player.get("score",0)
        if player_score != None:
            player_score_sum = player_score_sum + player_score
    score_diff = score - player_score_sum
    if score_diff < 0:
        logging.error("player have more points than the total")
        logging.error(score_diff)
    elif score_diff > 0:
        #logging.warn(score)
        #logging.warn("vs")    
        #logging.warn(player_score_sum)
        captain_found = False
        for player in options.get("player",[]):
            if player.get("isCaptain",False) == True:
                captain_found = True
                player["originalScore"] = player.get("score")
                if player.get("score") != None:
                    player["score"] = player.get("score") + score_diff
                
        if captain_found == False:
            logging.error("Score diff, but no captain in lineup")
            logging.error(score_diff)
    


def get_leaderboard_data(client:Client,leader_board_slug:str, ranking_filter:callable = None, ranking_sorter:callable = None):
    # Get leaderboard data
    param = {
		"leaderboardSlug": leader_board_slug
	}
    body = """
query getRankingForLeaderboard($leaderboardSlug: String!, $endCursor: String) { 
	football { 
		so5 { 	
			so5Leaderboard(slug:$leaderboardSlug){ 
				rules {
					captain
				} 
				displayName svgLogoUrl mainRarityType
				so5Rankings(first:100,after:$endCursor,){ 
					nodes { 
                        ranking
                        eligibleForReward
                        eligibleRewards {
                            usdAmount
                            cards {
                                player {
                                    slug
                                }
                                quantity
                                quality
                                rarity
                            }
                        }
						score 
						so5Lineup { 
							user { 
								nickname 
								id 
							} 
							so5Appearances { 
								captain 
								card { 
									pictureUrl
                                    positionTyped 
                                    rarity
                                    player {
                                        slug
                                    }
								} 
								cleanScore 
								bonus 
								so5Score { 
									position 
								} 
								game { 
									homeTeam { 
										__typename ... on Club { 
											name 
											pictureUrl 
										} 
										__typename ... on NationalTeam { 
											name 
											pictureUrl 
										} 
									} 
									homeGoals 
									awayTeam { 
										... on Club { 
											name 
											pictureUrl 
										} 
										... on NationalTeam { 
											name 
											pictureUrl 
										} 
									} 
									awayGoals 
								} 
							} 
						} 
					} 
                    pageInfo {
                        endCursor hasNextPage hasPreviousPage startCursor  
                    } 
				} 
			} 
		} 
	} 
}
"""
    #leaderBoardResult = json.loads(context["rootHandler"].external().getRequestHandler().request("sorareHeroesGetRankings",param))
    leaderBoard = client.request(body,param,{ "resultSelector": ["data","football","so5","so5Leaderboard"]   })
    #if leader_board_slug == "22-26-sep-2023-global-cap-division-11":
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/leaderBoards/"+leader_board_slug+".json"    
    file_func.write_json_to_file(leaderBoard,cachefile)
    
    # Get rankings
    lineup_list = client.request(body,param,{ 
        "resultSelector": ["data","football","so5","so5Leaderboard","so5Rankings","nodes"],
        "pagination": {
            "targetNumber": 1,
            "paginationVariable": "endCursor",
            "cursorSelector": ["data","football","so5","so5Leaderboard","so5Rankings","pageInfo","endCursor"],
            "resultFilter": ranking_filter
        }
         
    })
    #print("Lineup length")
    #print(len(lineup_list))
   
    #lineup = leaderBoard.get("so5Rankings",{}).get("nodes",{})[0]
    logging.info(str(len(lineup_list))+" relevant lineups found")
    if ranking_sorter != None:
        #print("Sort")
        logging.info("Sort lineups")
        lineup_list.sort(key=ranking_sorter)
        logging.info("Sorting finished")

    return {
        "leaderBoard": leaderBoard,
        "rankings": lineup_list
    }

def create_leaderboard_image(client:Client,leader_board_slug:str, ranking_filter:callable = None, ranking_sorter:callable = None):
    print(leader_board_slug)
    # leaderboardSlug: 11-15-aug-2023-champion-asia-division-5
    leader_board_data = get_leaderboard_data(client,leader_board_slug,ranking_filter,ranking_sorter)
    leaderBoard = leader_board_data.get("leaderBoard")
    lineup_list = leader_board_data.get("rankings")
    

    #print("Captain:")
        
    #print("=========")
    rarity = leaderBoard.get("mainRarityType","unknown")
    if rarity == "limited":
        color = "#EDCC42"
        textColor = "#FFFFFF"        
    elif rarity == "rare":
        color = "#A61429"
        textColor = "#FFFFFF"        
    elif rarity == "super_rare":
        color = "#4780D4"
        textColor = "#FFFFFF"        
    elif rarity == "unique":
        color = "#545454"
        textColor = "#FFFFFF"        
    else:
        color = "#FFFFFF"
        textColor = "#000000"        
        
    options = {
        "bgColor": color,
        "textColor": textColor
    }
    folder = "sorarefiles/"+leaderBoard.get("mainRarityType","unknown")+"/"+leader_board_slug
    options["resultFilename"] = "results/"+folder+".png"
    #os.makedirs(folder)
    folder = folder + "/"

    #print(json.dumps(leaderBoard,indent=2))
    options["leagueName"] = leaderBoard.get("displayName","???")
    download_file(leaderBoard.get("svgLogoUrl"),folder+"league_logo.svg")
    options["leagueLogo"] = folder+"league_logo.svg"
    # get 1st place
        
    # Todo: Check if list has at least 1 item
    lineup = lineup_list[0]

    #print(lineup)
    #time.sleep(60)
    options["score"] = lineup.get("score","???")
    options["place"] = "#"+str(lineup.get("ranking"))
    lineup = lineup.get("so5Lineup",{})
    options["userName"] = lineup.get("user",{}).get("nickname","???")
    #options["place"] = "1st"
    #print(json.dumps(lineup,indent=2))

    count = 0
    player_array = []
    for card in lineup.get("so5Appearances",[]):
        #logging.error(card)
        player = {}
        card_filename = "player_"+str(count)+".png"

        if download_file(card.get("card",{}).get("pictureUrl"),folder+card_filename):
            player["cardFilename"] = folder+card_filename
        player["isCaptain"] = card.get("captain")
        player["playerSlug"] = card.get("card",{}).get("player",{}).get("slug")
        player["rarity"] = card.get("card",{}).get("rarity")
        
        player["score"] = card.get("cleanScore",0)
        if player["score"] == None:
            player["score"] = 0
        # Game info 
        game_exists = True
        try:
            if card.get("game",{}).get("homeTeam",{}).get("pictureUrl","") == "":
                home_team_filename = ""
            else:
                home_team_filename = folder+"home_team_"+str(count)+".png"
                   
                if not download_file(card.get("game",{}).get("homeTeam",{}).get("pictureUrl"),home_team_filename):
                    home_team_filename = ""        
        except:
            home_team_filename = ""
            game_exists = False

        try:
            if card.get("game",{}).get("awayTeam",{}).get("pictureUrl") == "":
                away_team_filename = ""
            else:
                away_team_filename = folder+"away_team_"+str(count)+".png"
                if not download_file(card.get("game",{}).get("awayTeam",{}).get("pictureUrl"),away_team_filename):
                    away_team_filename = ""        
        except:
            away_team_filename = ""
            game_exists = False

        if game_exists == True:
            player["game"] = {
                "homeTeamLogo": home_team_filename,
                "awayTeamLogo": away_team_filename,
            }
            try:
                player["game"]["homeGoals"] = card.get("game",{}).get("homeGoals",{})
                player["game"]["awayGoals"] = card.get("game",{}).get("awayGoals",{})
            except:
                pass


        try:
            player["position"] = card.get("so5Score",{}).get("position")
        except:
            player["position"] = card.get("card",{}).get("positionTyped")
            pass

        count += 1
        player_array.append(player)

    player_array = sorted(player_array, key=get_player_pos_value)
    
    options["player"] = player_array
    
    calc_captain_bonus(options)
    #print(options)
    #print(json.dumps(options, indent= 2))
    return options
    
    #createImage(options)



def download_file(url:str, filename: str):
    if os.path.isfile(filename):
        logging.info("File already exists. Skip\r")
        return True
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent','Mozilla/5.0')]
    urllib.request.install_opener(opener)
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        pass
    try:
        logging.info("Load image...")
        urllib.request.urlretrieve(url,filename)
        logging.info("done")
        return True
    except:
        return False


def get_price_of_player(client:Client, player_slug:str,rarity:str, price_date: str):
    print("Get price of "+player_slug,end='\r')
    cachefile = os.path.dirname(os.path.abspath(__file__))+"/../../temp/sorare/cache/price/"+player_slug+".json"
    price_cache = file_func.read_json_from_file(cachefile)
    #logging.info(price_cache)
    if price_cache.get(rarity,{}).get(price_date,{}).get("avg",None) != None:
        return price_cache.get(rarity,{}).get(price_date,{}).get("avg",None)
    price_list = get_cards_of_player(client,player_slug,rarity)
    #logging.info(len(price_list))
    price_list_dt = []
    for price in price_list:
        if price["datetime"] < price_date:
            price_list_dt.append(price) 
    #logging.info(len(price_list_dt))
    last_five = price_list_dt[-5:]
    #logging.info(last_five)
    if len(last_five) == 0:
        return None
    else:
        sum = 0
        for price in last_five:
            sum = sum + price["usd"]
    avg = sum / len(last_five)
    #logging.info(avg)
    #if price_cache.get(player_slug,None) == None:
    #    price_cache[player_slug] = {}
    if price_cache.get(rarity,None) == None:
        price_cache[rarity] = {}        
    price_cache[rarity][price_date] = {
        "last_five": last_five,
        "avg": avg
    } 
    file_func.write_json_to_file(price_cache,cachefile)

    return avg