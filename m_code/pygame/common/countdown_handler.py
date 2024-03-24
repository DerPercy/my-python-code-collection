class CountdownHandler():
    countdowns = []
    listener = None
        
    def on_tick(self)-> None:
        for cd in self.countdowns:
            cd[1] = cd[1] - 1
            if cd[1] <= 0:
                self.listener(cd[0])
                self.countdowns.remove(cd)
                


    def add_countdown(self,id:str,num_ticks:int) -> None:
        self.countdowns.append([id,num_ticks])
    
    def add_countdown_listener(self,on_countdown_finished):
        #""" on_countdown_finished(countdown_id:str) -> None"""
        self.listener = on_countdown_finished
    