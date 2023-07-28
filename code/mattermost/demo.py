from mattermostdriver import Driver
import os
import requests


print(os.getenv('MATTERMOST_URL'))
foo = Driver({ 
    'url': os.getenv('MATTERMOST_URL'),
    'token': os.getenv('MATTERMOST_TOKEN'),
    'port': 443,
    'debug': False
})

foo.login()
print(foo.client._token)
#data = foo.client.make_request('get', '/../../plugins/focalboard/api/v2/teams', options=None, params=None, data=None, files=None, basepath=None)
#data = foo.client.make_request('get', '/../../boards/dashboard', options=None, params=None, data=None, files=None, basepath=None)
#print(data.content)
#for c in data.cookies:
#   print(c.name, c.value)
headers = foo.client.auth_header()

headers["X-Requested-With"] = "XMLHttpRequest"

r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v1/workspaces", headers=headers)
print(r.json())
workspaces = r.json()

for workspace in workspaces:
    if workspace.get("boardCount",0) > 0:
        wsID = workspace.get("id")
        r = requests.get("https://"+os.getenv('MATTERMOST_URL')+"/plugins/focalboard/api/v1/workspaces/"+wsID+"/blocks?all=true", headers=headers)
        print(r.content)
