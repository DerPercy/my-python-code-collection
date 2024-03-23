from common.map import draw_map, build_collision_map,load_map_definition
from common.collision import create_surroundings,calc_collision
from common.map_bots import MapBotHandler
from common.trigger_handler import TriggerHandler
import pygame
from icecream import ic



screen = pygame.display.set_mode((1800, 840))
clock = pygame.time.Clock()


# genutzte Farben
GRUEN   = (   0, 199,   0)
BLAU    = (   0,   0, 100)
SCHWARZ = (   0,   0,   0)
WEISS   = ( 255, 255, 255)
color_map = {
    "GRUEN": (   0, 199,   0),
    "BLAU" : (   0,   0, 100)
}

# map layout
map_start_x = 0
map_start_y = 0
map_tile_size = 64

(map,tile_def,exits,bots) = load_map_definition("./rpg/maps/entry.json",color_map)


spieler_1_x = 26
spieler_1_y = 1
spielfigur_1_bewegung_x = 0
spielfigur_1_bewegung_y = 0
spieler_2_x = 3
spieler_2_y = 0
spielfigur_2_bewegung_x = 0
spielfigur_2_bewegung_y = 0

bot_handler = MapBotHandler()
trigger_handler = TriggerHandler()
bot_handler.init_bots(bots,trigger_handler)

chars = []

def check_exits(position:tuple[int,int]) -> dict: # returns exit or none
    for ext in exits:
        if ext[0][0] == position[0] and ext[0][1] == position[1]:
            return ext
    return None
    

game_active = True
while game_active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_active = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                spielfigur_1_bewegung_x = -1
            elif event.key == pygame.K_RIGHT:
                spielfigur_1_bewegung_x = 1  
            elif event.key == pygame.K_UP:
                spielfigur_1_bewegung_y = -1  
            elif event.key == pygame.K_DOWN:
                spielfigur_1_bewegung_y = 1
            elif event.key == pygame.K_a:
                spielfigur_2_bewegung_x = -1
            elif event.key == pygame.K_d:
                spielfigur_2_bewegung_x = 1  
            elif event.key == pygame.K_w:
                spielfigur_2_bewegung_y = -1  
            elif event.key == pygame.K_s:
                spielfigur_2_bewegung_y = 1
            
            elif event.key == pygame.K_SPACE:
                #bots.add_bot((spieler_2_x,spieler_2_y),"rpg/images/map/terrain/poo.png")  
                pass
    
    # check player movement
    coll_map = build_collision_map(map,tile_def,chars)

    # Player 1
    bot_handler.handle_player_collision((spieler_1_x + spielfigur_1_bewegung_x,spieler_1_y + spielfigur_1_bewegung_y),trigger_handler)
    surroundings = create_surroundings(coll_map,(spieler_1_x,spieler_1_y))
    coll_movement = calc_collision(surroundings,(spielfigur_1_bewegung_x,spielfigur_1_bewegung_y),"STAY")
    spielfigur_1_bewegung_x = coll_movement[0][0]
    spielfigur_1_bewegung_y = coll_movement[0][1]

    spieler_1_x = spieler_1_x + spielfigur_1_bewegung_x
    spieler_1_y = spieler_1_y + spielfigur_1_bewegung_y

    # Player 2
    surroundings = create_surroundings(coll_map,(spieler_2_x,spieler_2_y))
    coll_movement = calc_collision(surroundings,(spielfigur_2_bewegung_x,spielfigur_2_bewegung_y),"STAY")
    spielfigur_2_bewegung_x = coll_movement[0][0]
    spielfigur_2_bewegung_y = coll_movement[0][1]
    spieler_2_x = spieler_2_x + spielfigur_2_bewegung_x
    spieler_2_y = spieler_2_y + spielfigur_2_bewegung_y

    # Check exits
    act_exit = check_exits((spieler_1_x,spieler_1_y))
    if act_exit != None:
        (map,tile_def,exits,bots) = load_map_definition(act_exit[1],color_map)
        bot_handler.init_bots(bots,trigger_handler)
        (spieler_1_x,spieler_1_y) = act_exit[2]
        (spieler_2_x,spieler_2_y) = act_exit[2]
    chars = []
    chars.extend(bot_handler.get_bots_for_map())
    chars.append(((spieler_1_x,spieler_1_y),0,"rpg/images/map/terrain/girl.png"))
    chars.append(((spieler_2_x,spieler_2_y),0,"rpg/images/map/terrain/cow.png"))
    draw_map(screen,(map_start_x,map_start_y,map_tile_size),map,tile_def,chars)

    pygame.display.flip()

    # Refresh-Zeiten festlegen
    clock.tick(10)
    spielfigur_1_bewegung_x = 0
    spielfigur_1_bewegung_y = 0
    spielfigur_2_bewegung_x = 0
    spielfigur_2_bewegung_y = 0


pygame.quit()
exit()