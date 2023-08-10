from attrs import define
from . import Board

@define
class Category:
    """A representation of a mattermost task"""
    id: str
    name: str
    boards: list[Board] = []