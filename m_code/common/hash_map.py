"""
My HashMap implementation
"""
import logging
from typing import Dict, Generic, TypeVar

T = TypeVar("T")

class MyHashMap(Generic[T]):
    def __init__(self) -> None:
        self._store: Dict[str, T] = {}
          
    def set_item(self, k: str, v: T) -> None:
        self._store[k] = v
    
    def get_item(self, k: str) -> T:
        try:
            return self._store[k]
        except:
            return None
  

def create_from_list(map_type:Generic[T], entry_list:list[T], key_field: str ) -> MyHashMap[T]:
    ret_map = MyHashMap[T]()
    for entry in entry_list:
        ret_map.set_item(k=getattr(entry, key_field), v=entry)
    return ret_map