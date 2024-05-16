import csv
import logging
import re

from .transaction_history import TransactionHistory
from datetime import datetime, timedelta

class CSVProcessor:
    def process_csv(self,file_dest:str,transaction_history:TransactionHistory = None) -> TransactionHistory:
        if transaction_history == None:
            transaction_history = TransactionHistory()
        with open(file_dest, newline='') as csvfile:

            spamreader = csv.reader(csvfile, delimiter=',')
            lines = []
            for row in spamreader:
                lines.append(row)   
    
            lines = lines[self._get_header_line_count():] # remove header
            lines = sorted(lines, key = lambda row: self._get_sort_method()(row)) # sort by date
            for row in lines:
                self._process_csv_row(row,transaction_history)
        return transaction_history
    def getDatetime(self,dateString):
        return datetime.fromisoformat(dateString.replace("Z","+00:00")) + timedelta(hours=1)
    def _get_header_line_count(self)->int:
        raise Exception("Sorry, I'm abstract") 
    def _get_sort_method(self)->callable:
        raise Exception("Sorry, I'm abstract")
    def _process_csv_row(self,row,transaction_history:TransactionHistory):
        raise Exception("Sorry, I'm abstract")

class CSVProcessorV2(CSVProcessor):

    def getDatetime(self, dateString):
        return datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S UTC')
    def _process_csv_row(self, row, transaction_history: TransactionHistory):
        #ID,Timestamp,Transaction Type,                                     Asset,  Quantity Transacted,Price Currency, Price at Transaction,Subtotal,Total (inclusive of fees and/or spread),Fees and/or Spread,Notes
        #66351c189a87975631451030,2024-05-03 17:17:12 UTC,Staking Income,   ETH2,   0.00003642178,      EUR,            2857.1544069329423321965,0.10,0.10,0,

        timestamp = row[1]
        action = row[2]
        symbol = row[3]
        quantity = float(row[4])
        rate = float(row[6])
        if row[7] == "":
            eurWoFees = 0 
        else:
            eurWoFees = float(row[7])
        if row[9] == "":
            fees = float(0)
        else:
            fees = float(row[9])
        transactionDescription = row[10]

        try:
            if action == 'Buy' or action == 'Receive' or action == 'Advanced Trade Buy': # Buy/Receive coins in coinbase
                transaction_history.action_buy(
                    dt          =   self.getDatetime(timestamp),
                    symbol      =   symbol,
                    quantity    =   quantity,
                    rate        =   rate,
                    fees_in_fiat=   fees
                )
            elif action == 'Learning Reward' or action == 'Staking Income': # Learing rewards
                transaction_history.action_rewards(
                    dt          =   self.getDatetime(timestamp),
                    symbol      =   symbol,
                    quantity    =   quantity,
                    rate        =   rate,
                    fees_in_fiat=   fees,
                    is_staking  =(action == 'Staking Income')
                )
            elif action == "Send" or action == 'Sell' or action == 'Advance Trade Sell': # Send/Sell coins in coinbase
                transaction_history.action_sell(
                    dt          =   self.getDatetime(timestamp),
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
                    dt=self.getDatetime(timestamp),
                    symbol_from=symbol,
                    symbol_to=sec_symbol,
                    quantity_from=quantity,
                    quantity_to=sec_quantity,
                    rate_from=rate,
                    rate_to=sec_rate,
                    fees_in_fiat=fees
                )
            elif action == "Deposit" or action == "Withdrawal":
                # ignore
                pass
            else:
                print(row)
        except Exception as e:
            logging.error("Error in row")
            logging.info(row)
            logging.error(e)
            raise e


    def _get_header_line_count(self) -> int:
        return 4
    def _get_sort_method(self) -> callable:
        def sortRow(row):
            if len(row) < 1:
                return ""
            return row[0]
        return sortRow


class CSVProcessorV1(CSVProcessor):
    def _process_csv_row(self, row, transaction_history: TransactionHistory):
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
                    dt          =   self.getDatetime(timestamp),
                    symbol      =   symbol,
                    quantity    =   quantity,
                    rate        =   rate,
                    fees_in_fiat=   fees
                )
            elif action == 'Learning Reward' or action == 'Rewards Income': # Learing rewards
                transaction_history.action_rewards(
                    dt          =   self.getDatetime(timestamp),
                    symbol      =   symbol,
                    quantity    =   quantity,
                    rate        =   rate,
                    fees_in_fiat=   fees,
                    is_staking  =(action == 'Rewards Income')
                )
            elif action == "Send" or action == 'Sell' or action == 'Advanced Trade Sell': # Send/Sell coins in coinbase
                transaction_history.action_sell(
                    dt          =   self.getDatetime(timestamp),
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
                    dt=self.getDatetime(timestamp),
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


    def _get_header_line_count(self) -> int:
        return 8
    def _get_sort_method(self) -> callable:
        def sortRow(row):
            if len(row) < 1:
                return ""
            return row[0]
        return sortRow

