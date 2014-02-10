# SpaceHack control text generation - York Hackspace December 2013
# Provides text generation for control names and various control type actions

import random
import json

def readWordList(filename):
    f=open('words/' + filename)
    ret = f.read().replace('\r','').split('\n')
    f.close
    if '' in ret: ret.remove('')
    return ret

#read word lists
adjectives = readWordList('adjectives.txt')
baseparts = readWordList('baseparts.txt')
elements = readWordList('elements.txt')
greekletters = readWordList('greekletters.txt')
letters = readWordList('letters.txt')
nouns = readWordList('nouns.txt')
prefixparts = readWordList('prefixparts.txt')
prefixtoothed = readWordList('prefixtoothed.txt')
suffixtoothed = readWordList('suffixtoothed.txt')
verbs = readWordList('verbs.txt')
onwords = readWordList('onwords.txt')
offwords = readWordList('offwords.txt')
bannedpasswd = readWordList('bannedpasswd.txt')

rawcols = [c.split(',') for c in readWordList('colours.txt')]
colours = [c[0] for c in rawcols]
colourlookup = {c[0]: (int(c[1]), int(c[2]), int(c[3])) for c in rawcols}

allcontrolwords = adjectives + baseparts + elements + nouns + greekletters + verbs + colours + onwords + offwords
allgeneralwords = readWordList('words.txt')

f=open("words/emergencies.txt")
emergencies=json.loads(f.read())
f.close()

# Letters that can work on a 7-segment
sevensegletters = ['A','B','C','D','E','F','G','H','I','J','L','N',
               'O','P','Q','R','S','T','U','Y']

# Letters which can be used on the 4x4 keypad via password letter substitutions
# (A, B, C and D are on the keypad, plus 1=I, 0=O, 3=E, 5=S)
passwdletters = ['A', 'B', 'C', 'D', 'E', 'I', 'O', 'S']

# Letters which can be used on an 'upside down calculator'
upsidedowncalcletters = ['O', 'I', 'Z', 'E', 'H', 'S', 'G', 'L', 'B']

#Check if a word can be displayed on a 4-digit 7-seg
def checkSafeWord(word, minlen, maxlen, safeletters):
    if len(word)>maxlen or len(word) < minlen:
        return False
    else:
        for i in range(len(word)):
            if word[i].upper() not in safeletters:
                return False
    return True

def getSafeWords(wordlist, minlen, maxlen, safeletters):
    return list(set([word for word in wordlist if checkSafeWord(word, minlen, maxlen, safeletters)]))

safewords = getSafeWords(allcontrolwords, 3, 4, sevensegletters)
passwd = list(set(getSafeWords(allgeneralwords, 4, 8, passwdletters)) - set(bannedpasswd))
upsidedowncalc = list(set(getSafeWords(allgeneralwords, 3, 4, upsidedowncalcletters)) - set(bannedpasswd))

# Used to see how many lines a label will take up on a fixed-width
# display without splitting words over line breaks, for instance on
# a 16x2 display, "salination C-crank sonar" will be displayed on
# two lines, like:
# [salination------]  or  [---salination---] if centred.
# [C-crank sonar---]      [-C-crank sonar--]
# This is used to validate the suitability of generated control names for a
# target 16x2 LCD and action instructions for three lines of a target 20x4
# display.
def countLines(control, width):
    lines = 1
    linelen=0
    for word in control.split(' '):
        if linelen + len(word) < width:
            linelen += len(word) + 1
        else:
            lines += 1
            linelen = len(word)
    return lines

# Generate a random control name
def getControlName(maxwidth, maxlines, minlen):
    finished=False
    while not finished:
        ret = (random.choice(['','',random.choice(adjectives).lower()+' ',
                random.choice(adjectives).lower()+' ', random.choice(adjectives).lower()+' ',
                random.choice(prefixtoothed).lower() +random.choice(suffixtoothed)+ ' '])
                +random.choice(['','',random.choice(letters), 
                random.choice(greekletters).lower()])+random.choice(baseparts).lower()
                +random.choice(['','','',' '+random.choice(baseparts).lower()]))
        if countLines(ret, maxwidth) <= maxlines and len(ret) >= minlen:
            finished=True
    return ret

