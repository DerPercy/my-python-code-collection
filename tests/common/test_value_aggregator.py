from context_common import MyValueAggregator
import cattrs
from icecream import ic

def test_attrs_simple():
    """ Dummy test method, to see if pytest works """
    myva = MyValueAggregator()
    myva.add_value(10)
    json = cattrs.unstructure(myva)
    ic(json)
    assert 1==0


