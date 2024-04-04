import json
from icecream import ic
from card_stack import CardStack

"""
Actions
"""
def get_go_action():
    def action_go(engine:RPGCardEngine,commands:list[str]) -> tuple[RPGActionResult,callable]:
        #ic(commands)
        if len(commands) == 0:
            return(RPGActionResult("Wohin möchtest du gehen"),action_go)
        engine.player_location = engine.locations[engine.player_location].get("exits")[int(commands[0])-1]
        engine.current_action_handler = None 
        engine.use_action_point(1)
        return (engine.do_action_by_text("look"),None)
    return action_go


class RPGActionResult:
    result_text = None
    def __init__(self,res_text:str):
        self.result_text = res_text

    def result_to_text(self)-> str:
        return self.result_text

class RPGCardEngine:

    player_location = None
    player_action_points = None
    player_action_points_current = None
    locations = None
    action_handler = None
    current_action_handler = None

    def __init__(self,config_source:str):
        json_data = json.load(open(config_source))
        init_locations(self,json_data)
        self.player_location = json_data.get("init").get('STARTLOCATION')
        self.player_action_points = json_data.get("init").get('player').get('actionPoints')
        self.player_action_points_current = self.player_action_points
        self.locations = json_data.get("locations")
        self.action_handler = {}
        self.register_action(["g","gehe","go"],get_go_action())
        #ic(json_data)    


    def do_action_by_text(self,action:str) -> RPGActionResult:
        action_list = action.split()
        #ic(self.action_handler)
        handler = None
        result = None
        if self.current_action_handler != None:
            (result,handler) = self.current_action_handler(self,action_list)
        elif self.action_handler.get(action_list[0]) != None:
            (result,handler) = self.action_handler.get(action_list[0])(self,action_list[1:])
        self.current_action_handler = handler
        if result != None:
            return result
        if action_list[0] == "look":
            result = self.locations[self.player_location].get("description")
            result += "\nAusgänge:"
            indx = 1
            for exit in self.locations[self.player_location].get("exits"):
                result += "\n"+str(indx)+") " + self.locations[exit].get("description")
                indx = indx + 1
            return RPGActionResult(result)
        #ic(self.player_location)
        return RPGActionResult("Unbekannte Aktion")
    
    def handle_player_round_end(self):
        print("Runde beendet")
        self.player_action_points_current = self.player_action_points

    def register_action(self,commands:list[str],action:callable) -> None:
        for comm in commands:
            self.action_handler[comm] = action
        


    def use_action_point(self,points:int = 1):
        self.player_action_points_current = self.player_action_points_current - points
        #ic(self.player_action_points_current)
        if self.player_action_points_current <= 0:
            self.handle_player_round_end()



def init_locations(engine:RPGCardEngine, config_data:dict) -> None:
    location_data = config_data.get("locations")
    collect_card_data = config_data.get("cards",{}).get("collect",{})
    for location_key in location_data:
        loc_data = location_data[location_key]
        # Handle collection info
        collect_info_list =  loc_data.get("cards",{}).get("collect",[])
        if len(collect_info_list) > 0:
            card_stack = CardStack()
            for collect_info in collect_info_list:
                card_stack.add_card(collect_card_data.get(collect_info[0]),collect_info[1])
            card_stack.shuffle_stack()
            while card_stack.get_stack_size() > 0: 
                #ic(card_stack.draw_top_card().get_payload())
                pass
            
    pass
