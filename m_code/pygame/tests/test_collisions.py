"""Test common collisions"""
from .context import collision


def test_no_collision():
    """ No collision """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (-1,-1)

def test_collision_x():
    """ Collision top """
    result = collision.calc_collision(
        [[0,1,0],
         [0,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (1,-1)
    
    """ Collision bottom """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [0,1,0]],
        (1,1)
    )
    assert result[0] == (-1,1)


def test_collision_y():

    """ Collision left """
    result = collision.calc_collision(
        [[0,0,0],
         [1,0,0],
         [0,0,0]],
        (1,-1)
    )
    assert result[0] == (1,1)

    """ Collision left """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,1],
         [0,0,0]],
        (1,1)
    )
    assert result[0] == (1,-1)

def test_collision_y_x():

    """ Collision top left """
    result = collision.calc_collision(
        [[0,1,0],
         [1,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (1,1)

    """ Collision top right """
    result = collision.calc_collision(
        [[0,1,0],
         [0,0,1],
         [0,0,0]],
        (-1,1)
    )
    assert result[0] == (1,-1)

    """ Collision bottom left """
    result = collision.calc_collision(
        [[0,0,0],
         [1,0,0],
         [0,1,0]],
        (1,-1)
    )
    assert result[0] == (-1,1)

    """ Collision bottom right """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,1],
         [0,1,0]],
        (1,1)
    )
    assert result[0] == (-1,-1)

def test_collision_corner():

    """ Collision top left """
    result = collision.calc_collision(
        [[1,0,0],
         [0,0,0],
         [0,0,0]],
        (-1,-1)
    )
    assert result[0] == (1,1)

    """ Collision top right """
    result = collision.calc_collision(
        [[0,0,1],
         [0,0,0],
         [0,0,0]],
        (-1,1)
    )
    assert result[0] == (1,-1)

    """ Collision bottom left """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [1,0,0]],
        (1,-1)
    )
    assert result[0] == (-1,1)

    """ Collision bottom right """
    result = collision.calc_collision(
        [[0,0,0],
         [0,0,0],
         [0,0,1]],
        (1,1)
    )
    assert result[0] == (-1,-1)
