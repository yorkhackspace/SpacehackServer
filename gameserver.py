#!/usr/bin/env python
#SpaceHack!  Game server main module
#York Hackspace January 2014
#This runs on a Raspberry Pi

import controls
import mosquitto
import time
import random
import json
import os
from GameStarter.gamestart import GameStarter
from console import Console

# Best guess whether we're on a laptop or the real thing
runningOnPi = (os.uname()[4][:3] == 'arm')

lifeDisplay = runningOnPi
sound = True #Switch this off if you don't have pyGame
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

# Clever start button handling
gs = GameStarter(4, 1.5, 4.0, 0.5)
gsIDs = {}
nextID = 0

#Game variables
consoles = {} #all registered consoles
players = [] #all participating players
playerstats = {}
currenttimeout = 30.0
lastgenerated = time.time()
numinstructions = 0
instructions = {}
gamestate = 'initserver' #initserver, waitingforplayers, initgame, setupround, playround, roundover, hyperspace, gameover
warningsound = None

#Show when we've connected
def on_connect(mosq, obj, rc):
    """Receive MQTT connection notification"""
    if rc == 0:
        print("Connected to MQTT")
        global gamestate
        gamestate = 'waitingforplayers'
    else:
        print("Failed - return code is " + rc)

#MQTT message arrived
def on_message(mosq, obj, msg):
    """Receive and process incoming MQTT published message"""
    nodes = msg.topic.split('/')
    print(gamestate + ' - ' + msg.topic + " - " + str(msg.payload))
    if nodes[0]=='server':
        if nodes[1]=='register':
            config = json.loads(str(msg.payload))
            consoleip = config['ip']
            # Create and store an object to manage this console
            if not consoleip in consoles:
                c = Console(mosq, config)
                c.subscribe()
                consoles[consoleip] = c
            console = consoles[consoleip]
            console.clearSetup()
            #set console up for game start
            if gamestate == 'waitingforplayers':
                #Still waiting to start
                print(config['controls'])
                console.setup['controls'][console.startButtonID] = {
                    'type':       'button',
                    'enabled':    1,
                    'name':       controls.blurb['startbutton'],
                    'gamestart':  True,
                    'definition': {}
                }
                console.sendCurrentSetup()
                console.tellPlayer(controls.blurb['waitingforplayers'])
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
                    console.tellPlayer(controls.blurb['gameinprogress'])
    elif nodes[0] == 'clients':
        consoleip = nodes[1]
        ctrlid = nodes[2]
        if nodes[3] == 'value':
            value = str(msg.payload)
            if consoleip in consoles:
                if 'controls' in consoles[consoleip].setup:
                    if consoles[consoleip].setup['controls'][ctrlid]['type'] in ['button', 'toggle', 'selector']:
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
    global gsIDs
    global nextID
    if gamestate == 'playround':
        # Record the control value
        consoles[consoleip].recordValue(value)
        #Check posted value against current instructions
        match = (consoleip, ctrlid, value)
        if match in instructions:
            # Find out who issued the instruction
            info = instructions[match]
            instructorip = info['instructor']
            consoles[consoleip].fixControl(ctrlid)
            playSound(random.choice(controls.soundfiles['right']))
            
            #update stats
            playerstats[instructorip]['instructions']['hit'] += 1
            playerstats[targetip]['targets']['hit'] += 1
            numinstructions -= 1
            if numinstructions <= 0:
                #Round over
                roundOver()
            else:
                #Pick a new target and carry on
                pickNewTarget(instructorip)
            
            del instructions[match]
        else:
            #Suppress caring about button releases - only important in game starts
            if not (consoles[consoleip].setup['controls'][ctrlid]['type'] == 'button' and str(value) == "0"):
                playSound(random.choice(controls.soundfiles['wrong']))
    elif gamestate == 'setupround':
        consoles[consoleip].recordValue(value)
    elif gamestate == 'waitingforplayers':
        #button push?
        if 'gamestart' in consoles[consoleip].setup['controls'][ctrlid]:
            if value:
                #Add to list of players
                if not consoleip in gsIDs:
                    gsIDs[consoleip] = nextID
                    nextID += 1
                gs.push(gsIDs[consoleip])
            else:
                #remove from list of players
                if consoleip in gsIDs:
                    gs.release(gsIDs[consoleip])
            #Either way, reset the clock for game start
            lastgenerated = time.time()
            
#Define a new set of controls for each client for this game round and send it to them as JSON.
def defineControls():
    """Define a new set of controls for each client for this game round and send it to them as JSON."""
    for consoleip in players:
        print("Defining console " + consoleip)
        console = consoles[consoleip]
        console.pickNewControls()
        console.setup['timeout'] = currenttimeout
        console.sendCurrentSetup()

#Get a choice from a range that isn't the same as the old value
def getChoice(choicerange, oldval):
    """Get a choice from a range that isn't the same as the old value."""
    everything = set( choicerange )
    exclude = set( [oldval] )
    return random.choice( list( everything - exclude ) )

