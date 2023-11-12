from attrs import define
from datetime import datetime

@define
class Transaction:
    """A representation of a coinbase tax transaction"""
    time: datetime
    fees: float = 0
    gain: float = 0 # Gain of this transaction (could be negative)
