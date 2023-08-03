from todoist_api_python.api import TodoistAPI, Project
from .project import ClientProject
from .exception import ClientException




class Client:

    def __init__(self, options=None):
        self.api = TodoistAPI(options.get('apiKeyClient',None))
        pass

    def get_project(self, name: str ) -> ClientProject:
        projects = self.api.get_projects();
        for project in projects:
            print(project)
            if project.name == name:
                return conv_todoist_proj_to_client_proj(project, self.api)
        raise ClientException('Project with name '+name+' not found')
    

def conv_todoist_proj_to_client_proj(todoist_proj: Project, api: TodoistAPI):
    return ClientProject(api,todoist_proj)



