from attrs import define
from .stock_pool_item import StockPoolItem
@define
class StockPool:
    """A representation of a stock pool"""
    items: list[StockPoolItem] = []
