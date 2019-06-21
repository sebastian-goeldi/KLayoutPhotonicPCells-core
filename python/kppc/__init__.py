import json
import os


class JSONObject:
    def __init__(self, dic):
        vars(self).update(dic)


dir_path = os.path.dirname(os.path.realpath(__file__))

with open(dir_path + '/settings.json', 'r') as infile:
    settings = json.load(infile, object_hook=JSONObject)
