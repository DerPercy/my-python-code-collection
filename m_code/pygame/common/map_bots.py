from icecream import ic
from .trigger_handler import TriggerHandler
from . import bot_behavior

class MapBotHandler():
    bots = []
    #def add_bot(self,position:tuple[int,int],img_path:str, tick_handler:callable = None) -> None:
    #    self.bots.append((
    #        position,
    #        img_path
    #    ))
    
    def remove_bot(self,bot):
        self.bots.remove(bot)
    def init_bots(self,bots:list[dict],trigger_handler:TriggerHandler) -> None:
        #ic(bots)
        if bots != None:
            self.bots = bots
            for bot in self.bots:
                process_actions("ACTIONS",bot,build_options(trigger_handler,self))

    def get_bots_for_map(self) -> list[tuple[tuple[int,int],int,str]]:
        list = []
        for bot in self.bots:
            list.append((bot[0],bot[1],bot[2]))
        return list
    
    def handle_player_collision(self,player_position:tuple[int,int],trigger_handler:TriggerHandler) -> None:
        """Checks, if collision between bots and player occures and trigger actions"""
        for bot in self.bots:
            if bot[0][0] == player_position[0] and bot[0][1] == player_position[1]:
                process_actions("ON_COLLISION",bot,build_options(trigger_handler,self))
                #ic("Collision with bot",bot)
                process_actions("ACTIONS",bot,build_options(trigger_handler,self))
                
        pass

def build_options(trigger_handler:TriggerHandler,bot_handler:MapBotHandler) -> dict:
    return  {
        "triggerHandler": trigger_handler,
        "botHandler": bot_handler
    }

actions = {
    "SET_TRIGGER": bot_behavior.set_trigger,
    "REMOVE_IF_TRIGGER": bot_behavior.remove_if_trigger
}

def process_actions(action_name,bot,options): 
    """
    Process bot actions
    """
    if bot[3].get(action_name) != None:
        for action in bot[3].get(action_name):
            actions[action[0]](action,bot,options)