from attrs import define
import logging

@define
class ThumbnailUpload:
    """A representation of a youtube video upload"""
    file: str
    videoId: str
    logging_level:str = "INFO"
    noauth_local_webserver:bool = False
    auth_host_port = [8080, 8090]
    auth_host_name:str = "localhost"

