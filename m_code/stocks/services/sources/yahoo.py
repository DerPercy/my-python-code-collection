import requests
from datetime import datetime
from .._context import StockPrice
from ._context import StockPriceSourceYahoo

def fetch_stock_prices_yahoo(source:StockPriceSourceYahoo) -> list[StockPrice]:
    #print("Get price from yahoo")
    #print(source.symbol)
    response = requests.get(
        "https://query2.finance.yahoo.com/v8/finance/chart/"+source.symbol+"?formatted=true&lang=de-DE&region=DE&includeAdjustedClose=true&interval=1mo&period1=1000&period2=1705190400&events=capitalGain|div|split&useYfid=true&corsDomain=de.finance.yahoo.com",
        headers={
            "User-Agent":"Mozilla/5.0"
        }
    )
    #print(response.status_code)
    #print(response.content)
    data = response.json()
    timestamps = data.get("chart",{}).get("result",[{}])[0].get("timestamp",[])
    values = data.get("chart",{}).get("result",[{}])[0].get("indicators",{}).get("quote",[{}])[0].get("open",[])
    
    # TRET.AS changed rate => need to normalize
    if source.symbol == "TRET.AS":
        for i in range(len(values)):
            if values[i] > 1000:
                values[i] = values[i] / 100
    #print(timestamps)
    stock_price_list = []
    for i in range(len(timestamps)):
        stock_price_list.append(
            StockPrice(
                datetime=datetime.fromtimestamp(timestamps[i]),
                value=values[i]
            )
        )
    return stock_price_list
