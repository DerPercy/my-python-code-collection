"""
My HashMap implementation
"""
from typing import Dict, Generic, TypeVar, get_type_hints,get_args, Any
from attrs import define, field,asdict, has
from attr import attrs
from cattrs import Converter
from icecream import ic

T = TypeVar("T")

@define
@attrs(auto_attribs=True)
class MyHashMap(Generic[T]):
    map: dict[str, T] = field(default={})
    
    def __attrs_post_init__(self):
        if self.map == {}:  # this is needed to create a new dict instance and did not overwrite data from structure 
            self.map = {}

    def set_item(self, k: str, v: T) -> None:
        if not hasattr(self,"map"):
            self.map = {}
        self.map[k] = v
    
    def has_item(self,k) -> bool:
        return k in self.map.keys()
    
    def get_item(self, k: str) -> T:
        try:
            return self.map[k]
        except:
            return None
    #def get_map_type(self):
    #    return T
    def get_keys(self) -> list[str]:
        return self.map.keys()
    def item__list(self) -> list[T]:
        result: list[T] = []
        for key in self.map.keys():
            result.append(self.get_item(key))
        return result

my_conv = None

def prepare_converter(c:Converter) -> Converter:
    global my_conv
    def f_unstructure_hashmap(data: MyHashMap):
        ret_data = {
            "map":{}
        }
        for key in data.map.keys():
            ret_data["map"][key] = my_conv.unstructure(data.map[key])
        return ret_data
    
    def f_structure_hashmap(data,cls:type):
        #ic("On structure")
        #ic(data)
        #ic(cls.__qualname__)
        #ic(cls.__dict__)
        #ic(cls.__args__[0])
        #ic(cls)
        #ic(data["map"].keys())
        map = {}
        for key in data["map"].keys():
            map[key] = my_conv.structure(data["map"][key],cls.__args__[0])
        return MyHashMap(
            map=map
        )
    def f_unstructure_check(cls:type):
        return cls.__qualname__ == "MyHashMap"
    
    def f_unstructure_factory(cls:type):
        return f_unstructure_hashmap
    
    def f_structure_factory(obj):
        return f_structure_hashmap

    c.register_structure_hook_factory(
        predicate=f_unstructure_check,
        factory=f_structure_factory
    )
    c.register_unstructure_hook_factory(
        predicate=f_unstructure_check,
        factory=f_unstructure_factory
    )
    my_conv = c
    return c

def create_from_list(map_type:Generic[T], entry_list:list[T], key_field: str ) -> MyHashMap[T]:
    ret_map = MyHashMap[T]()
    for entry in entry_list:
        ret_map.set_item(k=getattr(entry, key_field), v=entry)
    return ret_map