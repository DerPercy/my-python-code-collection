from .client import Client
def get_fixture_slug_of_gameweek(client:Client,gw:int) -> str:
    print("get_fixture_slug_of_gameweek needs to be implemented")
    return "1-5-sep-2023"


# after: endCursor
#client.request("""
#query FixturesQuery {
#    so5 { so5Fixtures(first:50 after:"WyIyMDIzLTAzLTIxIDE1OjAwOjAwLjAwMDAwMDAwMCBVVEMiLCI0M2ViY2Q0OC00MTU1LTRiMmMtYjZmMi1lMWE4NDUzMGY3ZGMiXQ") {  
#        nodes {
#		    slug aasmState canCompose eventType gameWeek
#	    }
#        pageInfo {
#            endCursor hasNextPage hasPreviousPage startCursor  
#        } 
#    } }
#}
#""")
