from ._context import StockPrice,StockPriceSource
from .sources.yahoo import fetch_stock_prices_yahoo

def fetch_stock_prices(source:StockPriceSource) -> list[StockPrice]:
    if source.type == "YAHOO":
        return fetch_stock_prices_yahoo(source)
    print("Test")
    pass
