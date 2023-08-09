from attrs import define

@define
class Task:
    """A representation of a mattermost task"""
    title: str
    project: str
    id: str
    createAt: int
    updateAt: int
    deleteAt: int
    icon: str = ""
    