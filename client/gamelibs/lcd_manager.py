#spacehack game client LCD handling utility library

import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from NokiaLCD import NokiaLCD

lcd={}

def initLCDs(sortedlist, config):
    for ctrlid in sortedlist:
        dispdef = config['local']['controls'][ctrlid]['display']
        if dispdef['type'] == 'hd44780':
	        newlcd = Adafruit_CharLCD()
	        newlcd.pin_e = dispdef['pin']
	        GPIO.setup(newlcd.pin_e, GPIO.OUT)
	        GPIO.output(newlcd.pin_e, GPIO.LOW)
	        newlcd.begin(dispdef['width'], dispdef['height'])
	        lcd[ctrlid]=newlcd
	        print("Control " + ctrlid + " is hd44780 on pin " + newlcd.pin_e)
        else:
	        newlcd = NokiaLCD(pin_SCE=dispdef['pin'])
	        lcd[ctrlid]=newlcd
	        print("Control " + ctrlid + " is nokia on pin " + dispdef['pin'])
    return lcd

#Display a timer bar on the bottom row of the instructions display
def displayTimer(timeoutstarted, timeoutdisplayblocks):
    """Display a timer bar on the bottom row of the instructions display"""
    global timeoutdisplayblocks
    if timeoutstarted == 0.0:
        blockstodisplay = 0
    else:
        timesincetimeout = time.time() - timeoutstarted
        if timesincetimeout > roundconfig['timeout']:
            blockstodisplay = 0
        else:
            blockstodisplay = int(0.5 + 20 * (1 - (timesincetimeout / roundconfig['timeout'])))
        #Work out diff between currently displayed blocks and intended, to minimise amount to draw
        if blockstodisplay > timeoutdisplayblocks:
            lcd["0"].setCursor(timeoutdisplayblocks, 3)
            lcd["0"].message((blockstodisplay - timeoutdisplayblocks) * chr(255))
        elif timeoutdisplayblocks > blockstodisplay:
            lcd["0"].setCursor(blockstodisplay, 3)
            lcd["0"].message((timeoutdisplayblocks - blockstodisplay ) * ' ')
        timeoutdisplayblocks = blockstodisplay

#Pretty print to the LCDs taking into account width
def display(message, width, ctrlid):
    """Pretty print to the LCDs taking into account width"""
    words = message.split(" ")
    line = ""
    pos=0
    lcd[ctrlid].clear()
    for word in words:
        if len(line) + len(word) > width:
            lcd[ctrlid].setCursor(0, pos)
            lcd[ctrlid].message(line.rstrip() + '\n')
            line = word + " "
            pos += 1
        else:
            line += word + " "
    lcd[ctrlid].setCursor(0, pos)
    lcd[ctrlid].message(line.rstrip())
