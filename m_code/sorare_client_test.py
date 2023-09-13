from sorare import Client as SorareClient
from sorare.fixture import get_fixture_slug_of_gameweek

import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


print(os.getenv('SORARE_EMAIL'))
print(os.getenv('SORARE_PASSWORD'))

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

# after: endCursor
client.request("""
query FixturesQuery {
    so5 { so5Fixtures(first:50 after:"WyIyMDIzLTAzLTIxIDE1OjAwOjAwLjAwMDAwMDAwMCBVVEMiLCI0M2ViY2Q0OC00MTU1LTRiMmMtYjZmMi1lMWE4NDUzMGY3ZGMiXQ") {  
        nodes {
		    slug aasmState canCompose eventType gameWeek
	    }
        pageInfo {
            endCursor hasNextPage hasPreviousPage startCursor  
        } 
    } }
}
""")
               
game_weeks = list(range(301,401))
for game_week in game_weeks:
    fixture_slug = get_fixture_slug_of_gameweek(client,game_week)
    print(game_week)
