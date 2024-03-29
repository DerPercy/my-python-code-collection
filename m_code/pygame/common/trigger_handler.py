class TriggerHandler():
    trigger_list = []
    listener = None
    def set_trigger_listener(self,on_trigger_function:callable):
        #""" on_trigger_function(trigger_id:str,trigger_action:str) -> None"""
        self.listener = on_trigger_function

    def add_trigger(self,trigger:str):
        self.trigger_list.append(trigger)
        self.listener(trigger,"ADD")

    def remove_trigger(self,trigger:str):
        for tr in self.trigger_list:
            if tr == trigger:
                self.trigger_list.remove(tr)
        self.listener(trigger,"REMOVE")

    def has_trigger(self, trigger:str) -> bool:
        for tr in self.trigger_list:
            if tr == trigger:
                return True
        return False