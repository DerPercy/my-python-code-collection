from datetime import datetime
import copy

class CoinStackHandler:
    content = None

    def __init__(self) -> None:
        self.content = {
            "possession": [],
            "lines": 0
        }

    def addQuantity(self,date: datetime,quantity: float,exchangeRate: float) -> bool:
        self.content["lines"] = self.content["lines"] + 1
        poss = {
            "date": date,
            "quantity": quantity,
            "rate": exchangeRate
        }
        self.calcPosition(poss)
        self.content["possession"].append(poss)
        return True
    
    
    def calcPosition(self, position):
        """ Update the additional fields (for UI) on the possession position"""
        position["eurAmount"] = position["quantity"] * position["rate"]
        #position["eurAmountUI"] = toEURAmountUI(position["eurAmount"])
        #position["rateUI"] = toExchangeRateUI(position["rate"])
        #position["quantityUI"] = ETHquantityToUI(position["quantity"])
        #position["dateUI"] = toDateUI(position["date"])

    def removeQuantity(self,date: datetime,quantity: float,exchangeRate: float) -> dict:
        quantityLeft = quantity
        possessionsToSell = []
        while quantityLeft > 0.00000001: # To pevent rounding errors
            nextPos = self._getNextPossessionToSell(quantityLeft)
            possessionsToSell.append(nextPos)
            quantityLeft = quantityLeft - nextPos["quantity"]

        sellAmount = quantity * exchangeRate
        gainInEur = sellAmount
        for soldPoss in possessionsToSell:
            soldPoss["rateSell"] = exchangeRate
            #soldPoss["rateSellUI"] = toExchangeRateUI(exchangeRate)
            soldPoss["eurSell"] = soldPoss["quantity"] * exchangeRate
            #soldPoss["eurSellUI"] = toEURAmountUI(soldPoss["eurSell"])
            soldPoss["eurGain"] = soldPoss["eurSell"] - soldPoss["amountEur"]
            #soldPoss["eurGainUI"] = toEURAmountUI(soldPoss["eurGain"])

            gainInEur = gainInEur - soldPoss["amountEur"]
        return {
            "soldPossessions": possessionsToSell,
            "sold": {
                "quantity": quantity,
                "rate": exchangeRate,
                "amountEur": sellAmount,
               # "amountEurUI": toEURAmountUI(sellAmount)
            },
            "gainInEur": gainInEur,
            #"gainInEurUI": toEURAmountUI(gainInEur)
        }
    
    def _getNextPossessionToSell(self,quantity:float):
        nextElement = self.content["possession"][0]
        if int(nextElement["quantity"]*10000) > int(quantity *10000):
            nextElement["quantity"] = nextElement["quantity"] - quantity
            self.calcPosition(nextElement)
        else:
            quantity = nextElement["quantity"]
            self.content["possession"].remove(nextElement)
        return {
            "quantity": quantity,
            #"quantityUI": ETHquantityToUI(quantity),
            "rate": nextElement["rate"],
            #"rateUI": toExchangeRateUI(nextElement["rate"]),
            "amountEur": quantity * nextElement["rate"],
            #"amountEurUI": toEURAmountUI(quantity * nextElement["rate"]),
            "dateUI": nextElement["date"].strftime("%d.%m.%Y")
        }

    def getContent(self):
        retData = copy.deepcopy(self.content)
        self.fillHeadData(retData)
        return retData
    
    def fillHeadData(self,content):
        quantitySum = 0
        eurAmountSum = 0
        for entry in content["possession"]:
            quantitySum += entry["quantity"]
            eurAmountSum += entry["eurAmount"]
        content["totalQuantity"] = quantitySum
        #content["totalQuantityUI"] = ETHquantityToUI(quantitySum)
        content["totalEurAmount"] = eurAmountSum
        #content["totalEurAmountUI"] = toEURAmountUI(eurAmountSum)

