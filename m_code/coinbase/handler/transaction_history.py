import copy 

from datetime import datetime
from .transaction import Transaction
from .Coinstack import CoinStackHandler


class TransactionHistory:

    coinstacks = {}
    transactions = []
    def __init__(self) -> None:
        self.coinstacks = {}
        self.transactions = []
    def action_buy(self, dt:datetime, symbol:str,quantity:float,rate:float,fees_in_fiat:float) -> None:
        """
        Action: buy a coin
        """
        transaction = Transaction(dt)
        transaction.coinstack_before = copy.deepcopy(self.coinstacks)
        transaction.fees = fees_in_fiat
        csh = getCoinStack(symbol,self.coinstacks)
        csh.addQuantity(dt,quantity,rate)
        transaction.description = "Kauf {:.4}".format(quantity)+" "+symbol+ " für {:10.2f}".format(quantity*rate)+" EUR"
        transaction.coinstack_after = copy.deepcopy(self.coinstacks)
        self.transactions.append(transaction)

    def action_rewards(self, dt:datetime, symbol:str,quantity:float,rate:float,fees_in_fiat:float,is_staking:bool) -> None:
        """
        Action: get a reward
        """
        transaction = Transaction(dt)
        transaction.coinstack_before = copy.deepcopy(self.coinstacks)
        transaction.fees = fees_in_fiat
        csh = getCoinStack(symbol,self.coinstacks)
        csh.addQuantity(dt,quantity,rate)
        if is_staking:
            transaction.income = quantity * rate
            transaction.description = "Staking Erlöse: {:10.4f}".format(quantity*rate)+" EUR"
        else:
            transaction.gain = quantity * rate 
        transaction.coinstack_after = copy.deepcopy(self.coinstacks)
        self.transactions.append(transaction)


    def action_sell(self, dt:datetime, symbol:str,quantity:float,rate:float,fees_in_fiat:float) -> None:
        """
        Action: sell a coin
        """
        transaction = Transaction(dt)
        transaction.coinstack_before = copy.deepcopy(self.coinstacks)
        transaction.fees = fees_in_fiat

        csh = getCoinStack(symbol,self.coinstacks)
        result = csh.removeQuantity(dt,quantity,rate)
        transaction.gain = result.get("gainInEur")
        transaction.gain_details = result
        transaction.description = "Verkauf {:.4}".format(quantity)+" "+symbol+ " für {:10.2f}".format(quantity*rate)+" EUR"
        transaction.coinstack_after = copy.deepcopy(self.coinstacks)
        self.transactions.append(transaction)
            


    def action_convert(self, dt:datetime, symbol_from:str,symbol_to:str,quantity_from:float,quantity_to:float,rate_from:float,rate_to:float,fees_in_fiat:float) -> None:
        """
        Action: sell a coin
        """
        transaction = Transaction(dt)
        transaction.coinstack_before = copy.deepcopy(self.coinstacks)
        transaction.fees = fees_in_fiat

        # Add target coin
        csh = getCoinStack(symbol_to,self.coinstacks)
        csh.addQuantity(dt,quantity_to,rate_to)
        # Remove source coin
        csh = getCoinStack(symbol_from,self.coinstacks)
        result = csh.removeQuantity(dt,quantity_from,rate_from)
        transaction.gain = result.get("gainInEur")
        transaction.description = "Umwandlung {:.4}".format(quantity_from)+" "+symbol_from+" in  {:.4}".format(quantity_to)+" "+symbol_to+" (Wert: {:10.2f}".format(quantity_from*rate_from)+" EUR)"
        transaction.gain_details = result
        transaction.coinstack_after = copy.deepcopy(self.coinstacks)
        self.transactions.append(transaction)
    
    def get_report_for_year(self, year:int) -> dict:
        filtered_transactions = filter(in_fiscal_year_func(year), self.transactions)
        totalFees = 0
        totalGain = 0
        report_transactions = []
        coinstack_start = None
        coinstack_end = None
        income_total = 0 # Erlöse
        paid_total = 0
        received_total = 0
        for transaction in filtered_transactions:
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
        return {
            "transactions": report_transactions,
            "coinstackStart": coinstack_start,
            "coinstackEnd": coinstack_end,
            "incomeTotal": income_total,
            "paidTotal": paid_total,
            "receivedTotal": received_total
        }
    
"""
Utility Methods
"""
def in_fiscal_year_func(fiscal_year:int) -> callable:
    def inFiscalYear(item:Transaction):
        if item.time.year == fiscal_year:
            return True
    return inFiscalYear


def getCoinStack(symbol:str,coinstacks) -> CoinStackHandler:
    if coinstacks.get(symbol) == None:
        coinstacks[symbol] = CoinStackHandler()
    return coinstacks.get(symbol)