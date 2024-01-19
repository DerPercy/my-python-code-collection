from .common.DictIterator import DictIterator

from ._context import StockPrice

class IndicatorHandler(DictIterator[StockPrice]):
    indicator_key:str
    def __init__(self,indicator_id:str) -> None:
        super().__init__()
        self.indicator_key = indicator_id
    
    def set_indicator_value(self,value:float):
        stock_price = self.get_current_item( )
        stock_price.indicators[self.indicator_key] =value