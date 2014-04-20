#SpaceHack!  Game server main module
#York Hackspace January 2014
#This runs on a Raspberry Pi

import controls
import mosquitto
import time
import random
import json

sound = False #Switch this off if you don't have pyGame

debugMode = True

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
currenttimeout = 10.0
lastgenerated = time.time()
numinstructions = 0
gamestate = 'initserver' #initserver, readytostart, waitingforplayers, initgame, setupround, playround, roundover, gameover

#Show when we've connected
def on_connect(mosq, obj, rc):
    """Receive MQTT connection notification"""
    if rc == 0:
        print("Connected to MQTT")
        global gamestate
        gamestate = 'readytostart'
    else:
        print("Failed - return code is " + rc)

#MQTT message arrived
def on_message(mosq, obj, msg):
    """Receive and process incoming MQTT published message"""
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
            if gamestate in ['readytostart', 'waitingforplayers']:
                #Still waiting to start
                consolesetup['instructions'] = controls.blurb['readytostart']
                consolesetup['timeout'] = 0.0
                consolesetup['controls'] = {}
                print(config['controls'])
                for control in config['controls']:
                    ctrlid = control['id']
                    consolesetup['controls'][ctrlid]={}
                    if 'gamestart' in control:
                        consolesetup['controls'][ctrlid]['type'] = 'button'
                        consolesetup['controls'][ctrlid]['enabled'] = 1
                        consolesetup['controls'][ctrlid]['name'] = controls.blurb['startbutton']
                        consolesetup['controls'][ctrlid]['gamestart'] = True
                        consolesetup['controls'][ctrlid]['definition'] = {}
                    else:
                        consolesetup['controls'][ctrlid]['type'] = 'inactive'
                        consolesetup['controls'][ctrlid]['enabled'] = 0
                        consolesetup['controls'][ctrlid]['name'] = ""
                    client.subscribe('clients/' + consoleip + '/' + ctrlid + '/value')
            else:
                #There's a game on, but this client's late for it
                if consoleip in players:
                    players.remove(consoleip)
                #Was this the last remaining player?
                if len(players) == 0:
                    #back to start
                    resetToWaiting()
                    return
                else:
                    #Game still active - sit the rest of it out
                    consolesetup['instructions'] = controls.blurb['gameinprogress']
                    consolesetup['controls'] = {}
                    for control in config['controls']:
                        ctrlid = control['id']
                        consolesetup['controls'][ctrlid]={}
                        consolesetup['controls'][ctrlid]['type'] = 'inactive'
                        consolesetup['controls'][ctrlid]['enabled'] = 0
                        consolesetup['controls'][ctrlid]['name'] = ""
                        client.subscribe('clients/' + consoleip + '/' + ctrlid + '/value')
            if len(consolesetup) > 0:
                currentsetup[consoleip] = consolesetup
                client.publish('clients/' + consoleip + '/configure', json.dumps(consolesetup))
    elif nodes[0] == 'clients':
        consoleip = nodes[1]
        ctrlid = nodes[2]
        if nodes[3] == 'value':
            value = str(msg.payload)
            if consoleip in currentsetup:
                if 'controls' in currentsetup[consoleip]:
                    if currentsetup[consoleip]['controls'][ctrlid]['type'] in ['button', 'toggle', 'selector']:
                        try:
                            value = int(value)
                        except ValueError:
                            return
                    receiveValue(consoleip, ctrlid, value)
                
def receiveValue(consoleip, ctrlid, value):
    """Process a received value for a control"""
    global lastgenerated
    global gamestate
    global numinstructions
    if gamestate == 'playround':
        #Check posted value against current targets
        matched = False
        if 'definition' in currentsetup[consoleip]['controls'][ctrlid]:
            currentsetup[consoleip]['controls'][ctrlid]['definition']['value'] = value
        for targetip in players:
            consoledef = console[targetip]
            if ('target' in consoledef and consoledef['target']['console'] == consoleip 
                        and consoledef['target']['control'] == ctrlid
                        and str(consoledef['target']['value']) == str(value)):
                #Match
                matched = True
                clearCorruption(consoleip, ctrlid)
                playSound(random.choice(controls.soundfiles['right']))

                #update stats
                playerstats[targetip]['instructions']['hit'] += 1
                playerstats[consoleip]['targets']['hit'] += 1
                numinstructions -= 1
                if numinstructions <= 0:
                    #Round over
                    roundOver()
                else:
                    #Pick a new target and carry on
                    pickNewTarget(targetip)
        if not matched: #Need to also check if a game round has begun yet
            #Suppress caring about button releases - only important in game starts
            if not (currentsetup[consoleip]['controls'][ctrlid]['type'] == 'button' and str(value) == "0"):
                playSound(random.choice(controls.soundfiles['wrong']))
    elif gamestate in ['readytostart', 'waitingforplayers']:
        #button push?
        if 'gamestart' in currentsetup[consoleip]['controls'][ctrlid]:
            if value:
                #Add to list of players
                if not consoleip in players:
                    players.append(consoleip)
            else:
                #remove from list of players
                if consoleip in players:
                    players.remove(consoleip)
            #Either way, reset the clock for game start
            gamestate = 'waitingforplayers'
            lastgenerated = time.time()
            
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
        for control in console[consoleip]["controls"]:
            ctrlid = control['id']
            consolesetup['controls'][ctrlid]={}
            consolesetup['controls'][ctrlid]['enabled']=1
            #In case LCDs fail - allow a 'fixed name' we can tape over the LCD
            if 'fixedname' in control:
                consolesetup['controls'][ctrlid]['name'] = str(control['fixedname'])
            else: #Normal case - generate a new control name
                consolesetup['controls'][ctrlid]['name']=controls.getControlName(control['width'], 2, 12)
            ctrldef = random.choice([x for x in control['supported']])
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

