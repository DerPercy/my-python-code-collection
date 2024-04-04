import random

class Card():
    payload = None
    def __init__(self, card_stack, payload:dict) -> None:
        self.payload = payload
        pass
    def back_to_stack(self):
        pass
    
    def get_payload(self) -> dict:
        return self.payload


class CardStack():  
    cards = None

    def __init__(self) -> None:
        self.cards = []
    pass
    def add_card(self,card_data:dict,number:int = 1) -> list[Card]:
        ret_cards = []
        for _ in range(number):
            card = Card(self,card_data)
            ret_cards.append(card)
            self.cards.append(card)
        return ret_cards

    def shuffle_stack(self) -> None:
        random.shuffle(self.cards)

    def get_stack_size(self) -> int:
        return len(self.cards)

    def draw_top_card(self) -> Card:
        return self.cards.pop()