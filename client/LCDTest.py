# SpaceHack! Game client main module
#York Hackspace January 2014
#This runs on a Beaglebone Black

import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD

#Three HD44780 LCDs - 20x4 instructions display and two 16x2 control labels
lcd = [Adafruit_CharLCD(), Adafruit_CharLCD(), Adafruit_CharLCD()]
lcdpins = ["P9_15", "P8_16", "P9_13"]

#Pretty print to the LCDs taking into account width
def display(message, width, screen):
    words = message.split(" ")
    line = ""
    pos=0
    lcd[screen].clear()
    for word in words:
        if len(line) + len(word) > width:
            lcd[screen].setCursor(0, pos)
            lcd[screen].message(line.rstrip() + '\n')
            line = word + " "
            pos += 1
        else:
            line += word + " "
    lcd[screen].setCursor(0, pos)
    lcd[screen].message(line.rstrip())

#Process an incoming config for a round
def processRoundConfig(roundconfigstring):
    roundconfig = json.loads(roundconfigstring)
    display(roundconfig['instructions'], 20, 0)
    for ctrlid in controlids:
        controlsetup = roundconfig[ctrlid]
        lcdwrite(controlsetup['name'], ctrlid)
        #there's more to setup of course

def displayBar(num):
    lcd[0].setCursor(0,3)
    lcd[0].message(chr(255)*num + ' '*(20-num))

#LCDs share a data bus but have different enable pins
for i in range(3):
	lcd[i].pin_e = lcdpins[i]
	GPIO.setup(lcdpins[i], GPIO.OUT)
	GPIO.output(lcdpins[i], GPIO.LOW)
	
lcd[0].begin(20, 4)
display("Awaiting instructions!", 20, 0)
lcd[1].begin(16, 2)
display("Ready control 1!", 16, 1)
lcd[2].begin(16, 2)
display("Ready control 2!", 16, 2)

for i in range(21):
    displayBar(i)

for i in range(21):
    displayBar(20-i)
