class CountdownHandler():
    countdowns = []
    listener = None
        
    def on_tick(self)-> None:
        for cd in self.countdowns:
            cd[0] = cd[0] - 1
            if cd[0] <= 0:
                self.listener(cd[1])
                self.countdowns.remove(cd)
                


    def add_countdown(self,num_ticks:int,data:dict) -> None:
        self.countdowns.append([num_ticks,data])
    
    def add_countdown_listener(self,on_countdown_finished):
        #""" on_countdown_finished(data:dict) -> None"""
        self.listener = on_countdown_finished
    