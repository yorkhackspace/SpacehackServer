# console.py
# Abstraction of SpaceHack clients for the server

import GameStarter.gamestart
import controls
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
            #In case LCDs fail - allow a 'fixed name' we can tape over the LCD
            if 'fixedname' in control:
                ctrlname = control['fixedname']
            else: #Normal case - generate a new control name
                ctrlname = controls.getControlName(control['width'], 2, 12)
            #Pay attention to 'enabled' for particular supported mode
            ctrldef = random.choice([x for x in control['supported'] if 'enabled' not in x or x['enabled'] == 1])
            ctrltype = ctrldef['type']
            # TODO: Control-specific initialization probably wants to go elsewhere
            # e.g. in the constructor of a CtrlType
            if ctrltype in ['words', 'verbs']:
                if ctrldef['fixed']:
                    targetrange = ctrldef['list']
                elif 'safe' in ctrldef and ctrldef['safe']:
                    targetrange=controls.safewords
                elif 'list' in ctrldef:
                    if ctrldef['list']=='passwd':
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
                    finished = False
                    while not finished:
                        wordpool = random.sample(targetrange, ctrldef['quantity'])
                        # A/B selectors display both words; there needs to be space for them!
                        if ctrldef['quantity'] != 2 or len(wordpool[0]) + len(wordpool[1]) < 14:
                            finished = True
                    ctrldef['pool'] = sorted(wordpool)
                else:
                    ctrldef['pool'] = ctrldef['list']
            #Pick a starting value
            # TODO: Use ctrltypes.py and the randomize method
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
            # Set up the data structure
            setup['controls'][ctrlid] = {
                'name': ctrlname,
                'type': ctrltype,
                'definition': ctrldef,
                'enabled': 1
            }
            print("Control " + ctrlid + " is " + ctrltype + ": " + ctrlname)
        self.sendCurrentSetup()

    
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
