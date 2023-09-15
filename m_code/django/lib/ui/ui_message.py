from attrs import define

@define
class Message:
    """An ui message"""
    content: str