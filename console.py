# console.py
# Abstraction of SpaceHack clients for the server

import GameStarter.gamestart
import controls
import ctrltypes
import json
import random

class Console:
    def __init__(self, mqttclient, interface):
        # IP Address of the console (or rather, it's identifier)
        self.ip        = interface['ip']
        # Interface definition - i.e. the console's hardware capabilities
        self.interface = interface
        # MQTT client, for things handled internally
        self.mqtt      = mqttclient
        self.ctrls     = {}
        self.clearSetup()
    
    def clearSetup(self):
        """ Clears the current console setup """
        self.setup = {
            'controls': {},
            'timeout': 0.0,
            'instructions': ''
        }
        self.clearAllControls()
    
    @property
    def startButtonID(self):
        """ Retrieve the ID of the start button """
        return next(c['id'] for c in self.interface['controls'] if 'gamestart' in c)
    
    def publish(self, subtopic, message):
        """ Publish <message> to clients/{ip}/<subtopic> """
        self.mqtt.publish('clients/' + self.ip + '/' + subtopic, message)
    
    def subscribe(self):
        """ Subscribe the MQTT client to this console's messages """
        for control in self.interface['controls']:
            self.mqtt.subscribe(str('clients/' + self.ip + '/' + control['id'] + '/value'))
    
    def sendCurrentSetup(self):
        """ Publish the current setup to the console """
        self.publish('configure', json.dumps(self.setup))
    
    def __clearControl(self, ctrlid):
        """ Internal method for blanking a control (deferred send) """
        self.setup['controls'][ctrlid] = {
            'type':    'inactive',
            'enabled': 0,
            'name':    ''
        }
        if ctrlid in self.ctrls:
            del self.ctrls['ctrlid']
    
    def clearControl(self, ctrlid):
        """ Clear a control to blank """
        self.__clearControl(ctrlid)
        self.sendCurrentSetup
    
    def clearAllControls(self):
        """ Clear all controls to blank """
        for control in self.interface['controls']:
            self.__clearControl(control['id'])
        self.sendCurrentSetup
    
    def pickNewControls(self):
        """ Pick a random set of controls for this console """
        self.clearSetup()
        setup = self.setup
        #Pay attention to 'enabled' for the control as a whole
        for control in (x for x in self.interface["controls"] if 'enabled' not in x or x['enabled'] == 1):
            ctrlid = control['id']
            control = ctrltypes.pickNewControl(control, self.setup[ctrlid])
            control.randomize()
            self.ctrls[ctrlid] = control
            print("Control " + ctrlid + " is " + control.type + ": " + control.name)
        self.sendCurrentSetup()
    
    def recordControl(self, ctrlid, value):
        """ Record a received value """
        if ctrlid in self.ctrls:
            return self.ctrls[ctrlid].recordValue(value)
        return false
    
    def randomControl(self):
        """ Return a random control on this console """
        return random.choice(self.ctrls)
    
    # NOTE: Currently, the player's instruction screen is also set when sending current setup
    def tellPlayer(self, message):
        """Set the instruction panel"""
        message = str(message)
        self.publish('instructions', message)
        # FIXME: Fudge to be certain we stored this (so we can stop the client responding to this field!
        self.setup['instructions'] = message
    
    def corruptControl(self, ctrlid):
        """Introduce text corruptions to control names as artificial 'malfunctions'"""
        try:
            ctrl = self.setup['controls'][ctrlid]
            if 'corruptedname' in ctrl:
                corruptedname = ctrl['corruptedname']
            else:
                corruptedname = ctrl['name']
            corruptednamelist = list(corruptedname)
            # Get a list of replaceable character positions, and select some to corrupt
            replaceablechars = [ x[0] for x in enumerate(corruptednamelist) if x[1] != ' ' ]
            replacechars = random.sample(replaceablechars, 3)
            # Corrupt the selected characters
            for i in replacechars:
                #Try to get a printable character, this is different for HD44780 than Nokia but I just use the HD44780 here
                ascii = random.choice(range(12 * 16))
                ascii += 32
                if ascii > 128:
                    ascii += 32
                corruptednamelist[i] = chr(ascii)
            corruptedname = ''.join(corruptednamelist)
            ctrl['corruptedname'] = corruptedname
            self.publish(ctrlid + '/name', corruptedname)
        except:
            pass
    
    def fixControl(self, ctrlid):
        """Reset the corrupted control name when the player gets it right"""
        ctrl = self.setup['controls'][ctrlid]
        if 'corruptedname' in ctrl:
            del ctrl['corruptedname']
        self.publish(ctrlid + '/name', ctrl['name'])
    
    def resetToWaiting(self):
        """Reset the console setup and define the start button and instruction"""
        self.clearSetup()
        self.tellPlayer(controls.blurb['waitingforplayers'])
        self.setup['controls'][self.startButtonID] = {
            'type':       'button',
            'enabled':    1,
            'name':       controls.blurb['startbutton'],
            'gamestart':  True,
            'definition': {}
        }
        self.sendCurrentSetup()
