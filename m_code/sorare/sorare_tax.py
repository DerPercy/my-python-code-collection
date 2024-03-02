from client import Client as SorareClient
from account_entry import get_account_entries
from context import myjinja2
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = SorareClient({
    'email': os.getenv('SORARE_EMAIL'),
    'password': os.getenv('SORARE_PASSWORD')
})


get_account_entries(client)

environment = myjinja2.get_environment()
template = environment.get_template("taxReport.jinja2")


taxEntries = {
        "fiscalYear": "2023",
        "ethPossessionStart": [],
        "nftPossessionStart": [],
        "ethPossessionEnd": [],
        "nftPossessionEnd": [],
        "costInEur": 1.23,
        "costInEurUI": "1,23 EUR",
        "sellGainInEur": 2.34,
        "sellGainInEurUI": "2,34 EUR",
        "profitWithinYear": 1,
        "profitWithinYearUI": "1 EUR",
        "profitGTYear": 2,
        "profitGTYearUI": "2.00 EUR",
        "details": []

    }
content = template.render(
    data = {
        "taxEntries": taxEntries
    }
)
with open("temp/sorare-tax-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)
