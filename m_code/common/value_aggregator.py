
from attrs import define, field
from icecream import ic
from attr import attrs

@define
@attrs(auto_attribs=True)
class MyValueAggregator():
    sum_value: float = field(default=0)
    cnt: int = field(default=0)
    def add_value(self,val:float):
        self.cnt = self.cnt + 1
        self.sum_value = self.sum_value + val
    def has_values(self) -> bool:
        return self.cnt > 0

    def get_average(self) -> float:
        if self.cnt > 0:
            return self.sum_value / float(self.cnt)
        return 0
    def count(self) -> int:
        return self.cnt
    