# Describe an action suitable for a button
def getButtonAction(control):
    finished=False
    while not finished:
        ret = random.choice(verbs) + ' the ' + control
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Describe an action suitable for a toggle
def getToggleAction(control, targetstate):
    finished=False
    while not finished:
        if targetstate:
            ret = random.choice(onwords)
        else:
            ret = random.choice(offwords)
        ret += ' the ' + control
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Describe an action suitable for a selector
def getSelectorAction(control, numrange, targetnum, currentnum):
    finished=False
    while not finished:
        choices = ['Set ' + control + ' to ' + str(targetnum)]
        if targetnum > currentnum:
            changeword = 'Increase'
        else:
            changeword = 'Decrease'
        choices.append(changeword + ' ' + control + ' to ' + str(targetnum))
        if targetnum == max(numrange):
            choices.append(random.choice(['Set ','Increase ']) + control + ' to ' + random.choice(['maximum', '100%', 'full power']))
        if targetnum == min(numrange):
            choices.append(random.choice(['Set ','Decrease ']) + control + ' to ' + random.choice(['minimum', '0%', 'off']))
        ret = random.choice(choices)
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Describe an action suitable for a colour
def getColourAction(control, targetcolour):
    finished=False
    while not finished:
        ret = 'Set ' + control + ' to ' + random.choice(['','','','code ', 'condition ', 'status ']) + targetcolour + random.choice(['','','',' alert'])
        if countLines(ret, 20) <= 3:
            finished = True
    return str(ret)

# Describe an action suitable for a verb list choice
def getVerbListAction(control, targetverb):
    return targetverb + ' the ' + control

# Describe an action suitable for a word
def getWordAction(control, targetword):
    finished = False
    while not finished:
        ret = (random.choice(['Set ' + control + ' to \'' + targetword + '\'',
                              'Select \'' + targetword + '\' on ' + control]))
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Describe an action suitable for a numpad password action
def getPasswdAction(control, targetpasswd):
    finished = False
    while not finished:
        ret = (random.choice(['Set ' + control + ' to \'' + targetpasswd + '\'',
                              'Type \'' + targetpasswd + random.choice(['\' on ','\' into ','\' onto ']) + control,
                              'Key \'' + targetpasswd + '\' into ' + control,
                              control + ' password is \'' + targetpasswd + '\'']))
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

#Describe a pin entry action
def getPinAction(control, targetpin):
    finished = False
    while not finished:
        ret = (random.choice(['Set ' + control + ' to \'' + targetpasswd + '\'',
                              'Enter \'' + targetpasswd + random.choice(['\' on ','\' into ','\' onto ']) + control,
                              'Key \'' + targetpasswd + '\' into ' + control,
                              control + ' pin is \'' + targetpin + '\'']))
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Generate a random action
def getRandomAction(control):
    return random.choice([getButtonAction(control), getToggleAction(control, random.choice(range(2))),
                          getSelectorAction(control, range(11), random.choice(range(11)),random.choice(range(11))),
                          getColourAction(control, random.choice(colours)),
                          getWordAction(control, random.choice(safewords)),
                          getPasswdAction(control, random.choice(passwd))])

#Get a random emergency
def getEmergency():
    finished=False
    while not finished:
        n = random.choice(range(5))
        if n==0: #is {goingto} {badplace}
            em = "is " + random.choice(emergencies['goingto']) + " " + random.choice(emergencies['badplace'])
        elif n==1: #is {attackedby} {badpeople}
            em = "is " + random.choice(emergencies['attackedby']) + " " + random.choice(emergencies['badpeople'])
        elif n==2: #is {losing} {neededresource}
            em = "is " + random.choice(emergencies['losing']) + " " + random.choice(emergencies['neededresource'])
        elif n==3: #is {leaking} {fluid}
            em = "is " + random.choice(emergencies['leaking']) + " " + random.choice(emergencies['fluid'])
        elif n==4: #has a {broken} {device}
            em = "has " + random.choice(emergencies['broken']) + " " + random.choice(emergencies['device'])
        ret = random.choice(["Emergency","Warning","Danger","Don't Panic","Red Alert","SOS"]) + " - the ship " + em + "! Stand by!"
        if countLines(ret, 20) <= 4:
            finished = True
    return ret

# Get 50 controls
def get50Controls():
    for i in range(50):
        print(getControlName(16,2,12))
        
# Get 50 actions
def get50Actions():
    for i in range(50):
        print(getRandomAction(getControlName(16,2,12)))
        

#Get 50 emergencies
def get50Emergencies():
    for i in range(50):
        print(getEmergency())
        
