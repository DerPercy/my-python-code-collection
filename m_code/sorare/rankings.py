from .client import Client
from .models.ranking import Ranking


def get_rankings_of_leader_board_slug(client:Client,leader_board_slug:str,number: int) -> list[Ranking]:
    pass