import csv
import logging
import re
import copy

from datetime import datetime, timedelta
from handler.Coinstack import CoinStackHandler
from models.transaction import Transaction
from jinja2 import Environment, FileSystemLoader

from context import myjinja2 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Customizing part
fiscalYear = 2023


# Implementation part
coinstacks = {

}

transactions = []
def getDatetime(dateString):
	return datetime.fromisoformat(dateString.replace("Z","+00:00")) + timedelta(hours=1)
def getCoinStack(symbol:str) -> CoinStackHandler:
    global coinstacks
    if coinstacks.get(symbol) == None:
        coinstacks[symbol] = CoinStackHandler()
    return coinstacks.get(symbol)

def processCSVRow(row):
    global coinstacks
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
    #eurInclFees = float(row[7])
    if row[8] == "":
        fees = float(0)
    else:
        fees = float(row[8])
    transactionDescription = row[9]

    #print(row)
    try:
        transaction = Transaction(getDatetime(timestamp))
        transaction.coinstack_before = copy.deepcopy(coinstacks)
        transaction.fees = fees
        if action == 'Buy' or action == 'Receive' or action == 'Advanced Trade Buy': # Buy/Receive coins in coinbase
            csh = getCoinStack(symbol)
            csh.addQuantity(getDatetime(timestamp),quantity,rate)
            transaction.description = "Kauf {:.4}".format(quantity)+" "+symbol+ " für {:10.2f}".format(quantity*rate)+" EUR"
        elif action == 'Learning Reward' or action == 'Rewards Income': # Learing rewards
            csh = getCoinStack(symbol)
            csh.addQuantity(getDatetime(timestamp),quantity,rate)
            if action == 'Rewards Income':
                transaction.income = quantity * rate
                transaction.description = "Staking Erlöse: {:10.4f}".format(quantity*rate)+" EUR"
            else:
                transaction.gain = quantity * rate 
        elif action == "Send" or action == 'Sell' or action == 'Advanced Trade Sell': # Send/Sell coins in coinbase
            csh = getCoinStack(symbol)
            result = csh.removeQuantity(getDatetime(timestamp),quantity,rate)
            #print(result)
            transaction.gain = result.get("gainInEur")
            transaction.gain_details = result
            transaction.description = "Verkauf {:.4}".format(quantity)+" "+symbol+ " für {:10.2f}".format(quantity*rate)+" EUR"
            
        elif action == "Convert": # Convert one Coin to another
            print("Convert")
            result = re.search(r"Converted ([\d.,]*) ([^\s]*) to ([\d.,]*) ([^\s]*)", transactionDescription)
            # Add second coin
            sec_symbol = result.group(4)
            sec_quantity = float(result.group(3).replace(",", "."))
            sec_rate = eurWoFees / sec_quantity
            csh = getCoinStack(sec_symbol)
            csh.addQuantity(getDatetime(timestamp),sec_quantity,sec_rate)
            # Remove first coin
            csh = getCoinStack(symbol)
            result = csh.removeQuantity(getDatetime(timestamp),quantity,rate)
            transaction.gain = result.get("gainInEur")
            transaction.description = "Umwandlung {:.4}".format(quantity)+" "+symbol+" in  {:.4}".format(sec_quantity)+" "+sec_symbol+" (Wert: {:10.2f}".format(quantity*rate)+" EUR)"
            transaction.gain_details = result
            
        else:
            print(row)
        
        transaction.coinstack_after = copy.deepcopy(coinstacks)

        transactions.append(transaction)
        #if symbol == "SAND":
            #logging.info(row)
            #csh = getCoinStack(symbol)
            #logging.info(csh.getContent())
    except Exception as e:
        logging.error("Error in row")
        logging.info(row)
        csh = getCoinStack(symbol)
        logging.info(csh.getContent())
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
    
    #print(lines[:10])
    lines = lines[8:] # remove header
    #print(lines[:10])
    lines = sorted(lines, key = lambda row: sortRow(row)) # sort by date
    for row in lines:
        processCSVRow(row)

for cs in coinstacks:
    
    print("========== "+cs+" ==========")
    print(coinstacks.get(cs).getContent())
    pass


def inFiscalYear(item:Transaction):
    if item.time.year == fiscalYear:
        return True
    return False

transactions = filter(inFiscalYear, transactions)
totalFees = 0
totalGain = 0

report_transactions = []
coinstack_start = None
coinstack_end = None
income_total = 0 # Erlöse

paid_total = 0
received_total = 0
for transaction in transactions:
    #print(transaction)
    totalFees = totalFees + transaction.fees
    totalGain = totalGain + transaction.gain
    report_transactions.append(transaction)
    if coinstack_start == None:
        coinstack_start = transaction.coinstack_before
    coinstack_end = transaction.coinstack_after
    transaction.coinstack_before = None
    transaction.coinstack_after = None
    if transaction.income > 0:
        income_total = income_total + transaction.income
        transaction.budget_info = "Gesamt: {:10.2f}".format(income_total)+" EUR"
    if transaction.gain_details.get("sellAmount",0) > 0:
        received_total = received_total + transaction.gain_details.get("sellAmount",0)
        paid_total = paid_total + transaction.gain_details.get("buyAmount",0)
        transaction.budget_info = "Gesamt: Ausgaben: {:10.2f}".format(paid_total)+" EUR / Einnahmen: {:10.2f}".format(received_total)+ " EUR"
    
print(totalFees)
print(totalGain)
print(income_total)

environment = myjinja2.get_environment()
template = environment.get_template("tax.jinja2")

content = template.render(
    transactions=report_transactions,
    coinstack_start=coinstack_start,
    coinstack_end=coinstack_end,
    income_total=income_total,
    paid_total=paid_total,
    received_total=received_total,
    fiscalYear=fiscalYear
)
with open("example/tax-report.html", mode="w", encoding="utf-8") as file:
    file.write(content)
#print(transactions)





