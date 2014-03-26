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

#Who am I? Get my ip address
ipaddress = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]

#configuration. Load the config and get various dictionaries and arrays back
configFileName = 'game-' + ipaddress +'.config'
config, controlids, controldefs, sortedlist = config_manager.loadConfig(configFileName)

#initialise all of the LCDs and return a list of LCD objects
lcd = lcd_manager.initLCDs(sortedlist, config)

#Vars
roundconfig = {}
bar = []
keypad = None
hasregistered = False
timeoutstarted = 0.0
timeoutdisplayblocks = 0

#initialise all controls
control_manager.initialiseControls(config, sortedlist)
            
#MQTT client
client = mosquitto.Mosquitto("Game-" + ipaddress) #client ID
print config['local']
server = config['local']['server']

#Pretty print to the LCDs taking into account width
def display(message, width, ctrlid):
    """Pretty print to the LCDs taking into account width"""
    words = message.split(" ")
    line = ""
    pos=0
    lcd[ctrlid].clear()
    for word in words:
        if len(line) + len(word) > width:
            lcd[ctrlid].setCursor(0, pos)
            lcd[ctrlid].message(line.rstrip() + '\n')
            line = word + " "
            pos += 1
        else:
            line += word + " "
    lcd[ctrlid].setCursor(0, pos)
    lcd[ctrlid].message(line.rstrip())

#Display words on the left and right sides of the bottom row, for Nokia displays
def displayButtonsLine(leftstr, rightstr, ctrlid):
    """Display words on the left and right sides of the bottom row, for Nokia displays"""
    ctrldef = config['local']['controls'][ctrlid]['display']
    combinedstr = leftstr + " "*(ctrldef['width'] - len(leftstr) - len(rightstr)) + rightstr
    lcd[ctrlid].setCursor(0, ctrldef['height']-1)
    lcd[ctrlid].message(combinedstr)

#Display values centred on the fourth row, for Nokia displays
def displayValueLine(valuestr, ctrlid):
    """Display values centred on the fourth row, for Nokia displays"""
    ctrldef = config['local']['controls'][ctrlid]['display']
    if ctrldef['height'] > 4:
        leftpad = (ctrldef['width'] - len(valuestr)) // 2
        combinedstr = (" " * leftpad) + valuestr + (" " * (ctrldef['width'] - len(valuestr) - leftpad))
        lcd[ctrlid].setCursor(0, ctrldef['height']-3)
        lcd[ctrlid].message(combinedstr)
    


#Display a timer bar on the bottom row of the instructions display
def displayTimer():
    """Display a timer bar on the bottom row of the instructions display"""
    global timeoutdisplayblocks
    if timeoutstarted == 0.0:
        blockstodisplay = 0
    else:
        timesincetimeout = time.time() - timeoutstarted
        if timesincetimeout > roundconfig['timeout']:
            blockstodisplay = 0
        else:
            blockstodisplay = int(0.5 + 20 * (1 - (timesincetimeout / roundconfig['timeout'])))
        #Work out diff between currently displayed blocks and intended, to minimise amount to draw
        if blockstodisplay > timeoutdisplayblocks:
            lcd["0"].setCursor(timeoutdisplayblocks, 3)
            lcd["0"].message((blockstodisplay - timeoutdisplayblocks) * chr(255))
        elif timeoutdisplayblocks > blockstodisplay:
            lcd["0"].setCursor(blockstodisplay, 3)
            lcd["0"].message((timeoutdisplayblocks - blockstodisplay ) * ' ')
        timeoutdisplayblocks = blockstodisplay
        
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
            display(str(msg.payload), 20, "0")
            #start timer?
            if 'timeout' in roundconfig and roundconfig['timeout'] > 0.0:
                timeoutdisplayblocks = 0
                timeoutstarted = time.time()
        elif nodes[2] in controlids:
            ctrlid = nodes[2]
            if nodes[3] == 'enabled':
                roundconfig['controls'][ctrlid]['enabled'] = False
                #switch it off?
                display(" ", config['local']['controls'][ctrlid]['display'], ctrlid)
            elif nodes[3] == 'name':
                display(str(msg.payload), config['local']['controls'][ctrlid]['display'], ctrlid)
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
                    
#Process control value assignment
#def processControlValueAssignment(value, ctrlid, override=False):
 #   """Process control value assignment"""
