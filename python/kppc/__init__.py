import json
from pathlib import Path
import logging
import logging.handlers


class JSONObject:
    def __init__(self, dic):
        vars(self).update(dic)

settings_path = Path(__file__).resolve().parent.parent.parent / "settings.json"
defaultsettings_path = Path(__file__).resolve().parent.parent.parent / "default-settings.json"

def load_settings(path):
    obj = None
    try:
      with open(path, 'r') as infile:
        obj = json.load(infile, object_hook=JSONObject)
        return obj
    except:
      return None

default = load_settings(defaultsettings_path)
settings = load_settings(settings_path)
if settings is None:
    settings = default
else:
    ask = False
    if settings.General.SettingsVersion is None:
        ask = True
    curversion = [int(x) for x in settings.General.SettingsVersion.split('.')]
    defversion = [int(x) for x in default.General.SettingsVersion.split('.')]
    for i,j in zip(curversion,defversion):
        if j > i:
            ask = True
    if ask:
        pass
        #ask for replacement of option


logfile_path = settings_path.parent / "kppc.log"
logger = logging.getLogger('KPPC')
logger.setLevel(logging.DEBUG)
_fh = logging.handlers.RotatingFileHandler(logfile_path, maxBytes=32768, backupCount=4)
_ch = logging.StreamHandler()
_fh.setLevel(logging.getLevelName(settings.Logging.LogfileLevel[1:][settings.Logging.LogfileLevel[0]]))
_ch.setLevel(logging.getLevelName(settings.Logging.StreamLevel[1:][settings.Logging.StreamLevel[0]]))
_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
_fh.setFormatter(_formatter)
_ch.setFormatter(_formatter)

logger.addHandler(_fh)
logger.addHandler(_ch)