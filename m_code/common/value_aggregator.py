
class MyValueAggregator():
    sum_value = None
    cnt = None
    def __init__(self) -> None:
        self.sum_value = 0
        self.cnt = 0
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
    