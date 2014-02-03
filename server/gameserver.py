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
lastgenerated = 0
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
                
#Connect to MQTT (final code should make this a retry loop)
client.on_connect = on_connect
client.on_message = on_message
client.connect(server)

#Main topic subscription point for clients to register their configurations to
client.subscribe('server/register')

#Define a new set of controls for each client for this game round and send it to them.
def defineControls():
    for consoleip in consoles:
        consolesetup={}
        consolesetup['instructions']='Stand by!'
        consolesetup['controls']={}
        for control in console[consoleip]["controls"]:
            ctrlid = control['id']
            consolesetup['controls'][ctrlid]={}
            consolesetup['controls'][ctrlid]['enabled']=1
            consolesetup['controls'][ctrlid]['name']=controls.getControlName(control['width'], 2, 12)
            ctrltype = random.choice([x['type'] for x in control['supported']])
            consolesetup['controls'][ctrlid]['type']=ctrltype
        currentsetup[consoleip]=consolesetup
        client.publish('clients/' + consoleip + '/configure', json.dumps(consolesetup))
    
#Main loop
while(client.loop() == 0): 
    #Every five seconds...
    if time.time()-lastgenerated > 5:
        #Dump another batch of random control names and action
        defineControls()
        lastgenerated = time.time()

#If client.loop() returns non-zero, loop drops out to here.
#Final code should try to reconnect to MQTT and/or networking if so.