#Get a choice from a range that isn't the same as the old value
def getChoice(choicerange, oldval):
    """Get a choice from a range that isn't the same as the old value."""
    finished=False
    while not finished:
        retval = random.choice(choicerange)
        if retval != oldval:
            finished=True
    return retval

#Pick a new instruction to display on a given console
def pickNewTarget(consoleip):
    """Pick a new instruction to display on a given console."""
    #pick a random console and random control from that console
    targetconsole = random.choice(players)
    targetsetup = currentsetup[targetconsole]
    targetctrlid = random.choice(targetsetup['controls'].keys())
    targetcontrol = targetsetup['controls'][targetctrlid]
    targetname = targetcontrol['name']
    targetdef = targetcontrol['definition']
    targettimeout = currenttimeout
    if 'scalefactor' in targetdef:
        targettimeout *= targetdef['scalefactor']
    targetinstruction = ''
    #pick a new target based on the control type and current value
    ctrltype = targetcontrol['type']
    if 'value' in targetdef:
        curval = targetdef['value']
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
    elif ctrltype in ['words', 'verbs']:
        targetrange = targetdef['pool']
        targetval=getChoice(targetrange, curval)
        if 'list' in targetdef:
            if targetdef['list']=='passwd':
                targetinstruction = controls.getPasswdAction(targetname, targetval)
            elif targetdef['list']=='verbs' or ctrltype == 'verbs':
                targetinstruction = controls.getVerbListAction(targetname, targetval)
        elif ctrltype == 'verbs':
            targetinstruction = controls.getVerbListAction(targetname, targetval)
        if targetinstruction=='':
            targetinstruction = controls.getWordAction(targetname, targetval)
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
    console[consoleip]['target']={"console": targetconsole, "control": targetctrlid, "value": targetval, "timestamp": time.time(), "timeout": targettimeout}
    print("Instruction: " + consoleip + '/' + targetctrlid + ' - ' + str(targetinstruction))
    #update game stats
    playerstats[consoleip]['instructions']['total'] += 1
    playerstats[targetconsole]['targets']['total'] += 1
    #publish!
    client.publish('clients/' + consoleip + '/timeout', str(targettimeout))
    client.publish('clients/' + consoleip + '/instructions', str(targetinstruction))

def checkTimeouts():
    """Check all targets for expired instructions"""
    global numinstructions
    for consoleip in players:
        consoledef = console[consoleip]
        if 'target' in consoledef and consoledef['target']['timestamp'] + consoledef['target']['timeout'] < time.time():
            #Expired instruction
            playSound(random.choice(controls.soundfiles['wrong']))
            playerstats[consoleip]['instructions']['missed'] += 1
            playerstats[consoledef['target']['console']]['targets']['missed'] += 1
            numinstructions -= 1
            playerstats['game']['lives'] -= 1
            if playerstats['game']['lives'] <= 0:
                #Game over!
                gameOver()
            elif numinstructions <= 0:
                #Round over
                roundOver()
            else:
                #Pick a new target and carry on
                increaseCorruption(consoledef['target']['console'], consoledef['target']['control'])
                pickNewTarget(consoleip)
                
