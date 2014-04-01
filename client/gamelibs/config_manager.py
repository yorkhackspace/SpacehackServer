#spacehack game client config manager utility library

import json

config = []
controlids = []
controldefs = {}
sortedlist = []

#load configuration file
def loadConfig(fileName):
    print "Loading config from " + fileName
    f=open(fileName)
    config=json.loads(f.read())
    f.close()
    #TODO understand this line? Bob, what does the next line do????
    controlids = [control['id'] for control in config['interface']['controls']]
    controlids.sort()
    #Sort the controls into controldefs
    for control in config['interface']['controls']:
        ctrlid = control['id']
        controldefs[ctrlid] = control
    sortedlist = [ctrlid for ctrlid in config['local']['controls']]
    sortedlist.sort()
    return config, controlids, controldefs, sortedlist
