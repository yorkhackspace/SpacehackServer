"""
SpaceHack! Game client main module
York Hackspace January 2014
This runs on a Beaglebone Black
"""

import paho.mqtt.client as mqtt
import logging
import commands
import json
import time
import os

# import game libraries
from gamelibs import config_manager
from gamelibs import lcd_manager
from controls import control_manager

# Global Variables
roundconfig = {}
keypad = None
hasregistered = False
timeoutstarted = 0.0
reset_blocks = False

# Who am I? Get my ip address
ipaddress = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]

# configuration. Load the config and get various dictionaries and arrays back
config_file_name = 'game-%{}.config'.format(ipaddress)
config, controlids, controldefs, sortedlist = config_manager.loadConfig(config_file_name)

#initialise all of the LCDs and return a list of LCD objects
myLcdManager = lcd_manager.LcdManager(sortedlist, config)

#initialise all controls
control_manager.initialiseControls(config, sortedlist, myLcdManager)

logging.info(config['local'])
server = config['local']['server']

def on_message(client, userdata, msg):
    """Process incoming MQTT message"""
    global reset_blocks
    logging.info("{0} - {1}".format(msg.topic, msg.payload))
    nodes = msg.topic.split('/')
    global timeoutstarted
    global timeoutdisplayblocks
    global myLcdManager
    if nodes[0] == 'clients':
        if nodes[2] == 'configure':
            if str(msg.payload) == 'reboot':
                os.system('reboot')
            else:
                myLcdManager = lcd_manager.LcdManager(sortedlist, config)
                process_round_config(str(msg.payload))
                timeoutstarted = 0.0
                timeoutdisplayblocks = 0
        elif nodes[2] == 'instructions':
            myLcdManager.display(str(msg.payload), 20, "0")
            # start timer?
            if 'timeout' in roundconfig and roundconfig['timeout'] > 0.0:
                reset_blocks = True
                timeoutstarted = time.time()
        elif nodes[2] == 'timeout':
            roundconfig['timeout'] = float(str(msg.payload))
        elif nodes[2] in controlids:
            ctrlid = nodes[2]
            if nodes[3] == 'enabled':
                if str(msg.payload) == "0":
                    roundconfig['controls'][ctrlid]['enabled'] = False
                    # switch it off
                    myLcdManager.display(" ", config['local']['controls'][ctrlid]['display']['width'], ctrlid)
                else:
                    roundconfig['controls'][ctrlid]['enabled'] = True
                    # switch it on
                    myLcdManager.display(roundconfig['controls'][ctrlid]['name'], config['local']['controls'][ctrlid]['display']['width'], ctrlid)
            elif nodes[3] == 'name':
                if str(msg.payload) == '':
                    myLcdManager.clear(ctrlid)
                else:
                    myLcdManager.display(str(msg.payload), config['local']['controls'][ctrlid]['display']['width'], ctrlid, False)
    elif nodes[0] == 'server':
        if nodes[1] == 'ready':
            mess = str(msg.payload)
            if mess == 'started':
                myLcdManager = lcd_manager.LcdManager(sortedlist, config)
                client.publish("server/register", json.dumps(config['interface']))
            elif mess == 'ready':
                global hasregistered
                if not hasregistered:
                    hasregistered = True
                    client.publish("server/register", json.dumps(config['interface']))
            elif mess == 'poweroff':
                os.system('poweroff')


# Process an incoming config for a round
def process_round_config(roundconfigstring):
    """Process an incoming config for a round"""
    control_manager.initialiseControls(config, sortedlist, myLcdManager)
    config_json = json.loads(roundconfigstring)
    for key in config_json.keys():
        roundconfig[key] = config_json[key]
    myLcdManager.display(roundconfig['instructions'], 20, "0")
    control_manager.processRoundConfig(config, roundconfig, controlids)

def on_connect(client, userdata, flags, rc):
    logging.info("Connected to console with result {}".format(rc))
    # client.subscribe("foo")
    subsbase = "clients/" + ipaddress + "/"
    client.subscribe(subsbase + "configure")
    client.subscribe(subsbase + "instructions")
    client.subscribe(subsbase + "timeout")
    client.subscribe("server/ready")
    for controlid in controlids:
        client.subscribe(subsbase + str(controlid) + '/name')
        client.subscribe(subsbase + str(controlid) + '/enabled')

client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect
client.connect(server)
client.loop_start()

def main_loop():
    global reset_blocks
    while True:
        control_manager.pollControls(config, roundconfig,
                                     controlids, client, ipaddress)
        myLcdManager.displayTimer(timeoutstarted, reset_blocks,
                                  roundconfig.get('timeout', 0))
        if reset_blocks:
            reset_blocks = False

if __name__ == '__main__':
    main_loop()
