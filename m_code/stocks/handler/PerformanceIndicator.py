from ._context import StockPrice
from .IndicatorHandler import IndicatorHandler


class PerformanceIndicator(IndicatorHandler):
    offset:int
    def __init__(self, indicator_id: str,offset:int) -> None:
        super().__init__(indicator_id)
        self.offset = offset

    def on_item(self, item: StockPrice) -> None:
        super().on_item(item)
        stock_price_ref = self.get_item_at_offset(self.offset * -1)
        if stock_price_ref != None:
            self.set_indicator_value(item.value / stock_price_ref.value)

    
    
