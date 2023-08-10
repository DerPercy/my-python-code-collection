from attrs import define

@define
class Team:
    """A representation of a mattermost team"""
    id: str