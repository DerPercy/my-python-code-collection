from attrs import define

@define
class Board:
    """A representation of a mattermost board"""
    id: str
    category_dict: dict
    