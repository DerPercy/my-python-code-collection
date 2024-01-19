from typing import Dict, Generic, TypeVar
from abc import abstractmethod

T = TypeVar("T")

class DictIterator(Generic[T]):
    current_item: T 
    current_index: int
    current_items: list[T]

    def __init__(self) -> None:
        super().__init__()
        self.current_item = None
        self.current_index = 0
        self.current_items = []

    def iterate(self, items: list[T]):
        self.current_items = items
        for i in range(len(items)):
            self.current_index = i
            self.current_item = items[i]
            self.on_item(self.current_item)

    @abstractmethod
    def on_item(self,item: T) -> None:
        pass

    def get_current_item(self) -> T:
        return self.current_item

    def get_item_at_offset(self,offset:int) -> T:
        pos = self.current_index + offset
        if pos < 0:
            return None
        if pos >= len(self.current_items):
            return None
        return self.current_items[pos]