from attrs import define,field
from datetime import datetime

@define
class StockPrice:
    """A representation of a stock price"""
    datetime: datetime
    value: float 
    indicators:dict = field(factory=dict) #this needs to be done, otherwise all StockPrices have the same initicators object (class variable instead of instance var)
