class TriggerHandler():
    trigger_list = []
    
    def add_trigger(self,trigger:str):
        self.trigger_list.append(trigger)

    def remove_trigger(self,trigger:str):
        print("remove trigger"+trigger)
        for tr in self.trigger_list:
            if tr == trigger:
                self.trigger_list.remove(tr)

    def has_trigger(self, trigger:str) -> bool:
        for tr in self.trigger_list:
            if tr == trigger:
                return True
        return False