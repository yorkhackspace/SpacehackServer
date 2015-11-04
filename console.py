# console.py
# Abstraction of SpaceHack clients for the server

import GameStarter.gamestart
import controls
import json
import random

class Console:
    def __init__(self, mqttclient, interface):
        self.ip        = interface['ip']
        self.interface = interface
	self.mqtt      = mqttclient
        self.clearSetup()
    
    def clearSetup(self):
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
            print("Control " + ctrlid + " is " + ctrltype + ": " + setupctrl['name'])
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
