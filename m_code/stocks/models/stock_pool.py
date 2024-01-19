from attrs import define,field
from .stock_pool_item import StockPoolItem
from .stock import Stock
@define
class StockPool:
    """A representation of a stock pool"""
    stock: Stock
    items: list[StockPoolItem] = field(factory=list)
