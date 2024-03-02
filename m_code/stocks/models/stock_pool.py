from attrs import define,field
from .stock_pool_item import StockPoolItem
from .stock import Stock
from .stock_price import StockPrice

@define
class StockPool:
    """A representation of a stock pool"""
    stock: Stock
    items: list[StockPoolItem] = field(factory=list)

    def get_invested_amount(self) -> float:
        value = 0
        for item in self.items:
            value = value + (item.quantity * item.price.value)
        return value

