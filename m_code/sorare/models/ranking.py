from attrs import define

@define
class Ranking:
    """A representation of a sorare ranking"""
    id: str
    user_id: str
    position: int
    user_nickname: str = ""
