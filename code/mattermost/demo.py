import os
#from . import Client
import client
import json

cl = client.Client({
    'url': os.getenv('MATTERMOST_URL'),
    'token': os.getenv('MATTERMOST_TOKEN'),
    'port': 443
})

print(json.dumps(cl.getTasks(),indent=2))