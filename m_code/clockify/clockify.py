import re

def parse_description(description:str):
    ticket = ""
    result = re.search(r"([USTB]{1,2}[\d]*):[!\s]*(.*)", description)
    if result == None:
        desc = description
    else:
        if len(result.groups()) > 1:
            ticket = result.group(1)
            desc = result.group(2)
        else:
            desc = description
    #([USTB]{1,2}[\d]*):[!\s]*(.*)
                 
    return {
        "ticket": ticket,
        "description": desc
    }