def increaseCorruption(consoleip, ctrlid):
    """Introduce text corruptions to control names as artificial 'malfunctions'"""
    ctrldef = currentsetup[consoleip]['controls'][ctrlid]
    if 'corruptedname' in ctrldef:
        corruptednamelist = list(ctrldef['corruptedname'])
    else:
        corruptednamelist = list(ctrldef['name'])
    count = 3
    while count > 0:
        #Try to get a printable character, this is different for HD44780 than Nokia but I just use the HD44780 here
        ascii = random.choice(range(12 * 16))
        ascii += 32
        if ascii > 128:
            ascii += 32
        #Position to change - avoid spaces so corrupt name prints the same
        pos = random.choice(range(len(corruptednamelist)))
        if corruptednamelist[pos] != ' ':
            corruptednamelist[pos] = chr(ascii)
            count -= 1
    corruptedname = ''.join(corruptednamelist)
    ctrldef['corruptedname'] = corruptedname
    client.publish("clients/" + consoleip + "/" + ctrlid + "/name", corruptedname)
        
def clearCorruption(consoleip, ctrlid):
    """Reset the corrupted control name when the player gets it right"""
    ctrldef = currentsetup[consoleip]['controls'][ctrlid]
    if 'corruptedname' in ctrldef:
        del ctrldef['corruptedname']
        client.publish("clients/" + consoleip + "/" + ctrlid + "/name", str(ctrldef['name']))

def tellAllPlayers(consolelist, message):
    """Simple routine to broadcast a message to a list or consoles"""
    for consoleip in consolelist:
        client.publish('clients/' + consoleip + '/instructions', str(message))
        
def initGame():
    """Kick off a new game"""
    #Start game!
    global gamestate
    global currenttimeout
    gamestate = 'initgame'
    currenttimeout = 15.0
    for consoleip in players:
        #Slight fudge in assuming control 5 is the big button
        client.publish('clients/' + consoleip + '/5/name', "Get ready!")
    tellAllPlayers(players, controls.blurb['logo'])
    #Music
    if sound:
        #Pygame for sounds
        pygame.mixer.quit()
        pygame.mixer.init(48000, -16, 2, 1024) #was 1024
        playSound(controls.soundfiles['special']['fanfare'])
    #cut off non-players from participating
    for consoleip in list(set(consoles) - set(players)):
        consolesetup = {}
        consolesetup['instructions'] = controls.blurb['gameinprogress']
        consolesetup['timeout'] = 0.0
        consolesetup['controls'] = {}
        for control in console[consoleip]['controls']:
            ctrlid = control['id']
            consolesetup['controls'][ctrlid]={}
            consolesetup['controls'][ctrlid]['type'] = 'inactive'
            consolesetup['controls'][ctrlid]['enabled'] = 0
            consolesetup['controls'][ctrlid]['name'] = ""
            client.subscribe('clients/' + consoleip + '/' + ctrlid + '/value')
        client.publish('clients/' + consoleip + '/configure', json.dumps(consolesetup))
        currentsetup[consoleip] = consolesetup
    #Explanatory intro blurb
    if not debugMode:
        for txt in controls.blurb['intro']:
            tellAllPlayers(players, txt)
            time.sleep(5.0)
    #Setup initial game params
    global playerstats
    playerstats = {}
    for consoleip in players:
        playerstats[consoleip] = {}
        playerstats[consoleip]['instructions'] = {} #stats on instructions you read out
        playerstats[consoleip]['targets'] = {} #stats on instructions you should have implemented
        playerstats[consoleip]['instructions']['total'] = 0
        playerstats[consoleip]['instructions']['hit'] = 0
        playerstats[consoleip]['instructions']['missed'] = 0
        playerstats[consoleip]['targets']['total'] = 0
        playerstats[consoleip]['targets']['hit'] = 0
        playerstats[consoleip]['targets']['missed'] = 0
    playerstats['game'] = {}
    playerstats['game']['rounds'] = 0
    #stop music?
    if sound:
        for fn in controls.soundfiles['continuous']:
            snd = pygame.mixer.Sound("sounds/" + fn)
            snd.play(-1)
    #start first round
    initRound()

def initRound():
    """Kick off a new round"""
    global numinstructions
    global lastgenerated
    global gamestate
    gamestate = 'setupround'
    playSound(random.choice(controls.soundfiles['atmosphere']))
    #Dump another batch of random control names and action
    defineControls()
    playerstats['game']['rounds'] += 1
    playerstats['game']['lives'] = 5
    numinstructions = 10
    lastgenerated = time.time()
    
def roundOver():
    """End the round and jump to Hyperspace"""
    print "roundOver() called"
    global gamestate
    global currenttimeout
    gamestate = 'roundover'
    print "    gamestate changed"
    #Zap all existing targets
    for consoleip in players:
        consoledef = console[consoleip]
        if 'target' in consoledef:
            del consoledef['target']
        client.publish('clients/' + consoleip + '/timeout', "0.0")
    print "    about to tell player hyperspace"
    #play sound?
    tellAllPlayers(players, controls.blurb['hyperspace'])
    print "    Done hyperspace, playing sound..."
    playSound(controls.soundfiles['special']['hyperspace'])
    print "    about to sleeping "
    time.sleep(8.0)
    currenttimeout *= 0.75
    print "    about to init round"
    initRound()
    print "    all done!"
    
