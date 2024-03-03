from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2, CoinStackHandler,AssetHandler
from models.tax_entry import TaxEntry
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})

fiscal_year = 2023


transactions = get_account_entries(client)
fy_tax_entries = []
eth_coinstack = CoinStackHandler()
nft_assets = AssetHandler()
eth_possession_start = None
eth_possession_end = None
for transaction in transactions:
    tax_entry = TaxEntry("???")
    if transaction.in_fiscal_year(fiscal_year):
        if eth_possession_start == None:
            eth_possession_start = eth_coinstack.getContent()
    # Handle Coinstack gains
    coinstack_result = transaction.fill_coinstackhandler( eth_coinstack )
    transaction.fill_assethandler( nft_assets )
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