#Pick a new instruction to display on a given console
def pickNewTarget(consoleip):
    """Pick a new instruction to display on a given console."""
    #pick a random console and random control from that console
    targetconsole = random.choice(players)
    targetsetup = consoles[targetconsole].setup
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
        targetval = getChoice([0,1], curval)
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
            elif targetdef['list']=='verbs':
                targetinstruction = controls.getVerbListAction(targetname, targetval)
            else:
                targetinstruction = controls.getWordAction(targetname, targetval)
        elif ctrltype == 'verbs':
            targetinstruction = controls.getVerbListAction(targetname, targetval)
        else:
            targetinstruction = controls.getWordAction(targetname, targetval)
    elif ctrltype == 'pin':
        # Pick a new PIN, and then format it like 0987 (4 wide, leading zeroes)
        pin = getChoice( range(10000), int(curval) )
        targetval = "%04d" % pin
        targetinstruction = controls.getPinAction(targetname, targetval)
    else:
        print("Unhandled type: " + ctrltype)
    #Now we have targetval and targetinstruction for this consoleip, store and publish it
    match = (targetconsole, targetctrlid, targetval)
    instructions[match] = {
        'instructor': consoleip,
        'expiry':     time.time() + targettimeout,
    }
    print("Instruction: " + targetconsole + '/' + targetctrlid + ' - ' + ctrltype + ' (was ' + str(curval) + ') ' + str(targetinstruction))
    #update game stats
    playerstats[consoleip]['instructions']['total'] += 1
    playerstats[targetconsole]['targets']['total'] += 1
    #publish!
    consoles[consoleip].publish('timeout', str(targettimeout))
    consoles[consoleip].tellPlayer(targetinstruction)

def showLives():
    if lifeDisplay:
        lives = playerstats['game']['lives']
        print "Lives remaining: " + str(lives)
        if 0 <= lives <= 9:
            sev.displayDigit(lives)
            if lives == 0:
                led.solid(led.CODE_Col_White)
            elif lives == 1:
                led.flash(led.CODE_Col_Red, led.CODE_Col_Red1, 120)
            elif lives == 2:
                led.solid(led.CODE_Col_Red1)
            elif lives == 3:
                led.solid(led.CODE_Col_Red2)
            elif lives == 4:
                led.solid(led.CODE_Col_Yellow)
            elif lives == 5:
                led.solid(led.CODE_Col_Green)
            
def clearLives():
    if lifeDisplay:
        sev.clear()
        led.solid(led.CODE_Display_Fade)
        time.sleep(1.1)
        led.solid(led.CODE_Display_On)

def checkTimeouts():
    """Check all targets for expired instructions"""
    global numinstructions, warningsound
    for target, info in instructions:
        if time.time() > info['expiry']:
            #Expired instruction
            playSound(random.choice(controls.soundfiles['wrong']))
            playerstats[consoleip]['instructions']['missed'] += 1
            playerstats[targetconsole]['targets']['missed'] += 1
            numinstructions -= 1
            playerstats['game']['lives'] -= 1
            showLives()
            if playerstats['game']['lives'] <= 0:
                #Game over!
                gameOver()
            elif numinstructions <= 0:
                #Round over
                roundOver()
            else:
                #Pick a new target and carry on
                consoles[targetconsole].corruptControl(targetctrlid)
                pickNewTarget(consoleip)
                #Start a warning sound if we're on our last life
                if playerstats['game']['lives'] == 1 and sound:
                    warningsound = pygame.mixer.Sound("sounds/" + random.choice(controls.soundfiles['warning']))
                    warningsound.play(-1)

def tellAllPlayers(consolelist, message):
    """Simple routine to broadcast a message to a list or consoles"""
    for consoleip in consolelist:
        consoles[consoleip].tellPlayer(message)
        
def initGame():
    """Kick off a new game"""
    #Start game!
    global gamestate
    global currenttimeout
    global nextID
    gamestate = 'initgame'
    clearLives()
    currenttimeout = 15.0
    # get game players from GameStarter
    for key, value in gsIDs.iteritems():
        if gs.isStartablePlayer(value):
            print("Player %d (%s) startable" % (value, key))
            players.append(key)
        else:
            print("Player %d (%s) not startable" % (value, key))

    print("Player IPs: %r, player IDs: %r" % (players, gsIDs))
    for consoleip in players:
        #Slight fudge in assuming control 5 is the big button
        console = consoles[consoleip]
        console.publish(str(console.startButtonID) + '/name', '')
        console.publish(str(console.startButtonID) + '/name', 'Get ready!')
    tellAllPlayers(players, controls.blurb['logo'])
    #Music
    if sound:
        #Pygame for sounds
        pygame.mixer.quit()
        pygame.mixer.init(48000, -16, 2, 1024) #was 1024
        playSound(controls.soundfiles['special']['fanfare'])
    #cut off non-players from participating
    for consoleip in list(set(consoles) - set(players)):
        consoles[consoleip].clearSetup()
        consoles[consoleip].tellPlayer(controls.blurb['gameinprogress'])
    #Explanatory intro blurb
    if not debugMode:
        for txt in controls.blurb['intro']:
            tellAllPlayers(players, txt)
            time.sleep(blurbSleep)
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
    #continuous spaceship mix
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
    global instructions
    instructions = {}
    gamestate = 'setupround'
    playSound(random.choice(controls.soundfiles['atmosphere']))
    # Set this round's opening emergency
    emergency = controls.getEmergency()
    print(emergency)
    tellAllPlayers(emergency)
    #Dump another batch of random control names and action
    defineControls()
    playerstats['game']['rounds'] += 1
    playerstats['game']['lives'] = 5
    showLives()
    numinstructions = 10
    lastgenerated = time.time()
    