"""    roundsetup = roundconfig['controls'][ctrlid]
    ctrltype = roundsetup['type']
    ctrldef = roundsetup['definition']
    if 'value' not in ctrldef or ctrldef['value'] != value or override:
        controlsetup = config['local']['controls'][ctrlid]
        hardwaretype = controlsetup['hardware']
        pins = controlsetup['pins']
        if hardwaretype == 'phonestylemenu':
            RGB = [0.0, 0.0, 0.0]
            if ctrltype == 'toggle':
       	        if controlsetup['display']['height'] > 3:
                    if value:
                        displayValueLine("On", ctrlid)
                        RGB = [1.0, 0.0, 0.0]
                    else:
                        displayValueLine("Off", ctrlid)
            elif ctrltype == 'selector':
                if controlsetup['display']['height'] > 3:
                    displayValueLine(str(value), ctrlid)
            elif ctrltype == 'colour':
                if controlsetup['display']['height'] > 3:
                    displayValueLine(str(value), ctrlid)
                #Light the LED the right colours
                RGB = controlsetup['colours'][str(value)]
            elif ctrltype == 'words':
                if controlsetup['display']['height'] > 3:
                    displayValueLine(value, ctrlid)
            PWM.start(pins['RGB_R'], RGB[0])
            PWM.start(pins['RGB_G'], RGB[1])
            PWM.start(pins['RGB_B'], RGB[2])
        #elif hardwaretype == 'bargraphpotentiometer':
            #if roundsetup['enabled']:
            #    if ctrltype == 'toggle':
            #        if value:
                        #barGraph(10)
            #        else:
                        #barGraph(0)
            #    elif ctrltype == 'selector':
                    #barGraph(value)
            #else:
                #barGraph(0)
        elif hardwaretype == 'combo7SegColourRotary':
            RGB = [0.0, 0.0, 0.0]
            if roundsetup['enabled']:
                if ctrltype == 'toggle':
                    if value:
                        displayDigits('On')
                        RGB = [1.0, 0.0, 0.0]
                    else:
                        displayDigits('Off')
                        #Switch off LED
                elif ctrltype == 'selector':
                    displayDigits(str(value))
                    #Switch off LED
                elif ctrltype == 'colour':
                    #Light LED appropriate colour
                    if value == 'red':
                        displayDigits("RED")
                    elif value == 'green':
                        displayDigits("GREN")
                    elif value == 'blue':
                        displayDigits("BLUE")
                    elif value == 'yellow':
                        displayDigits("YELO")
                    elif value == 'cyan':
                        displayDigits("CYAN")
                    RGB = controlsetup['colours'][str(value)]
                elif ctrltype == 'words':
                    #Switch off LED
                    displayDigits(value.upper())
            else:
                dispalDigits("    ")
            PWM.start(pins['RGB_R'], 1.0 - RGB[0])
            PWM.start(pins['RGB_G'], 1.0 - RGB[1])
            PWM.start(pins['RGB_B'], 1.0 - RGB[2])
        elif hardwaretype == 'illuminatedbutton':
            if ctrltype == 'toggle':
                if value:
                    GPIO.output(pins['LED'], GPIO.HIGH)
                else:
                    GPIO.output(pins['LED'], GPIO.LOW)
        elif hardwaretype == 'potentiometer':
            if ctrltype == 'toggle':
                if controlsetup['display']['height']>3:
                    if value:
                        displayValueLine("On", ctrlid)
                        #Light the LED red
                    else:
                        displayValueLine("Off", ctrlid)
                        #Switch off LED
            elif ctrltype == 'selector':
                if controlsetup['display']['height']>3:
                    displayValueLine(str(value), ctrlid)
            elif ctrltype == 'colour':
                if controlsetup['display']['height']>3:
                    displayValueLine(str(value), ctrlid)
                #Light the LED the right colours
            elif ctrltype == 'words':
                if controlsetup['display']['height']>3:
                    displayValueLine(value, ctrlid)
            elif ctrltype == 'verbs':
                if controlsetup['display']['height']>3:
                    displayValueLine(value, ctrlid)
        elif hardwaretype == 'illuminatedtoggle':
            if ctrltype == 'toggle':
                if controlsetup['display']['height']>3:
                    if value:
    	                displayValueLine("On", ctrlid)
                        GPIO.output(pins['LED'], GPIO.LOW)
                    else:
                        displayValueLine("Off", ctrlid)
                        GPIO.output(pins['LED'], GPIO.HIGH)
        elif hardwaretype == 'keypad':
            #no need for cases
            displayValueLine(value)
        ctrldef['value'] = value
   """         
#Process an incoming config for a round
def processRoundConfig(roundconfigstring):
    """Process an incoming config for a round"""
    x = json.loads(roundconfigstring)
    for key in x.keys():
        roundconfig[key] = x[key]
    display(roundconfig['instructions'], 20, "0")
    for ctrlid in controlids:
        roundsetup = roundconfig['controls'][ctrlid]
        controlsetup = config['local']['controls'][ctrlid]
        display(roundsetup['name'], controlsetup['display']['width'], ctrlid)
        if 'definition' in roundsetup and roundsetup['enabled']:
            ctrltype = roundsetup['type']
            ctrldef = roundsetup['definition']
            #there's more to setup of course
            hardwaretype = config['local']['controls'][ctrlid]['hardware']
            if hardwaretype == 'phonestylemenu':
                if ctrltype == 'toggle':
                    displayButtonsLine("Off", "On", ctrlid)
                elif ctrltype == 'verbs':
                    displayButtonsLine(ctrldef['pool'][0], ctrldef['pool'][1], ctrlid)
                else:
                    displayButtonsLine("<<<<", ">>>>", ctrlid)
            elif hardwaretype == 'combo7SegColourRotary':
                if ctrltype == 'button':
                    displayDigits("PUSH")
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
    displayTimer()
    
