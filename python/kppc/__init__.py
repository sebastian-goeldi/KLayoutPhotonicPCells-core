import json
from pathlib import Path
import logging
import logging.handlers


class JSONObject:
    def __init__(self, dic):
        vars(self).update(dic)

settings_path = Path(__file__).resolve().parent.parent.parent / "settings.json"
defaultsettings_path = Path(__file__).resolve().parent.parent.parent / "default-settings.json"

def load_settings():
    global settings
    with open(settings_path, 'r') as infile:
        settings = json.load(infile, object_hook=JSONObject)

load_settings()

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