from jinja2 import Environment, FileSystemLoader
import os

def get_environment() -> Environment:
    file_path = os.path.dirname(__file__)
    places = []
    places.append(file_path+"/templates/")
    places.append("templates/")
    return Environment(loader=FileSystemLoader(places))