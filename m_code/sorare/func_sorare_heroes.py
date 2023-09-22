from .client import Client
import logging
import json
import os
import urllib

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
        logging.error("Position "+player.get("position")+" unknown")
    return ret_value     

def calc_captain_bonus(options):
    score = options.get("score")
    player_score_sum = 0
    for player in options.get("player",[]):
        player_score = player.get("score")
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
                player["score"] = player.get("score") + score_diff
        if captain_found == False:
            logging.error("Score diff, but no captain in lineup")
            logging.error(score_diff)
    
    
       

def create_leaderboard_image(client:Client,leader_board_slug:str):

    # leaderboardSlug: 11-15-aug-2023-champion-asia-division-5
    param = {
		"leaderboardSlug": leader_board_slug
	}
    body = """
query getRankingForLeaderboard($leaderboardSlug: String!) { 
	football { 
		so5 { 	
			so5Leaderboard(slug:$leaderboardSlug){ 
				rules {
					captain
				} 
				displayName svgLogoUrl mainRarityType
				so5Rankings(first:1){ 
					nodes { 
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
				} 
			} 
		} 
	} 
}
"""
    #leaderBoardResult = json.loads(context["rootHandler"].external().getRequestHandler().request("sorareHeroesGetRankings",param))
    leaderBoard = client.request(body,param,{ "resultSelector": ["data","football","so5","so5Leaderboard"]   })
    #leaderBoardResult.get("data",{}).get("football",{}).get("so5",{}).get("so5Leaderboard",{})
    
    #print("Captain:")
    #print(json.dumps(leaderBoard,indent=2))
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
    lineup = leaderBoard.get("so5Rankings",{}).get("nodes",{})[0]
    options["score"] = lineup.get("score","???")
    lineup = lineup.get("so5Lineup",{})
    options["userName"] = lineup.get("user",{}).get("nickname","???")
    options["place"] = "1st"
    #print(json.dumps(lineup,indent=2))

    count = 0
    player_array = []
    for card in lineup.get("so5Appearances",[]):
        #logging.error(card)
        player = {}
        card_filename = "player_"+str(count)+".png"

        download_file(card.get("card",{}).get("pictureUrl"),folder+card_filename)
        player["cardFilename"] = folder+card_filename
        player["isCaptain"] = card.get("captain")
        player["playerSlug"] = card.get("card",{}).get("player",{}).get("slug")
        player["rarity"] = card.get("card",{}).get("rarity")
        
        player["score"] = card.get("cleanScore",0)
        # Game info 
        if card.get("game",{}).get("homeTeam",{}).get("pictureUrl") == "":
            home_team_filename = ""
        else:
            home_team_filename = folder+"home_team_"+str(count)+".png"   
            download_file(card.get("game",{}).get("homeTeam",{}).get("pictureUrl"),home_team_filename)
         
        if card.get("game",{}).get("awayTeam",{}).get("pictureUrl") == "":
            away_team_filename = ""
        else:
            away_team_filename = folder+"away_team_"+str(count)+".png"
            download_file(card.get("game",{}).get("awayTeam",{}).get("pictureUrl"),away_team_filename)
        
        player["game"] = {
            "homeTeamLogo": home_team_filename,
            "awayTeamLogo": away_team_filename,
            "homeGoals": card.get("game",{}).get("homeGoals",{}),
            "awayGoals": card.get("game",{}).get("awayGoals",{}),
            
        }

        player["position"] = card.get("so5Score",{}).get("position")
        
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
        print("File already exists. Skip")
        return
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent','Mozilla/5.0')]
    urllib.request.install_opener(opener)
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        error = 1
    print("Load image...")
    urllib.request.urlretrieve(url,filename)
    print("done")
    pass
    