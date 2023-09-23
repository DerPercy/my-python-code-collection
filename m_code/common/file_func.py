import json 
import os

def write_json_to_file(json_data, filename:str):
    try:
        os.makedirs(os.path.dirname(filename))
    except:
        error = 1

    json_object = json.dumps(json_data, indent=4)

    with open(filename, "w") as outfile:
        outfile.write(json_object)

def read_json_from_file(filename:str):
    try:
        f = open(filename)
        return json.load(f)
    except:
        return {}

    