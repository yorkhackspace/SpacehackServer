#spacehack game client LCD handling utility library

import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from NokiaLCD import NokiaLCD
import time

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

mytimeoutdisplayblocks = 0

#Display a timer bar on the bottom row of the instructions display
def displayTimer(timeoutstarted, resetBlocks, timeout):
    """Display a timer bar on the bottom row of the instructions display"""
    global mytimeoutdisplayblocks
    if resetBlocks:
        mytimeoutdisplayblocks = 0

    if timeoutstarted == 0.0:
        mytimeoutdisplayblocks = 0
    else:
        timesincetimeout = time.time() - timeoutstarted
        if timesincetimeout > timeout:
            blockstodisplay = 0
        else:
            blockstodisplay = int(0.5 + 20 * (1 - (timesincetimeout / timeout)))       
        #Work out diff between currently displayed blocks and intended, to minimise amount to draw
        if blockstodisplay > mytimeoutdisplayblocks:
            lcd["0"].setCursor(0, 3)
            lcd["0"].message((blockstodisplay) * chr(255))
        elif mytimeoutdisplayblocks > blockstodisplay:
            lcd["0"].setCursor(blockstodisplay, 3)
            lcd["0"].message((mytimeoutdisplayblocks - blockstodisplay ) * ' ')
        mytimeoutdisplayblocks = blockstodisplay

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
