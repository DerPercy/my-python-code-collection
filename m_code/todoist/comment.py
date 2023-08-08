import logging
import re
import json

class ClientComment:
    def __init__(self, content: str, meta_data):
        self.content = content
        self.metadata = meta_data
        
    def get_meta_data(self):
        return self.metadata


def create_todoist_comment_from_meta_data(meta_data:dict) -> str:
    content = "`"+json.dumps(meta_data,indent=2)+"`"
    return content

def create_comment_from_todoist(todoist_comment):
    logging.debug(todoist_comment)
    metadata = get_comment_meta_data(todoist_comment.get("content"))
    return ClientComment(todoist_comment.get("content"), metadata)

def get_comment_meta_data(content):
    """
    Get Metadata of a todoist comment
    Metadata is a codeblock with json
    """
    logging.debug("Check if comment is metadata:"+content)
    x = re.search(r"^[\s]*`(.*)`[\s]*$", content,re.DOTALL) #re.DOTALL to allow line breaks in JSON
    if x is not None:
        data = x.groups()[0]
        logging.debug("comment matches pattern. Result:"+data)
        try:
            datajson = json.loads(data)
            logging.debug("result is json. Is metadata")
            logging.debug(datajson)
            return datajson
        except json.decoder.JSONDecodeError:
            logging.debug('result is no json')
    else:
        logging.debug("comment did not match pattern")
    return None