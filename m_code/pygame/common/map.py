from pygame import Surface
import pygame
from icecream import ic
import copy
import json



def load_map_definition(path:str,color_map:dict) -> tuple[dict,dict,dict]:
    json_data = json.load(open(path))
    tile_def = json_data.get("tileDefinition")
    for td in tile_def:
        td[0] = color_map.get(td[0])
    return (json_data.get("map"),tile_def,json_data.get("exits"))
def build_collision_map(        
        map:list[list[int]],
        tile_definitions:list[tuple[any]],
    ):
    collision_map = copy.deepcopy(map)
    for y in range(len(map)):
        for x in range(len(map[y])):
            tile_def = tile_definitions[map[y][x]]
            collision_map[y][x] = tile_def[1]
    return collision_map
def draw_map(
        screen:Surface, 
        options:tuple[int,int,int],
        map:list[list[int]],
        tile_definitions:list[tuple[any]],
        characters: list[tuple[tuple[int,int],str]]
    ):
    """
    tile_definitions
    1. background color
    """
    tile_size = options[2]
    map_start_x = options[0]
    map_start_y = options[1]
    
    for y in range(len(map)):
        for x in range(len(map[y])):
            tile_def = tile_definitions[map[y][x]]

            start_x = map_start_x+x*tile_size
            start_y = map_start_y+y*tile_size
            rect = [start_x,start_y,tile_size,tile_size]
            pygame.draw.rect(screen, tile_def[0], rect)
            if len(tile_def) > 2: # Image
                if not isinstance(tile_def[2],str):
                    for image_source in tile_def[2]:
                        imp = pygame.image.load(image_source).convert_alpha()
                        imp = pygame.transform.scale(imp, (tile_size, tile_size))
                        # Using blit to copy content from one surface to other
                        screen.blit(imp, (start_x, start_y))
                else:
                    image_source = tile_def[2]
                    imp = pygame.image.load(image_source).convert_alpha()
                    imp = pygame.transform.scale(imp, (tile_size, tile_size))
                    # Using blit to copy content from one surface to other
                    screen.blit(imp, (start_x, start_y))
    """Draw characters"""
    for char in characters:
        start_x = map_start_x+char[0][0]*tile_size
        start_y = map_start_y+char[0][1]*tile_size
        imp = pygame.image.load(char[1]).convert_alpha()
        #imp.fill((255,255,255,128), None, pygame.BLEND_RGBA_MULT)
        imp = pygame.transform.scale(imp, (tile_size, tile_size))
        screen.blit(imp, (start_x, start_y))
                        
            