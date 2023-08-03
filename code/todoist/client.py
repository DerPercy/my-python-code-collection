from todoist_api_python.api import TodoistAPI

class ClientTask():
    pass
class ClientProject():
    def get_task_by_external_id(self, id:str) -> ClientTask:
        #raise ClientException('Task with id '+id+' not found')
        raise ClientException('get_task_by_external_id  not implemented yet')


class Client:

    def __init__(self, options=None):
        self.api = TodoistAPI(options.get('apiKeyClient',None))
        pass

    def get_project(self, name: str ) -> ClientProject:
        projects = self.api.get_projects();
        for project in projects:
            print(project)
            if project.name == name:
                return conv_todoist_proj_to_client_proj(project)
        raise ClientException('Project with name '+name+' not found')
    

def conv_todoist_proj_to_client_proj(todoist_proj):
    return ClientProject()



class ClientException(Exception):
    pass