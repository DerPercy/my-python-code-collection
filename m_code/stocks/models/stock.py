from attrs import define
from . import stock_price
from . import stock_price_source
@define
class Stock:
    """A representation of a stock"""
    slug: str
    source: stock_price_source.StockPriceSource 
    prices: list[stock_price.StockPrice] = []
