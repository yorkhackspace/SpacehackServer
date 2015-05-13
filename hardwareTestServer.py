#SpaceHack!  Game server main module
#York Hackspace January 2014
#This runs on a Raspberry Pi

import controls
import mosquitto
import time
import random
import json

lifeDisplay = False
sound = False #Switch this off if you don't have pyGame
debugMode = False

#sleep times
blurbSleep = 4.5

if lifeDisplay:
    import seven_segment_display as sev
    import led_sign as led


def playSound(filename):
    """Play a sound, if enabled"""
    if sound:
        snd = pygame.mixer.Sound("sounds/" + filename)
        snd.play()
        
if sound:
    import pygame
    
#MQTT client to allow publishing
client = mosquitto.Mosquitto("PiServer") #ID shown to the broker
server = "127.0.0.1" #Mosquitto MQTT broker running locally


#Game variables
consoles = [] #all registered consoles
players = [] #all participating players
playerstats = {}
console = {}
currentsetup = {}
currenttimeout = 30.0
lastgenerated = time.time()
numinstructions = 0
gamestate = 'initserver' #initserver, readytostart, waitingforplayers, initgame, setupround, playround, roundover, hyperspace, gameover
warningsound = None

#Show when we've connected
def on_connect(obj, rc):
    """Receive MQTT connection notification"""
    if rc == 0:
        print("Connected to MQTT")
        global gamestate
        gamestate = 'readytostart'
    else:
        print("Failed - return code is " + rc)

#MQTT message arrived
def on_message(obj, msg):
    """Receive and process incoming MQTT published message"""
    nodes = msg.topic.split('/')
    print msg.topic
    global players
    print(gamestate + ' - ' + msg.topic + " - " + str(msg.payload))
    if nodes[0]=='server':
        if nodes[1]=='register':
            config = json.loads(str(msg.payload))
            consoleip = config['ip']
            console[consoleip] = config
            players.append(consoleip)
            
#Define a new set of controls for each client for this game round and send it to them as JSON.
def defineControls():
    """Define a new set of controls for each client for this game round and send it to them as JSON."""
    emergency = controls.getEmergency()
    print(emergency)
    for consoleip in players:
        print("Defining console " + consoleip)
        consolesetup={}
        consolesetup['instructions']=emergency
        consolesetup['timeout'] = currenttimeout
        consolesetup['controls']={}
        #Pay attention to 'enabled' for the control as a whole
        for control in (x for x in console[consoleip]["controls"] if 'enabled' not in x or x['enabled'] == 1):
            ctrlid = control['id']
            consolesetup['controls'][ctrlid]={}
            #Pay attention to 'enabled' attribute
            if 'enabled' in control:
                consolesetup['controls'][ctrlid]['enabled']=control['enabled']
            else:
                consolesetup['controls'][ctrlid]['enabled']=1
            #In case LCDs fail - allow a 'fixed name' we can tape over the LCD
            if 'fixedname' in control:
                consolesetup['controls'][ctrlid]['name'] = str(control['fixedname'])
            else: #Normal case - generate a new control name
                consolesetup['controls'][ctrlid]['name']=controls.getControlName(control['width'], 2, 12)
            #Pay attention to 'enabled' for particular supported mode
            ctrldef = random.choice([x for x in control['supported'] if 'enabled' not in x or x['enabled'] == 1])
            ctrltype = ctrldef['type']
            if ctrltype in ['words', 'verbs']:
                if ctrldef['fixed']:
                    targetrange = ctrldef['list']
                elif 'safe' in ctrldef and ctrldef['safe']:
                    targetrange=controls.safewords
                elif 'list' in ctrldef:
                    if ctrldef['list']=='allcontrolwords':
                        targetrange=controls.allcontrolwords
                    elif ctrldef['list']=='passwd':
                        targetrange=controls.passwd
                    elif ctrldef['list']=='verbs':
                        targetrange=controls.verbs
                    else:
                        targetrange = controls.allcontrolwords
                elif ctrltype=='verbs':
                    targetrange = controls.verbs
                else:
                    targetrange = controls.allcontrolwords
                #Create a predetermined list?
                if not ctrldef['fixed']:
                    reallyfinished = False
                    while not reallyfinished:
                        wordpool = []
                        finished=False
                        while not finished:
                            newword = random.choice(targetrange)
                            if not newword in wordpool:
                                wordpool.append(newword)
                            if len(wordpool) == ctrldef['quantity']:
                                finished=True
                        if ctrldef['quantity'] != 2 or len(wordpool[0]) + len(wordpool[1]) < 14:
                            reallyfinished = True
                    ctrldef['pool'] = sorted(wordpool)
                else:
                    ctrldef['pool'] = ctrldef['list']
            #Pick a starting value
            if 'assignable' in ctrldef and ctrldef['assignable']:
                if ctrltype in ['words', 'verbs']:
                    ctrldef['value']=random.choice(ctrldef['pool'])
                elif ctrltype == 'selector':
                    ctrldef['value'] = random.choice(range(ctrldef['min'],ctrldef['max']+1))
                elif ctrltype == 'colour':
                    ctrldef['value'] = random.choice(ctrldef['values'])
                elif ctrltype == 'toggle':
                    ctrldef['value'] = random.choice(range(2))
                elif ctrltype == 'button':
                    ctrldef['value'] = 0
                elif ctrltype == 'pin':
                    ctrldef['value'] = ''
            consolesetup['controls'][ctrlid]['type'] = ctrltype
            consolesetup['controls'][ctrlid]['definition']=ctrldef
            print("Control " + ctrlid + " is " + ctrldef['type'] + ": " + consolesetup['controls'][ctrlid]['name'])

        currentsetup[consoleip]=consolesetup
        client.publish('clients/' + consoleip + '/configure', json.dumps(consolesetup))


def tellAllPlayers(consolelist, message):
    """Simple routine to broadcast a message to a list or consoles"""
    for consoleip in consolelist:
        client.publish('clients/' + consoleip + '/instructions', str(message))
        
def initGame():
    initRound()

def initRound():
    """Kick off a new round"""
    global numinstructions
    global lastgenerated
    #Dump another batch of random control names and action
    defineControls()
    lastgenerated = time.time()
    
#Main loop

#Connect to MQTT (final code should make this a retry loop)
client.on_connect = on_connect
client.on_message = on_message
client.connect(server)

#Main topic subscription point for clients to register their configurations to
client.subscribe('server/register')

client.publish('server/ready', 'started')

lastReady = time.time()
while(client.loop(0) == 0): 
    if time.time() - lastReady > 3.0:
        lastReady = time.time()
        client.publish('server/ready', 'ready')
    if len(players) > 0 :
        initGame()
        tellAllPlayers(players, "This is a test setup. This is an LCD test instruction.")
        break

#If client.loop() returns non-zero, loop drops out to here.
#Final code should try to reconnect to MQTT and/or networking if so.
