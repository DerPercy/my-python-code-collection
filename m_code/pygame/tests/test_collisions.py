"""Test common collisions"""
from .context import collision


"""
Map:

        y-1
x-1      0   x+1
        y+1


"""


def test_no_collision():
    """ No collision """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (-1,-1)
    assert result[1] == []  # No collisions

def test_collision_y():
    """ Collision top """
    result = collision.calc_collision(
        [[0,1,0],
         [0,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (-1,1)
    assert result[1] == [(0,-1)]
    
    """ Collision bottom """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [0,1,0]],
        (1,1)
    )
    assert result[0] == (1,-1)
    assert result[1] == [(0,1)]

def test_collision_x():

    """ Collision left """
    result = collision.calc_collision(
        [[0,0,0],
         [1,0,0],
         [0,0,0]],
        (-1,1)
    )
    assert result[0] == (1,1)
    assert result[1] == [(-1,0)]

    """ Collision right """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,1],
         [0,0,0]],
        (1,1)
    )
    assert result[0] == (-1,1)
    assert result[1] == [(1,0)]

def test_collision_y_x():

    """ Collision top left """
    result = collision.calc_collision(
        [[0,1,0],
         [1,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (1,1)
    assert result[1] == [(-1,0),(0,-1)]


    """ Collision top right """
    result = collision.calc_collision(
        [[0,1,0],
         [0,0,1],
         [0,0,0]],
        (1,-1)
    )
    assert result[0] == (-1,1)
    assert result[1] == [(1,0),(0,-1)]

    """ Collision bottom left """
    result = collision.calc_collision(
        [[0,0,0],
         [1,0,0],
         [0,1,0]],
        (-1,1)
    )
    assert result[0] == (1,-1)
    assert result[1] == [(-1,0),(0,1)]


    """ Collision bottom right """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,1],
         [0,1,0]],
        (1,1)
    )
    assert result[0] == (-1,-1)
    assert result[1] == [(1,0),(0,1)]


def test_collision_corner():

    """ Collision top left """
    result = collision.calc_collision(
        [[1,0,0],
         [0,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (1,1)
    assert result[1] == [(-1,-1)]


    """ Collision top right """
    result = collision.calc_collision(
        [[0,0,1],
         [0,0,0],
         [0,0,0]],
        (1,-1)
    )
    assert result[0] == (-1,1)
    assert result[1] == [(1,-1)]


    """ Collision bottom left """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [1,0,0]],
        (-1,1)
    )
    assert result[0] == (1,-1)
    assert result[1] == [(-1,1)]


    """ Collision bottom right """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [0,0,1]],
        (1,1)
    )
    assert result[0] == (-1,-1)
    assert result[1] == [(1,1)]



def test_collision_specials():
    result = collision.calc_collision(
        [[1,0,0],
         [0,0,1],
         [0,0,0]],
        (1,-1)
    )
    assert result[0] == (-1,1) , "Can not move to x=0 y=0 as there is a collision"
    assert result[1] == [(1,0)]
