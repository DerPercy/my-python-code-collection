from _context import myjinja2 

from models.stock import Stock
from models.stock_price_source import StockPriceSourceYahoo
from models.stock_pool import StockPool

from services.stock_price_service import fetch_stock_prices, get_stock_price_at_datetime
from services.stock_pool_service import buy_stocks,get_pool_value, get_stock_with_lowest_indicator_value_at_datetime, get_portfolio_value

from handler.PerformanceIndicator import PerformanceIndicator

# calculate indicators on the prices
ind = PerformanceIndicator("perf_1y",12)


pools:list[StockPool] = []



stocks = []
stocks.append( ("msci-world",       "URTH"))

stocks.append( ("msci-health-care", "XDWH.L"))
stocks.append( ("msci-tech",        "TNOW.PA"))
stocks.append( ("msci-telecom",     "WTEL.L"))
stocks.append( ("msci-cons-discr",  "XDWC.L")) 
stocks.append( ("msci-industrials", "XDWI.L")) 
stocks.append( ("msci-financials",  "LYPD.DE")) 
stocks.append( ("msci-real-estate", "TRET.AS")) 
stocks.append( ("msci-cons-stap",   "3SUE.DE"))
stocks.append( ("msci-materials",   "XDWM.DE"))
stocks.append( ("msci-energy",      "5MVW.DE"))
stocks.append( ("msci-utilities",   "XDWU.DE"))


for st in stocks:
    stock = Stock(
        slug=st[0],
        source=StockPriceSourceYahoo(
            symbol=st[1]
        )
    )
    stock.prices = fetch_stock_prices(stock.source)
    ind.iterate(stock.prices)
    pools.append(StockPool(stock))

price_info_list = []

buy_amount = 0
for stock_price in pools[0].stock.prices:
    # Single strategy
    #buy_stocks(pool.items,stock_price,100)
    last_price = stock_price
    buy_amount = buy_amount + 100
    # Mixed strategy
    (best_pool,best_price) = get_stock_with_lowest_indicator_value_at_datetime(pools,stock_price.datetime,"perf_1y")
    if best_pool != None:
        buy_stocks(best_pool.items,best_price,100)
    else: # Fallback: use the first element in portfolio
        buy_stocks(pools[0].items,stock_price,100)
    
    # Add price infos 
    stock_prices = []
    for pool in pools:
        stock_prices.append(
            get_stock_price_at_datetime(pool.stock.prices,stock_price.datetime)
        )

    price_info = {
        "dt": stock_price.datetime,
        "prices": stock_prices
    }
    price_info_list.append(price_info)


sell_value_mixed = get_portfolio_value(pools)
#for sp in stock.prices:
#    print(sp)

print("Amount invested:"+str(buy_amount))
print("Investment value (mixed):"+str(sell_value_mixed))


environment = myjinja2.get_environment()
template = environment.get_template("report.jinja2")

content = template.render(
    pools=pools,
    price_info_list=price_info_list
)
with open("report.html", mode="w", encoding="utf-8") as file:
    file.write(content)

#print(pool)