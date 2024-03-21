"""
Collision calculations
"""
from icecream import ic

def calc_collision(surroundings:list[list[int]],movement:tuple[int,int]) -> tuple[tuple[int,int],list[tuple[int,int]]]:
    """
    Calculates the moving direction based on the surronding objects
    surroundings: 3x3 map of the surronding objects (center: current position)
    movement: current movement(x,y)

    returns:
    tuple
    - new movement(x,y)
    - list of points, which collided
    """
    collision_detected = False
    result_movement = (movement[0],movement[1])
    if surroundings[1 + movement[0]][1] != 0:
        # switch x-movement
        result_movement = (result_movement[0] * -1,result_movement[1])
        collision_detected = True
    
    if surroundings[1][1+movement[1]] != 0:
        # switch y-movement
        result_movement = (result_movement[0],result_movement[1]*-1)
        collision_detected = True
    
    if collision_detected == False:
        # till now no collision: test corner
        if surroundings[1+movement[0]][1+movement[1]] != 0:
            result_movement = (result_movement[0]*-1,result_movement[1]*-1)
    
    return (result_movement,[])


def create_surroundings(map:list[list[int]],position:tuple[int,int]) -> list[list[int]]:
    """
    Create a surrounding map (3x3) based on the map and borders
    """
    steps = [-1,0,1]
    result = [[0,0,0],
              [0,0,0],
              [0,0,0]]
    for x in steps:
        for y in steps:
            if is_out_of_bounds(map,position,(x,y)):
                result[1+x][1+y] = 1 # out of bounds 
            else:
                result[1+x][1+y] = map[position[0]+x][position[1]+y]

    return result

def is_out_of_bounds(map:list[list[int]],position:tuple[int,int],movement:tuple[int,int]) -> bool:
    if position[0]+movement[0] < 0:
        return True
    if position[1]+movement[1] < 0:
        return True
    if position[0]+movement[0] >= len(map):
        return True 
    if position[1]+movement[1] >= len(map[position[0]]):
        return True 
    return False