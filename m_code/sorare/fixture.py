from .client import Client

gw_cache = {}
after_cursor = ""


def get_fixture_slug_of_gameweek(client:Client,gw:int) -> str:
    global after_cursor
    print("Get gameweek"+str(gw))
    gw_str = str(gw)
    if gw_cache.get(gw_str) != None:
        return gw_cache.get(gw_str)
    fixture_found = None
    #print("get_fixture_slug_of_gameweek needs to be implemented")
    options = {
        "resultSelector": ["data","football","so5","so5Fixtures"],    
    }
    result= client.request("""
query FixturesQuery($afterCursor: String) {
    football { so5 { so5Fixtures(first:50 after: $afterCursor) {  
        nodes {
		    slug aasmState canCompose eventType gameWeek
	    }
        pageInfo {
            endCursor hasNextPage hasPreviousPage startCursor  
        } 
    } } }
}
""",{"afterCursor": after_cursor},options)
    after_cursor = result.get("pageInfo").get("endCursor")
    for fixture in result.get("nodes"):
        print("Gameweek found"+str(fixture.get("gameWeek")))
        if fixture.get("gameWeek") == gw:
            fixture_found = fixture.get("slug")
        gw_cache[str(fixture.get("gameWeek"))] = fixture.get("slug")
    
    if fixture_found != None:
        return fixture_found
    
    return get_fixture_slug_of_gameweek(client,gw)


# after: endCursor
#client.request("""
#query FixturesQuery($afterCursor: String) {
#    football { so5 { so5Fixtures(first:50 after: $afterCursor) {  
#        nodes {
#		    slug aasmState canCompose eventType gameWeek
#	    }
#        pageInfo {
#            endCursor hasNextPage hasPreviousPage startCursor  
#        } 
#    } } }
#}
#""")
