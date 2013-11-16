# Simple demo for reverse-engineered technobabble control and action generation.
# This is probably a bit too wordy at the minute as I've not got any weightings
# in the choices.

import random

def readWordList(filename):
    f=open('words/' + filename)
    ret = f.read().replace('\r','').split('\n')
    f.close
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
def getControlName():
    finished=False
    while not finished:
        ret = (random.choice(['','',random.choice(adjectives).lower()+' ',
                random.choice(adjectives).lower()+' ',
                random.choice(prefixtoothed).lower() +random.choice(suffixtoothed)+ ' '])
                +random.choice(['','',random.choice(letters), 
                random.choice(greekletters).lower()])+random.choice(baseparts).lower()
                +random.choice(['','','',' '+random.choice(baseparts).lower()]))
        if countLines(ret, 16) <= 2 and len(ret) >= 12:
            finished=True
    return ret

# Generate a random action suitable for a button
def getButtonAction(control):
    finished=False
    while not finished:
        ret = random.choice(verbs) + ' the ' + control
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Generate a random action suitable for a toggle
def getToggleAction(control):
    finished=False
    while not finished:
        ret = (random.choice([random.choice(onwords),random.choice(offwords)])
                + ' the ' + control)
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Generate a random action suitable for a selector
def getSelectorAction(control):
    finished=False
    while not finished:
        ret = (random.choice([random.choice(['Set ','']) + control + ' to '
                   + random.choice([str(random.choice(range(11))), 'full power', 'maximum', '50%']),
                   'Increase ' + control + ' to ' + str(random.choice(range(11))),
                   'Decrease ' + control + ' to ' + str(random.choice(range(11)))]))
        if countLines(ret, 20) <= 3:
            finished = True
    return ret

# Generate a random action
def getRandomAction(control):
    return random.choice([getButtonAction(control), getToggleAction(control), getSelectorAction(control)])

# Get 50 controls
def get50Controls():
    for i in range(50):
        print(getControlName())
        
# Get 50 actions
def get50Actions():
    for i in range(50):
        print(getRandomAction(getControlName()))
        

#get50Actions()
