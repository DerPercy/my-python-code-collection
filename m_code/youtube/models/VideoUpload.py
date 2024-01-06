from attrs import define

@define
class VideoUpload:
    """A representation of a youtube video upload"""
    file: str
    keywords: str
    title: str
    category: str
    privacyStatus: str
    description: str
    logging_level:str = "INFO"
    noauth_local_webserver:bool = False
    auth_host_port = [8080, 8090]
    auth_host_name:str = "localhost"