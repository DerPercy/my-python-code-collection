from attrs import define
from context import CoinStackHandler
from datetime import datetime, timedelta

@define
class Transaction:
    """A representation of a sorare account transaction"""
    payload: dict
    current_user_slug: str

    def process_payload(self):
        print(self.payload.get("entryType"))
        #if self.payload.get("entryType") == "PAYMENT":
        print(self.payload)
        return self
    
    def in_fiscal_year(self, fy:int) -> bool:
        return fy == self.get_datetime( ).year
    
    def fill_coinstackhandler(self, csh:CoinStackHandler) -> None:
        eth_amount = self.get_eth_amount()
        if eth_amount > 0:
            #if transaction["type"] != "REWARD":
            csh.addQuantity(self.get_datetime(),eth_amount,self.get_eth_exchange_rate( ))
        elif eth_amount < 0:
            return csh.removeQuantity(self.get_datetime(),eth_amount * -1,self.get_eth_exchange_rate( ))
        
        return None
    def get_eth_amount(self):
        return float(self.payload["amount"]) / 1000000000000000000 
    
    def get_eth_exchange_rate(self):
        return self.payload["amountInFiat"]["eur"] / self.get_eth_amount( )
    
    def get_datetime(self) -> datetime:
        return datetime.fromisoformat(self.payload.get("date").replace("Z","+00:00")) + timedelta(hours=1)