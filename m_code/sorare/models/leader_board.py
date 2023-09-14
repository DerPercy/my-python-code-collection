from attrs import define

@define
class LeaderBoard:
    """A representation of a sorare leaderBoard"""
    slug: str
    rarity:str