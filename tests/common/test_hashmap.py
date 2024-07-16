"""Sample test functions"""
from context_common import MyHashMap,prepare_converter
import cattrs
from icecream import ic
from attrs import define
from attr import attrs

@define
@attrs(auto_attribs=True)
class MyInnerAttrsClass:
    value:str
@define
@attrs(auto_attribs=True)
class MyAttrsClass:
    myMap: MyHashMap[MyHashMap[MyInnerAttrsClass]]

def test_attrs_simple():
    """ Dummy test method, to see if pytest works """
    my_hm = MyHashMap[str]()
    my_hm.set_item("a","2")

    my_outer_hm = MyHashMap[MyHashMap[str]]()
    my_outer_hm.set_item("b",my_hm)
    json = prepare_converter(cattrs.GenConverter()).unstructure(my_outer_hm) #,MyHashMap[MyHashMap[int]])
    ic(json)
    new = prepare_converter(cattrs.GenConverter()).structure(json,MyHashMap[MyHashMap[str]])
    #new = cattrs.GenConverter().structure(my_hm,MyHashMap[int])
    ic(my_outer_hm)
    ic(new)
    assert my_outer_hm == new

def test_attrs_nested():
    """ Dummy test method, to see if pytest works """
    inner = MyInnerAttrsClass(value="test-value")
    inner_hm = MyHashMap[MyInnerAttrsClass]()
    inner_hm.set_item("test",inner)

    outer_hm = MyHashMap[MyHashMap[MyInnerAttrsClass]]()
    outer_hm.set_item("inner",inner_hm)

    outer = MyAttrsClass(
        myMap=outer_hm
    )
    json = prepare_converter(cattrs.GenConverter()).unstructure(outer)   
    ic(json)

    assert outer.myMap.get_item("inner").get_item("test").value == "test-value" 
    
    assert json == {"myMap": {"map": { "inner": {"map": {"test": { "value": "test-value"}}}}}}

    new = prepare_converter(cattrs.GenConverter()).structure(json,MyAttrsClass)
    assert outer == new
  