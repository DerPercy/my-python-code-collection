import logging
import re
import json

class ClientComment:
    pass


def create_comment_from_todoist(todoist_comment):
    print(todoist_comment)
    get_comment_meta_data(todoist_comment.get("content"))
    return ClientComment()

def get_comment_meta_data(content):
    """
    """
    print(content)
    x = re.search(r"^[\s]*`(.*)`[\s]*$", content)
    if x != None:
        data = x.groups()[0]
        logging.debug(data)
        try:
            datajson = json.loads(data)
            logging.debug(datajson)
        except json.decoder.JSONDecodeError:
            logging.debug('No JSON')
    return "To implement"