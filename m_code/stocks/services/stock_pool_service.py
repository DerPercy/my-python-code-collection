from datetime import datetime

from ._context import StockPrice,StockPoolItem,StockPool

from .stock_price_service import get_stock_price_at_datetime, get_current_price_of_stock

def get_stock_with_lowest_indicator_value_at_datetime(stock_pools:list[StockPool], dt:datetime, indicator_key: str)-> tuple[StockPool, StockPrice]:
    global_min = None
    selected_pool= None
    selected_price = None
    for stock_pool in stock_pools:
        dt_price = get_stock_price_at_datetime(stock_pool.stock.prices,dt)
        if dt_price == None:
            continue
        checkValue = dt_price.indicators.get(indicator_key,None)
        if checkValue != None and global_min == None:
            global_min = checkValue
            selected_pool = stock_pool
            selected_price = dt_price
        elif checkValue != None and checkValue < global_min: # and global_min != None
            global_min = checkValue
            selected_pool = stock_pool
            selected_price = dt_price    
    return (selected_pool,selected_price)

def buy_stocks(items:list[StockPoolItem],price:StockPrice,amount:float) -> list[StockPoolItem]:
    pool_item = StockPoolItem(
        price=price,
        quantity=amount / price.value
    )
    items.append(pool_item)
    return items

def get_pool_value(items:list[StockPoolItem],current_price:StockPrice) -> float:
    value = 0
    for pool_item in items:                  
        value = value + ( pool_item.quantity * current_price.value )
    return value


def get_portfolio_value(pools:list[StockPool]) -> float:
    value = 0
    for pool in pools:                  
        value = value + get_pool_value(pool.items,get_current_price_of_stock(pool.stock))
    return value