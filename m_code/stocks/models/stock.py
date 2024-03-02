from attrs import define
from . import stock_price
from . import stock_price_source
@define
class Stock:
    """A representation of a stock"""
    slug: str
    source: stock_price_source.StockPriceSource 
    prices: list[stock_price.StockPrice] = []

    def get_latest_price(self) -> stock_price.StockPrice:
        if len(self.prices) == 0:
            return None
        return self.prices[-1]