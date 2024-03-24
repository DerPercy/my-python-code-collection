from icecream import ic
from .trigger_handler import TriggerHandler
from .countdown_handler import CountdownHandler
from . import bot_behavior
from attrs import define

@define
class MapBotHandlerEnvironment():
    th: TriggerHandler
    ch: CountdownHandler

class MapBotHandler():
    bots = []
    #def add_bot(self,position:tuple[int,int],img_path:str, tick_handler:callable = None) -> None:
    #    self.bots.append((
    #        position,
    #        img_path
    #    ))
    
    def remove_bot(self,bot):
        self.bots.remove(bot)
    def init_bots(self,bots:list[dict],env:MapBotHandlerEnvironment) -> None:
        #ic(bots)
        if bots != None:
            self.bots = bots
            for bot in self.bots:
                process_actions("ACTIONS",bot,build_options(env,self))

    def get_bots_for_map(self) -> list[tuple[tuple[int,int],int,str]]:
        list = []
        for bot in self.bots:
            list.append((bot[0],bot[1],bot[2]))
        return list
    
    def handle_player_collision(self,player_position:tuple[int,int],player_params:dict, env:MapBotHandlerEnvironment) -> None:
        """Checks, if collision between bots and player occures and trigger actions"""
        for bot in self.bots:
            if bot[0][0] == player_position[0] and bot[0][1] == player_position[1]:
                process_actions("ON_COLLISION",bot,build_options(env,self))
                #ic("Collision with bot",bot)
                process_actions("ACTIONS",bot,build_options(env,self))
                
        pass

def build_options(env:MapBotHandlerEnvironment,bot_handler:MapBotHandler) -> dict:
    return  {
        "triggerHandler": env.th,
        "countdownHandler": env.ch,
        "botHandler": bot_handler
    }

actions = {
    "SET_TRIGGER": bot_behavior.set_trigger,
    "REMOVE_IF_TRIGGER": bot_behavior.remove_if_trigger,
    "IMAGE_IF_TRIGGER": bot_behavior.image_if_trigger,
    "IF_TRIGGER_THEN_TRIGGER": bot_behavior.if_trigger_then_trigger
}

def process_actions(action_name,bot,options): 
    """
    Process bot actions
    """
    if bot[3].get(action_name) != None:
        for action in bot[3].get(action_name):
            actions[action[0]](action,bot,options)