from attrs import define
from context import CoinStackHandler,AssetHandler
from datetime import datetime, timedelta
from icecream import ic
import logging

@define
class Transaction:
    """A representation of a sorare account transaction"""
    payload: dict
    current_user_slug: str

    def process_payload(self):
        #print(self.payload.get("entryType"))
        #if self.payload.get("entryType") == "PAYMENT":
        #print(self.payload)
        return self
    
    def in_fiscal_year(self, fy:int) -> bool:
        return fy == self.get_datetime( ).year
    
    def fill_assethandler(self, asset_handler:AssetHandler) -> None:
        """
        Fill the assethandler
        Handle sold and received cards
        """
        if self.payload.get("entryType") == "PAYMENT_FEE":
            # Payment Fee needs not be handled
            return True
        if self.payload.get("entryType") == "DEPOSIT":
            # Deposits needs not be handled
            return True

        if self.payload.get("tokenOperation") == None:
            logging.error("No tokenOperation Found")
            ic(self.payload)
            return False

        price = 0
        if self.payload.get("tokenOperation").get("__typename") == "TokenBid":
            received_cards = get_card_slugs(self.payload.get("tokenOperation",{}).get("auction"))
            sent_cards = []
            price = self.payload.get("amountInFiat").get("eur")

        else:
            if self.i_am_the_receiver():
                received_cards = get_card_slugs(self.payload.get("tokenOperation",{}).get("senderSide"))
                sent_cards = get_card_slugs(self.payload.get("tokenOperation",{}).get("receiverSide"))
            else:
                received_cards = get_card_slugs(self.payload.get("tokenOperation",{}).get("receiverSide"))
                sent_cards = get_card_slugs(self.payload.get("tokenOperation",{}).get("senderSide"))
        
            for sent_card in sent_cards:
                if not asset_handler.remove_asset(self.get_datetime(),sent_card):
                    ic(self.payload)
                    return False
            price = 27.27
        if len(received_cards) > 0:
            price_per_unit = price / len(received_cards)
            for received_card in received_cards:
                if(received_card == "richie-laryea-2021-limited-93"):                    
                    ic(self.i_am_the_receiver())
                if not asset_handler.add_asset(self.get_datetime(),received_card,price_per_unit):
                    ic(self.payload)
                    return False
        return True

    def i_am_the_receiver(self,log:bool = False) -> bool:
        """
        Determines, if i am the receiver of the transaction
        """
        if self.payload.get("tokenOperation").get("sender") != None:
            if self.payload.get("tokenOperation").get("sender").get("slug") == self.current_user_slug:
                return False

        if self.payload.get("tokenOperation").get("receiver") == None:
            return True
        else:
            if self.payload.get("tokenOperation").get("receiver").get("slug") == self.current_user_slug:
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
    if side == None:
        return cards
    for card in side.get("cards"):
        cards.append(card["slug"])
    return cards