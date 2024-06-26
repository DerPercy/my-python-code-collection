from attrs import define
from datetime import datetime


"""
Use Transaction from /handler folder

"""
@define
class Transaction:
    """A representation of a coinbase tax transaction"""
    time: datetime
    fees: float = 0
    gain: float = 0 # Gain of this transaction (could be negative)
    coinstack_before: dict = {}
    coinstack_after: dict = {}
    description: str = ""
    income: float = 0 # staking income 
    budget_info: str = ""
    gain_details: dict = {} # details about gain
    
