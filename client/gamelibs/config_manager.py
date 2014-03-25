import json

config = []
controlids = []
controldefs = {}

#load configuration file
def loadConfig(fileName)
    f=open(fileName)
    config=json.loads(f.read())
    f.close()
    #TODO understand this line? Bob, what does this line do????
    controlids = [control['id'] for control in config['interface']['controls']]
    controlids.sort()
    #Sort the controls into controldefs
    for control in config['interface']['controls']:
        ctrlid = control['id']
        controldefs[ctrlid] = control
