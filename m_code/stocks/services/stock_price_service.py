from datetime import datetime
from ._context import StockPrice,StockPriceSource,Stock
from .sources.yahoo import fetch_stock_prices_yahoo

def fetch_stock_prices(source:StockPriceSource) -> list[StockPrice]:
    if source.type == "YAHOO":
        return fetch_stock_prices_yahoo(source)
    
def get_stock_price_at_datetime(stock_prices:list[StockPrice],dt:datetime) -> StockPrice:
    for stock_price in stock_prices:
        if (dt - stock_price.datetime).days == 0:
            return stock_price
    return None # Nothing found at the datetime

def get_current_price_of_stock(stock:Stock) -> StockPrice:
    price = None
    for item in stock.prices:
        price = item
    return price
