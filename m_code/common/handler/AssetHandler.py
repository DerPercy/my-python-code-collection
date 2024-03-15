from datetime import datetime
from icecream import ic
import logging
"""
Handle NFT assets
"""
class AssetHandler:
    content = None


    def __init__(self) -> None:
        self.content = {
            "possession": [],
            "lines": 0
        }

    def add_asset(self,date: datetime, asset_id: str,price_in_eur: float) -> bool:
        """
        Adds an asset
        """
        #self.content["lines"] = self.content["lines"] + 1
        for poss in self.content["possession"]:
            if asset_id == poss.get("assetId"):
                logging.error("Asset "+asset_id+ " already in store. Did not add again")
                return False
        poss = {
            "date": date,
            "assetId": asset_id,
            "price": price_in_eur
        }
        #self.calcPosition(poss)
        self.content["possession"].append(poss)
        return True

    def remove_asset (self,date: datetime, asset_id: str):
        """
        Removes an asset
        """
        for poss in self.content["possession"]:
            if asset_id == poss.get("assetId"):
                return True
        logging.error("Asset "+asset_id+ " is not in store. Could not remove")       
        return False
        


    def get_content(self) -> dict:
        """
        Get asset information
        """
        self.content["lines"] = len(self.content["possession"])
        return self.content
