from .trigger_handler import TriggerHandler
from .countdown_handler import CountdownHandler

def set_trigger(params:list[any], bot,options:dict) -> None:
    """ ["SET_TRIGGER","KEY_1_FOUND"] """
    th:TriggerHandler = options.get("triggerHandler")
    th.add_trigger(params[1])

def remove_trigger(params:list[any], bot,options:dict) -> None:
    """ ["REMOVE_TRIGGER","KEY_1_FOUND"] """
    th:TriggerHandler = options.get("triggerHandler")
    th.remove_trigger(params[1])


def remove_if_trigger(params:list[any], bot, options:dict) -> None:
    """ ["REMOVE_IF_TRIGGER", "KEY_1_FOUND"] """
    th:TriggerHandler = options.get("triggerHandler")
    
    if th.has_trigger(params[1]):
        bh = options.get("botHandler")
        bh.remove_bot(bot)

def image_if_trigger(params:list[any], bot, options:dict) -> None:
    """ ["IMAGE_IF_TRIGGER", "rpg/images/map/terrain/truhe_offen.png","CHEST_1_OPEN"] """
    th:TriggerHandler = options.get("triggerHandler")
    if th.has_trigger(params[2]):
        bot[2] = params[1]
def set_image(params:list[any], bot, options:dict) -> None:
    """ ["SET_IMAGE", "rpg/images/map/terrain/truhe_offen.png"] """
    bot[2] = params[1]

def if_trigger_then_trigger(params:list[any], bot, options:dict) -> None:
    """ ["IF_TRIGGER_THEN_TRIGGER","KEY_1_FOUND","CHEST_1_OPEN"] """
    th:TriggerHandler = options.get("triggerHandler")
    if th.has_trigger(params[1]):
        th.add_trigger(params[2])

def add_countdown(params:list[any], bot, options:dict) -> None:
    """ ["ADD_COUNTDOWN","CHEST_1_CLOSE",15] """
    ch:CountdownHandler = options.get("countdownHandler")
    ch.add_countdown(params[1],params[2])
