from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2, CoinStackHandler,AssetHandler, file_func
from models.tax_entry import TaxEntry
import logging
import os
from dotenv import load_dotenv
from icecream import ic
from datetime import datetime

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

fiscal_year = 2023


transactions = get_account_entries(client)

trans_json = []
for trans in transactions:
    trans_json.append(trans.payload)
fy_tax_entries = []
eth_coinstack = CoinStackHandler()
nft_assets = AssetHandler()

# Prefill assets, which are not in transcations anymore (bought by creditcard)



nft_assets.add_asset(datetime(2021,9,25),"jonathan-ramon-maidana-2021-limited-65",2.46)
nft_assets.add_asset(datetime(2021,9,25),"jordi-jose-delem-2021-limited-64",2.46)
nft_assets.add_asset(datetime(2021,9,25),"juan-agudelo-2021-limited-64",2.50)
nft_assets.add_asset(datetime(2021,9,25),"katsunori-ueebisu-2021-limited-64",2.50)


nft_assets.add_asset(datetime(2021,9,26),"haruhiko-takimoto-2021-limited-3",4.77)
#nft_assets.add_asset(datetime(2021,10,2),"noah-fadiga-2021-limited-86",14.21)
#nft_assets.add_asset(datetime(2021,10,2),"csaba-bukta-2021-limited-84",21.62)
#nft_assets.add_asset(datetime(2021,10,6),"richie-laryea-2021-limited-93",11.96)
#nft_assets.add_asset(datetime(2021,10,6),"ivan-marquez-alvarez-2021-limited-89",11.94)
#nft_assets.add_asset(datetime(2021,10,7),"vyacheslav-grulev-2021-limited-86",12.21)
#nft_assets.add_asset(datetime(2021,10,7),"aaron-herrera-2021-limited-88",9.13)
#nft_assets.add_asset(datetime(2021,10,11),"tiago-emanuel-embalo-djalo-2021-limited-100",16.94)
#nft_assets.add_asset(datetime(2021,10,12),"lukas-malicsek-2021-limited-109",16.49)
#nft_assets.add_asset(datetime(2021,10,17),"braian-ezequiel-romero-2021-limited-96",21.55)
#nft_assets.add_asset(datetime(2021,10,17),"baptiste-santamaria-2021-limited-106",21.55)
#nft_assets.add_asset(datetime(2021,10,19),"dae-won-kim-2021-limited-106",29.71)
#nft_assets.add_asset(datetime(2021,10,19),"jair-rodrigues-junior-2021-limited-128",20.86)
#nft_assets.add_asset(datetime(2021,10,20),"thiago-santos-santana-2021-limited-108",33.98)
#nft_assets.add_asset(datetime(2021,10,20),"cristian-portugues-manzanera-2021-limited-122",38.85)
nft_assets.add_asset(datetime(2021,10,20),"patrick-pentz-2021-limited-81",158.23)
nft_assets.add_asset(datetime(2021,10,20),"marco-djuricin-2021-limited-112",47.68)
nft_assets.add_asset(datetime(2021,10,23),"stefan-frei-2021-limited-110",115.82)
nft_assets.add_asset(datetime(2021,10,27),"yoon-ho-kwak-2021-rare-2",99.56)


#nft_assets.add_asset(datetime(2021,10,24),"kelyn-rowe-2021-limited-99",7.04)
#nft_assets.add_asset(datetime(2021,11,7),"sang-hyub-lim-2021-rare-77",110.44)
#nft_assets.add_asset(datetime(2021,11,18),"chi-in-jung-2021-rare-38",107.83)


 

















eth_possession_start = None
eth_possession_end = None
for transaction in transactions:
    tax_entry = TaxEntry("???")
    if transaction.in_fiscal_year(fiscal_year):
        if eth_possession_start == None:
            eth_possession_start = eth_coinstack.getContent()
    # Handle Coinstack gains
    coinstack_result = transaction.fill_coinstackhandler( eth_coinstack )
    if not transaction.fill_assethandler( nft_assets ):
        break
    if coinstack_result != None:
        tax_entry.eth_result = coinstack_result

    if transaction.in_fiscal_year(fiscal_year):
        fy_tax_entries.append(tax_entry.calculate())
        eth_possession_end = eth_coinstack.getContent()

environment = myjinja2.get_environment()
template = environment.get_template("taxReport.jinja2")


taxEntries = {
        "fiscalYear": fiscal_year,
        "ethPossessionStart": eth_possession_start,
        "nftPossessionStart": [],
        "ethPossessionEnd": eth_possession_end,
        "nftPossessionEnd": [],
        "costInEur": 1.23,
        "costInEurUI": "1,23 EUR",
        "sellGainInEur": 2.34,
        "sellGainInEurUI": "2,34 EUR",
        "profitWithinYear": 1,
        "profitWithinYearUI": "1 EUR",
        "profitGTYear": 2,
        "profitGTYearUI": "2.00 EUR",
        "details": fy_tax_entries

    }
content = template.render(
    data = {
        "taxEntries": taxEntries
    }
)
with open("temp/sorare-tax-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)

ic(nft_assets.get_content().get("lines"))
