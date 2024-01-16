from attrs import define
from .stock_price import StockPrice
#import StockPrice

@define
class StockPoolItem:
    """A representation of a stock pool item"""
    price: StockPrice
    quantity: float
