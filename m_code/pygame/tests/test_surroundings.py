"""Test common surroundings"""
from .context import collision


# initialize 6x7 map
map = [ [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,1,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0]
    ]

def test_borders():
    result = collision.create_surroundings(map,(0,0))
    assert result == [  [1,1,1],
                        [1,0,0],
                        [1,0,0]]
    
    result = collision.create_surroundings(map,(6,5))
    assert result == [  [0,0,1],
                        [0,0,1],
                        [1,1,1]]

def test_collisions():
    result = collision.create_surroundings(map,(0,1))
    assert result == [  [1,0,0],
                        [1,0,0],
                        [1,0,1]]
