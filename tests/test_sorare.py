import os
from .context import sorare
from .context import sorare_func_sorare_heroes
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


load_dotenv()

def test_sorare_prices():
    logging.error("Hallo")
    
    client = sorare.client.Client({
        'email': os.getenv('SORARE_EMAIL'),
        'password': os.getenv('SORARE_PASSWORD')
    })

    price = sorare_func_sorare_heroes.get_price_of_player(client, "juan-camilo-hernandez-suarez","limited", "2022-09-01T14:00:00Z")
    #price = sorare_func_sorare_heroes.get_price_of_player(client, "walter-daniel-benitez","limited", "2022-09-01T14:00:00Z")
    print(str(price))
    assert None == None