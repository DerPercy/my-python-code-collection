from models.stock import Stock
from models.stock_price_source import StockPriceSourceYahoo
from models.stock_pool import StockPool

from services.stock_price_service import fetch_stock_prices
from services.stock_pool_service import buy_stocks,get_pool_value

stock = Stock(
    slug="msci-health-care",
    source=StockPriceSourceYahoo(
        symbol="XDWH.L"
    )
)

stock = Stock(
    slug="msci-world",
    source=StockPriceSourceYahoo(
        symbol="URTH"
    )
)



stock.prices = fetch_stock_prices(stock.source)

pool = StockPool()
buy_amount = 0
last_price = None
for stock_price in stock.prices:
    buy_stocks(pool.items,stock_price,100)
    last_price = stock_price
    buy_amount = buy_amount + 100

sell_value = get_pool_value(pool.items,last_price)

print(stock.prices)

print("Amount invested:"+str(buy_amount))
print("Investment value:"+str(sell_value))


#print(pool)