def gameOver():
    """End the current game and dole out the medals"""
    global gamestate
    gamestate = 'gameover'
    for consoleip in players:
        client.publish('clients/' + consoleip + '/timeout', "0.0")
    tellAllPlayers(players, controls.blurb['ending']['splash'])
    #play sound
    if sound:
        #Pygame for sounds
        pygame.mixer.quit()
        pygame.mixer.init(48000, -16, 2, 1024) #was 1024
        playSound(controls.soundfiles['special']['explosion'])
        playSound(controls.soundfiles['special']['taps'])
    for consoleip in players:
        config = console[consoleip]
        consolesetup = {}
        consolesetup['instructions'] = str(controls.blurb['ending']['start'])
        consolesetup['timeout'] = 0.0
        consolesetup['controls'] = {}
        for control in config['controls']:
            ctrlid = control['id']
            consolesetup['controls'][ctrlid]={}
            consolesetup['controls'][ctrlid]['type'] = 'inactive'
            consolesetup['controls'][ctrlid]['enabled'] = 0
            consolesetup['controls'][ctrlid]['name'] = ""
        client.publish("clients/" + consoleip + "/configure", json.dumps(consolesetup))
    time.sleep(5.0)
    instr = controls.blurb['ending']['you']
    #stats for your instructions
    for consoleip in players:
        instryou = instr.replace("{1}", str(playerstats[consoleip]['instructions']['hit']))
        instryou = instryou.replace("{2}", str(playerstats[consoleip]['instructions']['missed'] + playerstats[consoleip]['instructions']['hit']))
        instryou = instryou.replace("{3}", str(playerstats[consoleip]['instructions']['missed']))
        client.publish("clients/" + consoleip + "/instructions", str(instryou))
    time.sleep(5.0)
    #stats for your targets
    instr = controls.blurb['ending']['them']
    for consoleip in players:
        instrthem = instr.replace("{1}", str(playerstats[consoleip]['targets']['hit']))
        instrthem = instrthem.replace("{2}", str(playerstats[consoleip]['targets']['missed'] + playerstats[consoleip]['targets']['hit']))
        client.publish("clients/" + consoleip + "/instructions", str(instrthem))
    time.sleep(5.0)
    tellAllPlayers(players, controls.blurb['ending']['end'])
    time.sleep(5.0)
    #medals!
    for consoleip in players:
        client.publish("clients/" + consoleip + "/instructions", str(controls.getMedal()))
    time.sleep(15.0)
    resetToWaiting()
    
def resetToWaiting():
    """Reset game back to waiting for new players"""
    global gamestate
    gamestate = 'readytostart'
    for consoleip in consoles:
        consolesetup = {}
        consolesetup['instructions'] = controls.blurb['readytostart']
        consolesetup['controls'] = {}
        consolesetup['timeout'] = 0.0
        config = console[consoleip]
        for control in config['controls']:
            ctrlid = control['id']
            consolesetup['controls'][ctrlid]={}
            if 'gamestart' in control:
                consolesetup['controls'][ctrlid]['type'] = 'button'
                consolesetup['controls'][ctrlid]['enabled'] = 1
                consolesetup['controls'][ctrlid]['name'] = controls.blurb['startbutton']
                consolesetup['controls'][ctrlid]['gamestart'] = True
                consolesetup['controls'][ctrlid]['definition'] = {}
            else:
                consolesetup['controls'][ctrlid]['type'] = 'inactive'
                consolesetup['controls'][ctrlid]['enabled'] = 0
                consolesetup['controls'][ctrlid]['name'] = ""
        currentsetup[consoleip] = consolesetup
        client.publish('clients/' + consoleip + '/configure', json.dumps(consolesetup))
    global lastgenerated
    global numinstructions
    global players
    players = []
    lastgenerated = time.time()
    numinstructions = 0
    
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
    if gamestate == 'waitingforplayers' and len(players) >= 1 and time.time() - lastgenerated > 5.0:
        initGame()        
    elif gamestate == 'setupround' and time.time() - lastgenerated > 10.0:
        gamestate = 'playround'
        for consoleip in players:
            pickNewTarget(consoleip)
    elif gamestate == 'playround':
        checkTimeouts()

#If client.loop() returns non-zero, loop drops out to here.
#Final code should try to reconnect to MQTT and/or networking if so.
