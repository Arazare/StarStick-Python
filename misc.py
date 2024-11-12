import os
import json
import sys
import logging
from datetime import datetime
import hid

env = os.environ['USERPROFILE']
dirpath = env+'\\Documents\\StarStick\\'
path = env+'\\Documents\\StarStick\\config.json'

font = 12

defaultPreset = {'str': '2560x1440 @ 100%','w': 2440,'h':1440,'s':100}

thisSessionDevices = {}
DevicesDropList = []
selectedDevice = 0

root = 0

if os.path.isfile(path):

    with open(path, 'r') as f:
        config = json.load(f)

else:
    if os.path.isdir(dirpath):

        f = open(path, "w")
        config = {}
        json.dump(config, f)
        f.close()
    else:
        os.mkdir(dirpath)
        f = open(path, "w")
        config = {}
        json.dump(config, f)
        f.close()

def getHidDevicesName(mid,pid):
    
    device = hid.device()
    device.open(mid,pid)
    name = device.get_manufacturer_string() + ' ' + device.get_product_string()
    device.close()
    
    return name

def setSetting(name, data):
    config[name]=data
    with open(path, 'w') as f:
        json.dump(config, f)

def saveSettings():
    with open(path, 'w') as f:
        json.dump(config, f)

def getSetting(setting):
    
    if setting in config:
        if config[setting] is not None:
            return config[setting]
    
    config[setting] = None
    
    with open(path, 'w') as f:
        json.dump(config, f)

    return None

def myException(string,e):    
    logging.exception(string, e)

def set_up_logger():
    global fileName
    global logger

    
    logger = logging.getLogger(__name__)
    date_time_obj = datetime.now()
    timestamp_str = date_time_obj.strftime("%d-%b-%Y_%H_%M_%S")

    if os.path.isdir(dirpath)== False:
        os.mkdir(dirpath)

    fileName = dirpath+'\\Log Crash - {}.log'.format(timestamp_str)

    if getSetting('debug') is None:
        setSetting('debug', True)

    elif getSetting('debug') is True:
        logging.basicConfig(
            filename=fileName,
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filemode="w",
            )
    else:
        logging.basicConfig(
            filename=fileName,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filemode="w",
            )
        
    sys.excepthook = my_excepthook

def my_excepthook(exc_type, exc_value, exc_traceback):
     
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    logging.shutdown()  
    
    if os.stat(fileName).st_size == 0 : 
        os.remove(fileName)

    
    
    






















