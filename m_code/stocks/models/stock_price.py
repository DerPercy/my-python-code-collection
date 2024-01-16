from attrs import define
from datetime import datetime

@define
class StockPrice:
    """A representation of a stock price"""
    datetime: datetime
    value: float 
