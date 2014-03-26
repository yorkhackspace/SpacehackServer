# SpaceHack! Game client main module
#York Hackspace January 2014
#This runs on a Beaglebone Black

import sys
import mosquitto
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC

from Adafruit_CharLCD import Adafruit_CharLCD
from NokiaLCD import NokiaLCD
import gaugette.rotary_encoder as rotary
import Keypad_BBB
from collections import OrderedDict
import commands
import json
import time

#import game libraries
sys.path.append('./gamelibs')
sys.path.append('./controls')
import config_manager
import lcd_manager
import control_manager

#Vars
roundconfig = {}
keypad = None
hasregistered = False
timeoutstarted = 0.0
timeoutdisplayblocks = 0

#Who am I? Get my ip address
ipaddress = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]

#configuration. Load the config and get various dictionaries and arrays back
configFileName = 'game-' + ipaddress +'.config'
config, controlids, controldefs, sortedlist = config_manager.loadConfig(configFileName)

#initialise all of the LCDs and return a list of LCD objects
lcd = lcd_manager.initLCDs(sortedlist, config)

#initialise all controls
control_manager.initialiseControls(config, sortedlist, lcd)
            
#MQTT client
client = mosquitto.Mosquitto("Game-" + ipaddress) #client ID
print config['local']
server = config['local']['server']
        
#MQTT message arrived
def on_message(mosq, obj, msg):
    """Process incoming MQTT message"""
    print(msg.topic + " - " + str(msg.payload))
    nodes = msg.topic.split('/')
    global timeoutstarted
    global timeoutdisplayblocks
    if nodes[0]=='clients':
        if nodes[2]=='configure':
            processRoundConfig(str(msg.payload))
            timeoutstarted = 0.0
            timeoutdisplayblocks = 0
        elif nodes[2] == 'instructions':
            lcd_manager.display(str(msg.payload), 20, "0")
            #start timer?
            if 'timeout' in roundconfig and roundconfig['timeout'] > 0.0:
                timeoutdisplayblocks = 0
                timeoutstarted = time.time()
        elif nodes[2] in controlids:
            ctrlid = nodes[2]
            if nodes[3] == 'enabled':
                roundconfig['controls'][ctrlid]['enabled'] = False
                #switch it off?
                lcd_manager.display(" ", config['local']['controls'][ctrlid]['display'], ctrlid)
            elif nodes[3] == 'name':
                lcd_manager.display(str(msg.payload), config['local']['controls'][ctrlid]['display'], ctrlid)
    elif nodes[0] == 'server':
        if nodes[1] == 'ready':
            mess = str(msg.payload)
            if mess == 'started':
                client.publish("server/register", json.dumps(config['interface']))
            elif mess == 'ready':
                global hasregistered
                if not hasregistered:
                    hasregistered = True
                    client.publish("server/register", json.dumps(config['interface']))
                    
      
#Process an incoming config for a round
def processRoundConfig(roundconfigstring):
    """Process an incoming config for a round"""
    x = json.loads(roundconfigstring)
    for key in x.keys():
        roundconfig[key] = x[key]
    lcd_manager.display(roundconfig['instructions'], 20, "0")
    for ctrlid in controlids:
        roundsetup = roundconfig['controls'][ctrlid]
        controlsetup = config['local']['controls'][ctrlid]
        lcd_manager.display(roundsetup['name'], controlsetup['display']['width'], ctrlid)
        if 'definition' in roundsetup and roundsetup['enabled']:
            ctrltype = roundsetup['type']
            ctrldef = roundsetup['definition']
            #there's more to setup of course
            #hardwaretype = config['local']['controls'][ctrlid]['hardware']
            #if hardwaretype == 'phonestylemenu':
            #    if ctrltype == 'toggle':
            #        displayButtonsLine("Off", "On", ctrlid)
            #    elif ctrltype == 'verbs':
            #        displayButtonsLine(ctrldef['pool'][0], ctrldef['pool'][1], ctrlid)
            #    else:
            #        displayButtonsLine("<<<<", ">>>>", ctrlid)
            #elif hardwaretype == 'combo7SegColourRotary':
            #    if ctrltype == 'button':
            #        displayDigits("PUSH")
            if 'value' in ctrldef:
                control_manager.processControlValueAssignment(roundconfig, ctrldef['value'], ctrlid, True)

#Setup MQTT
client.on_message = on_message
client.connect(server)
subsbase = "clients/" + ipaddress + "/"
client.subscribe(subsbase + "configure")
client.subscribe(subsbase + "instructions")
client.subscribe("server/ready")

for controlid in [x['id'] for x in config['interface']['controls']]:
    client.subscribe(subsbase + str(controlid) + '/name')
    client.subscribe(subsbase + str(controlid) + '/enabled')
    
#Main loop
while(client.loop(0) == 0):
    control_manager.pollControls(config, roundconfig, controlids, client, ipaddress)
    lcd_manager.displayTimer(timeoutstarted, timeoutdisplayblocks, roundconfig['timeout'])
    
