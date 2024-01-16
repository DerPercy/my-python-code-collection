from ._context import StockPrice,StockPoolItem


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