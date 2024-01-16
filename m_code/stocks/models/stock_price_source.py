from attrs import define

@define
class StockPriceSource:
    """A representation of a stock price source"""
    type: str


@define
class StockPriceSourceYahoo(StockPriceSource):
    """ Source: Yahoo finance API"""
    symbol: str
    type: str = "YAHOO"