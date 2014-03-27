#spacehack game client LCD handling utility library

import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from NokiaLCD import NokiaLCD
import time

class LcdManager(object)
    lcd={}

    def __init__(self, sortedlist, config):
        for ctrlid in sortedlist:
        dispdef = config['local']['controls'][ctrlid]['display']
        if dispdef['type'] == 'hd44780':
            newlcd = Adafruit_CharLCD()
            newlcd.pin_e = dispdef['pin']
            GPIO.setup(newlcd.pin_e, GPIO.OUT)
            GPIO.output(newlcd.pin_e, GPIO.LOW)
            newlcd.begin(dispdef['width'], dispdef['height'])
            self.lcd[ctrlid]=newlcd
            print("Control " + ctrlid + " is hd44780 on pin " + newlcd.pin_e)
        else:
            newlcd = NokiaLCD(pin_SCE=dispdef['pin'])
            newlcd.setwidth(dispdef['width'])
            newlcd.setheight(dispdef['height'])
            self.lcd[ctrlid]=newlcd
            print("Control " + ctrlid + " is nokia on pin " + dispdef['pin'])

    mytimeoutdisplayblocks = 0

    #Display a timer bar on the bottom row of the instructions display
    def displayTimer(self, timeoutstarted, resetBlocks, timeout):
        """Display a timer bar on the bottom row of the instructions display"""
        if resetBlocks:
        self.mytimeoutdisplayblocks = 0

        if timeoutstarted == 0.0:
        self.mytimeoutdisplayblocks = 0
        else:
        timesincetimeout = time.time() - timeoutstarted
        if timesincetimeout > timeout:
            blockstodisplay = 0
        else:
            blockstodisplay = int(0.5 + 20 * (1 - (timesincetimeout / timeout)))       
        #Work out diff between currently displayed blocks and intended, to minimise amount to draw
        if blockstodisplay > self.mytimeoutdisplayblocks:
            self.lcd["0"].setCursor(0, 3)
            self.lcd["0"].message((blockstodisplay) * chr(255))
        elif mytimeoutdisplayblocks > blockstodisplay:
            self.lcd["0"].setCursor(blockstodisplay, 3)
            self.lcd["0"].message((self.mytimeoutdisplayblocks - blockstodisplay ) * ' ')
        self.mytimeoutdisplayblocks = blockstodisplay

    #Pretty print to the LCDs taking into account width
    def display(self, message, width, ctrlid):
        """Pretty print to the LCDs taking into account width"""
        words = message.split(" ")
        line = ""
        pos=0
        self.lcd[ctrlid].clear()
        for word in words:
        if len(line) + len(word) > width:
            self.lcd[ctrlid].setCursor(0, pos)
            self.lcd[ctrlid].message(line.rstrip() + '\n')
            line = word + " "
            pos += 1
        else:
            line += word + " "
        self.lcd[ctrlid].setCursor(0, pos)
        self.lcd[ctrlid].message(line.rstrip())

    #Display words on the left and right sides of the bottom row, for Nokia displays
    def displayButtonsLine(self, leftstr, rightstr, ctrlid):
        """Display words on the left and right sides of the bottom row, for Nokia displays"""
        lcdWidth = self.lcd[crtlid].getwidth()
        lcdHeight = self.lcd[crtlid].getheight()
        combinedstr = leftstr + " "*(lcdWidth - len(leftstr) - len(rightstr)) + rightstr
        self.lcd[ctrlid].setCursor(0, lcdHeight-1)
        self.lcd[ctrlid].message(combinedstr)

	#Display values centred on the fourth row, for Nokia displays
    def displayValueLine(self, valuestr, ctrlid):
        """Display values centred on the fourth row, for Nokia displays"""
        lcdWidth = self.lcd[crtlid].getwidth()
        lcdHeight = self.lcd[crtlid].getheight()
        if lcdHeight > 4:
        leftpad = (lcdWidth - len(valuestr)) // 2
        combinedstr = (" " * leftpad) + valuestr + (" " * (lcdWidth - len(valuestr) - leftpad))
        self.lcd[ctrlid].setCursor(0, lcdHeight-3)
        self.lcd[ctrlid].message(combinedstr)
