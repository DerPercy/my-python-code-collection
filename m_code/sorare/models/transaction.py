from attrs import define
from context import CoinStackHandler,AssetHandler
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
    
    def fill_assethandler(self, asset_handler:AssetHandler) -> None:
        """
        Fill the assethandler
        Handle sold and received cards
        """
        sender_cards = get_card_slugs(self.payload.get("senderSide"))
        receiver_cards = get_card_slugs(self.payload.get("receiverSide"))

        pass

    def i_am_the_receiver(self) -> bool:
        """
        Determines, if i am the receiver of the transaction
        """
        if self.payload.get("receiver") == None:
            return True
        return False
    
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
    
"""
Internal functions
"""

def get_card_slugs(side:dict) -> list[str]:
    cards = []
    for card in side.get("cards"):
        cards.append(card["slug"])
    return cards