import csv
import logging
import re
import copy

from datetime import datetime, timedelta
from handler.Coinstack import CoinStackHandler
from handler.transaction_history import TransactionHistory
from models.transaction import Transaction
from jinja2 import Environment, FileSystemLoader

from context import myjinja2 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Customizing part
fiscalYear = 2023

transaction_history = TransactionHistory()

def getDatetime(dateString):
	return datetime.fromisoformat(dateString.replace("Z","+00:00")) + timedelta(hours=1)

def processCSVRow(row):
    global fiscalYear
    timestamp = row[0]
    action = row[1]
    symbol = row[2]
    quantity = float(row[3])
    rate = float(row[5])
    if row[6] == "":
        eurWoFees = 0 
    else:
        eurWoFees = float(row[6])
    if row[8] == "":
        fees = float(0)
    else:
        fees = float(row[8])
    transactionDescription = row[9]

    try:
        if action == 'Buy' or action == 'Receive' or action == 'Advanced Trade Buy': # Buy/Receive coins in coinbase
            transaction_history.action_buy(
                dt          =   getDatetime(timestamp),
                symbol      =   symbol,
                quantity    =   quantity,
                rate        =   rate,
                fees_in_fiat=   fees
            )
        elif action == 'Learning Reward' or action == 'Rewards Income': # Learing rewards
            transaction_history.action_rewards(
                dt          =   getDatetime(timestamp),
                symbol      =   symbol,
                quantity    =   quantity,
                rate        =   rate,
                fees_in_fiat=   fees,
                is_staking  =(action == 'Rewards Income')
            )
        elif action == "Send" or action == 'Sell' or action == 'Advanced Trade Sell': # Send/Sell coins in coinbase
            transaction_history.action_sell(
                dt          =   getDatetime(timestamp),
                symbol      =   symbol,
                quantity    =   quantity,
                rate        =   rate,
                fees_in_fiat=   fees
            )
        elif action == "Convert": # Convert one Coin to another
            result = re.search(r"Converted ([\d.,]*) ([^\s]*) to ([\d.,]*) ([^\s]*)", transactionDescription)
            sec_symbol = result.group(4)
            sec_quantity = float(result.group(3).replace(",", "."))
            sec_rate = eurWoFees / sec_quantity
            transaction_history.action_convert(
                dt=getDatetime(timestamp),
                symbol_from=symbol,
                symbol_to=sec_symbol,
                quantity_from=quantity,
                quantity_to=sec_quantity,
                rate_from=rate,
                rate_to=sec_rate,
                fees_in_fiat=fees
            )
            
        else:
            print(row)
    except Exception as e:
        logging.error("Error in row")
        logging.info(row)
        logging.error(e)
        raise e

def sortRow(row):
    if len(row) < 1:
        return ""
    return row[0]
    
with open('example/transactions.csv', newline='') as csvfile:

    spamreader = csv.reader(csvfile, delimiter=',')
    lines = []
    for row in spamreader:
        lines.append(row)   
    
    lines = lines[8:] # remove header
    lines = sorted(lines, key = lambda row: sortRow(row)) # sort by date
    for row in lines:
        processCSVRow(row)

environment = myjinja2.get_environment()
template = environment.get_template("tax.jinja2")

trans_report = transaction_history.get_report_for_year(fiscalYear)

content = template.render(
    transactions=trans_report["transactions"],
    coinstack_start=trans_report["coinstackStart"],
    coinstack_end=trans_report["coinstackEnd"],
    income_total=trans_report["incomeTotal"],
    paid_total=trans_report["paidTotal"],
    received_total=trans_report["receivedTotal"],
    fiscalYear=fiscalYear
)

with open("example/tax-report-"+str(fiscalYear)+".html", mode="w", encoding="utf-8") as file:
    file.write(content)