def roundOver():
    """End the round and jump to Hyperspace"""
    global gamestate
    global currenttimeout
    global lastgenerated
    global warningsound
    global instructions
    instructions = {}
    gamestate = 'roundover'
    if sound and not warningsound is None:
        warningsound.stop()
        warningsound = None
    #Zap all existing targets
    for consoleip in players:
        consoles[consoleip].clearSetup()
    tellAllPlayers(players, controls.blurb['hyperspace'])
    if sound:
        playSound(controls.soundfiles['special']['hyperspace'])
    lastgenerated = time.time()
    currenttimeout *= 0.75
    gamestate = 'hyperspace'
    
def gameOver():
    """End the current game and dole out the medals"""
    global gamestate
    #Check we're not already here (fixes issue #4)
    if gamestate != 'playround':
        return
    gamestate = 'gameover'
    for consoleip in players:
        consoles[consoleip].clearSetup()
    tellAllPlayers(players, controls.blurb['ending']['splash'])
    #play sound
    if sound:
        #Pygame for sounds
        pygame.mixer.quit()
        pygame.mixer.init(48000, -16, 2, 1024) #was 1024
        playSound(controls.soundfiles['special']['explosion'])
        playSound(controls.soundfiles['special']['taps'])
    tellAllPlayers(players, controls.blurb['ending']['start'])
    time.sleep(5.0)
    instr = controls.blurb['ending']['you']
    #stats for your instructions
    for consoleip in players:
        instryou = instr.replace("{1}", str(playerstats[consoleip]['targets']['hit']))
        instryou = instryou.replace("{2}", str(playerstats[consoleip]['targets']['total']))
        instryou = instryou.replace("{3}", str(playerstats[consoleip]['targets']['missed']))
        consoles[consoleip].tellPlayer(instryou)
    time.sleep(5.0)
    #stats for your targets
    instr = controls.blurb['ending']['them']
    for consoleip in players:
        instrthem = instr.replace("{1}", str(playerstats[consoleip]['instructions']['hit']))
        instrthem = instrthem.replace("{2}", str(playerstats[consoleip]['instructions']['total']))
        consoles[consoleip].tellPlayer(instrthem)
    time.sleep(5.0)
    tellAllPlayers(players, controls.blurb['ending']['end'])
    time.sleep(5.0)
    #medals!
    for consoleip in players:
        consoles[consoleip].tellPlayer(controls.getMedal())
    time.sleep(15.0)
    resetToWaiting()
    
def resetToWaiting():
    """Reset game back to waiting for new players"""
    global gamestate
    gamestate = 'waitingforplayers'
    clearLives()
    for console in consoles.values():
        console.clearSetup()
        console.tellPlayer(controls.blurb['waitingforplayers'])
        console.setup['controls'][console.startButtonID] = {
            'type':       'button',
            'enabled':    1,
            'name':       controls.blurb['startbutton'],
            'gamestart':  True,
            'definition': {}
        }
        console.sendCurrentSetup()
    global lastgenerated
    global numinstructions
    global players
    players = []
    lastgenerated = time.time()
    numinstructions = 0
    
#Main loop

#Connect to MQTT (final code should make this a retry loop)
print 'Connecting MQTT'
client.on_connect = on_connect
client.on_message = on_message
client.connect(server)

#Main topic subscription point for clients to register their configurations to
print 'Listening for clients'
client.subscribe('server/register')

print 'Advertising server'
client.publish('server/ready', 'started')

print 'Entering main loop'
lastReady = time.time()
lastGSStep = time.time()
while(client.loop(0) == 0):
    if time.time() - lastGSStep > 0.05:
        lastGSStep = time.time()
        gs.timeStep(0.05)
    if time.time() - lastReady > 3.0:
        lastReady = time.time()
        client.publish('server/ready', 'ready')
    if gamestate == 'waitingforplayers' and gs.shouldStart():
        print 'Initializing new game'
        initGame()        
    elif gamestate == 'setupround' and time.time() - lastgenerated > 10.0:
        gamestate = 'playround'
        for consoleip in players:
            pickNewTarget(consoleip)
    elif gamestate == 'playround':
        checkTimeouts()
       
    elif gamestate == 'hyperspace' and time.time() - lastgenerated > 4.0:
        print 'Preparing next round'
        initRound()

#If client.loop() returns non-zero, loop drops out to here.
#Final code should try to reconnect to MQTT and/or networking if so.
