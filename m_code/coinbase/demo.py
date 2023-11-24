import csv
import logging
import re

from datetime import datetime, timedelta
from handler.Coinstack import CoinStackHandler
from models.transaction import Transaction

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        transaction.fees = fees
        if action == 'Buy' or action == 'Receive' or action == 'Advanced Trade Buy': # Buy/Receive coins in coinbase
            csh = getCoinStack(symbol)
            csh.addQuantity(getDatetime(timestamp),quantity,rate)
        elif action == 'Learning Reward' or action == 'Rewards Income': # Learing rewards
            csh = getCoinStack(symbol)
            csh.addQuantity(getDatetime(timestamp),quantity,rate)
            transaction.gain = quantity * rate 
        elif action == "Send" or action == 'Sell' or action == 'Advanced Trade Sell': # Send/Sell coins in coinbase
            csh = getCoinStack(symbol)
            result = csh.removeQuantity(getDatetime(timestamp),quantity,rate)
            #print(result)
            transaction.gain = result.get("gainInEur")
        elif action == "Convert": # Convert one Coin to another
            result = re.search(r"Converted ([\d.]*) ([^\s]*) to ([\d.]*) ([^\s]*)", transactionDescription)
            # Add second coin
            sec_symbol = result.group(4)
            sec_quantity = float(result.group(3))
            sec_rate = eurWoFees / sec_quantity
            csh = getCoinStack(sec_symbol)
            csh.addQuantity(getDatetime(timestamp),sec_quantity,sec_rate)
            # Remove first coin
            csh = getCoinStack(symbol)
            result = csh.removeQuantity(getDatetime(timestamp),quantity,rate)
            transaction.gain = result.get("gainInEur")
            
        else:
            print(row)
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
    if item.time.year == 2023:
        return True
    return False

transactions = filter(inFiscalYear, transactions)
totalFees = 0
totalGain = 0

for transaction in transactions:
    #print(transaction)
    totalFees = totalFees + transaction.fees
    totalGain = totalGain + transaction.gain
print(totalFees)
print(totalGain)

#print(transactions)





