from icecream import ic

class MapBotHandler():
    bots = []
    def add_bot(self,position:tuple[int,int],img_path:str, tick_handler:callable = None) -> None:
        self.bots.append((
            position,
            img_path
        ))
        

    def get_bots_for_map(self) -> list[tuple[tuple[int,int],str]]:
        list = []
        list.extend(self.bots)
        return list