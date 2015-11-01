# console.py
# Abstraction of SpaceHack clients for the server

import GameStarter.gamestart
import json

class Console:
    def __init__(self, mqttclient, interface):
        self.ip        = interface['ip']
        self.interface = interface
	self.mqtt      = mqttclient
        self.reset()
    
    def reset(self):
        self.setup     = {
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
            self.mqtt.subscribe('clients/' + self.ip + '/' + control['id'] + '/value')
    
    def sendCurrentSetup(self):
        """ Publish the current setup to the console """
        self.publish('configure', json.dumps(self.setup))
    
    def __clearControl(self, ctrlid):
        self.setup['controls'][ctrlid] = {
            'type':    'inactive',
            'enabled': 0,
            'name':    ''
        }
    
    def clearControl(self, ctrlid):
        """ Clear a control to blank """
        self.__clearControl(ctrlid)
        self.sendCurrentSetup
    
    def clearAllControls(self):
        """ Clear all controls to blank """
        for control in self.interface['controls']:
            self.__clearControl(control['id'])
        self.sendCurrentSetup
    
    def recordControl(self, ctrlid, value):
        """ Record a received value """
        if 'definition' in self.setup['controls'][ctrlid]:
            self.setup['controls'][ctrlid]['definition']['value'] = value
    
    def setControl(self, ctrlid, value):
        """ Assign a current value to a control """
        recordControl(ctrlid, value)
        consoles[consoleip].sendCurrentSetup()
    
    # NOTE: Currently, the player's instruction screen is also set when sending current setup
    def tellPlayer(self, message):
        message = str(message)
        self.publish('instructions', message)
        # FIXME: Fudge to be certain we stored this (so we can stop the client responding to this field!
        self.setup['instructions'] = message
    
    def on_ctrlvalue(self, ctrlid, value):
        pass
    
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
