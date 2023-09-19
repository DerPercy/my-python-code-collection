from attrs import define

@define
class User:
    """A representation of a sorare user"""
    id: str
    nickname: str
