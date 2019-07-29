import json
import os
from pathlib import Path

class JSONObject:
    def __init__(self, dic):
        vars(self).update(dic)


settings_path = Path(__file__).resolve().parent.parent.parent / "settings.json"

with open(settings_path, 'r') as infile:
    settings = json.load(infile, object_hook=JSONObject)
