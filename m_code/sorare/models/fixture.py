from attrs import define

@define
class Fixture:
    """A representation of a sorare fixture"""
    slug: str
    aasmState: str 