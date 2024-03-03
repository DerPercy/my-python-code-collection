from attrs import define

@define
class TaxEntry:
    """A representation of a sorare tax relevant entry"""
    description: str
    eth_result: dict = {} 
    entryEurGain: float = 27.27

    def calculate(self):
        return self;
