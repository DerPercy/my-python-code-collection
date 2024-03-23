from .trigger_handler import TriggerHandler

def set_trigger(params:list[any], bot,options:dict) -> None:
    """ ["SET_TRIGGER","KEY_1_FOUND"] """
    th:TriggerHandler = options.get("triggerHandler")
    th.add_trigger(params[1])


def remove_if_trigger(params:list[any], bot, options:dict) -> None:
    """ ["REMOVE_IF_TRIGGER", "KEY_1_FOUND"] """
    th:TriggerHandler = options.get("triggerHandler")
    
    if th.has_trigger(params[1]):
        bh = options.get("botHandler")
        bh.remove_bot(bot)