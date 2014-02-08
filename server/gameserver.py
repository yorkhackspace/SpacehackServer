#SpaceHack!  Game server main module
#York Hackspace January 2014
#This runs on a Raspberry Pi

import controls
import mosquitto
import time
import random
import pygame
import json

#MQTT client to allow publishing
client = mosquitto.Mosquitto("PiServer") #ID shown to the broker
server = "127.0.0.1" #Mosquitto MQTT broker running locally

#Pygame for sounds
pygame.init()
pygame.mixer.init()

#Game variables
consoles = []
console = {}
currentsetup = {}

#Show when we've connected
def on_connect(mosq, obj, rc):
    if rc == 0:
        print("Connected to MQTT")
    else:
        print("Failed - return code is " + rc)

#MQTT message arrived
def on_message(mosq, obj, msg):
    nodes = msg.topic.split('/')
    print(msg.topic + " - " + str(msg.payload))
    if nodes[0]=='server':
        if nodes[1]=='register':
            config = json.loads(str(msg.payload))
            consoleip = config['ip']
            console[consoleip] = config
            if not consoleip in consoles:
                consoles.append(consoleip)
            #set console up for game start
            consolesetup = {}
            consolesetup['instructions'] = 'To start new game, all players push and hold button'
            consolesetup['controls'] = {}
            print(config['controls'])
            for control in config['controls']:
                ctrlid = control['id']
                consolesetup['controls'][ctrlid]={}
                if 'gamestart' in control:
                    consolesetup['controls'][ctrlid]['type'] = 'button'
                    consolesetup['controls'][ctrlid]['enabled'] = 1
                    consolesetup['controls'][ctrlid]['name'] = "Push and hold to start"
                else:
                    consolesetup['controls'][ctrlid]['type'] = 'inactive'
                    consolesetup['controls'][ctrlid]['enabled'] = 0
                    consolesetup['controls'][ctrlid]['name'] = ""
            client.publish('clients/' + consoleip + '/configure', json.dumps(consolesetup))
            currentsetup[consoleip] = consolesetup
            #Temp for now
            defineControls()
                
#Define a new set of controls for each client for this game round and send it to them.
def defineControls():
    for consoleip in consoles:
        print("Defining console " + consoleip)
        consolesetup={}
        consolesetup['instructions']='Stand by!'
        consolesetup['controls']={}
        for control in console[consoleip]["controls"]:
            ctrlid = control['id']
            consolesetup['controls'][ctrlid]={}
            consolesetup['controls'][ctrlid]['enabled']=1
            consolesetup['controls'][ctrlid]['name']=controls.getControlName(control['width'], 2, 12)
            ctrldef = random.choice([x for x in control['supported']])
            consolesetup['controls'][ctrlid]['type']=ctrldef['type']
            consolesetup['controls'][ctrlid]['definition']=ctrldef
            print("Control " + ctrlid + " is " + ctrldef['type'] + ": " + consolesetup['controls'][ctrlid]['name'])
        currentsetup[consoleip]=consolesetup
        client.publish('clients/' + consoleip + '/configure', json.dumps(consolesetup))

#Get a choice from a range that isn't the same as the old value
def getChoice(choicerange, oldval):
    finished=False
    while not finished:
        retval = random.choice(choicerange)
        if retval != oldval:
            finished=True
    return retval

#Pick a new instruction to display on a given console
def pickNewTarget(consoleip):
    #pick a random console and random control from that console
    targetconsole = random.choice(consoles)
    targetsetup = currentsetup[targetconsole]
    targetctrlid = random.choice(targetsetup['controls'].keys())
    targetcontrol = targetsetup['controls'][targetctrlid]
    targetname = targetcontrol['name']
    targetdef = targetcontrol['definition']
    targetinstruction = ''
    #pick a new target based on the control type and current value
    ctrltype = targetcontrol['type']
    if 'value' in targetcontrol:
        curval = targetcontrol['value']
    else:
        curval=''
    if ctrltype == 'button':
        targetval=1
        targetinstruction = controls.getButtonAction(targetname)
    elif ctrltype == 'toggle':
        if curval == 0:
            targetval=1
        else:
            targetval=0
        targetinstruction = controls.getToggleAction(targetname, targetval)
    elif ctrltype == 'selector':
        targetrange = range(targetdef['min'],targetdef['max']+1)
        targetval = getChoice(targetrange, curval)
        targetinstruction = controls.getSelectorAction(targetname, targetrange, targetval, curval)
    elif ctrltype == 'colour':
        targetrange = targetdef['values']
        targetval = getChoice(targetrange, curval)
        targetinstruction = controls.getColourAction(targetname, targetval)
    elif ctrltype == 'words':
        if targetdef['fixed']:
            targetrange = targetdef['list']
        elif targetdef['safe']:
            targetrange=controls.safewords
        elif 'list' in targetdef:
            if targetdef['list']=='allcontrolwords':
                targetrange=controls.allcontrolwords
            elif targetdef['list']=='passwd':
                targetrange=controls.passwd
                targetinstruction = controls.getPasswdAction(targetname, getChoice(targetrange))
            elif targetdef['list']=='verbs':
                targetrange=controls.verbs
                targetinstruction = controls.getVarbAction(targetname, getChoice(targetrange))
            else:
                targetrange = controls.allcontrolwords
        else:
            targetrange=controls.allcontrolwords
        if targetinstruction=='':
            targetval=getChoice(targetrange, curval)
            targetinstruction = controls.getWordAction(targetname, targetval)
    elif ctrltype == 'verbs':
        if targetdef['fixed']:
            targetrange = targetdef['list']
        else:
            targetrange = controls.verbs
        targetval=getChoice(targetrange, curval)
        targetinstruction = controls.getVerbListAction(targetname, targetval)
    elif ctrltype == 'pin':
        finished=False
        while not finished:
            newpin=''
            for i in range(4):
                newpin += str(random.choice(range(10)))
            if newpin != curval:
                finished=True
        targetval=newpin
        targetinstruction = controls.getPinAction(targetname, targetval)
    else:
        print("Unhandled type: " + ctrltype)
    #Now we have targetval and targetinstruction for this consoleip, store and publish it
    console[consoleip]['instructions']=targetinstruction
    console[consoleip]['target']={"console": targetconsole, "control": targetctrlid,
                                  "value": targetval}
    print("Instruction: " + consoleip + '/' + targetctrlid + ' - ' + str(targetinstruction))
    client.publish('clients/' + consoleip + '/instructions', targetinstruction)
    
#Main loop

#Connect to MQTT (final code should make this a retry loop)
client.on_connect = on_connect
client.on_message = on_message
client.connect(server)

#Main topic subscription point for clients to register their configurations to
client.subscribe('server/register')

lastgenerated = 0
numinstructions =0
while(client.loop() == 0): 
    #Every five seconds...
    if time.time()-lastgenerated > 5:
        if numinstructions == 0:
            #Dump another batch of random control names and action
            print("calling define")
            defineControls()
            numinstructions = 5
        else:
            #print("calling pick")
            for consoleip in consoles:
                pickNewTarget(consoleip)
            numinstructions -= 1
        lastgenerated = time.time()

#If client.loop() returns non-zero, loop drops out to here.
#Final code should try to reconnect to MQTT and/or networking if so.
