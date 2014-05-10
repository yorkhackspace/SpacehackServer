#spacehack game client LCD handling utility library

import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from NokiaLCD import NokiaLCD
import PCD8544_BBB as PCD
import time

class LcdManager(object):
    lcd={}

    def __init__(self, sortedlist, config):
        SCEPins = []
        #get bus pins first
        hd44780bus = config['local']['buses']['hd44780']
        nokiabus = config['local']['buses']['nokia']
        hd44780data_pins = []
        for i in range(8):
            thispin = 'LCD_D'+str(i)
            if (thispin) in hd44780bus:
                hd44780data_pins.append(hd44780bus[thispin])

        for ctrlid in sortedlist:
            dispdef = config['local']['controls'][ctrlid]['display']
            if dispdef['type'] == 'hd44780':
		        
                
                newlcd = Adafruit_CharLCD(pin_rs = hd44780bus['LCD_RS'], pins_db=hd44780data_pins)
                newlcd.pin_e = dispdef['pin']
                GPIO.setup(newlcd.pin_e, GPIO.OUT)
                GPIO.output(newlcd.pin_e, GPIO.LOW)
                newlcd.begin(dispdef['width'], dispdef['height'])
                self.lcd[ctrlid]=newlcd
                print("Control " + ctrlid + " is hd44780 on pin " + newlcd.pin_e)
            else:
                if "contrast" in dispdef:
                    myContrast = int(dispdef['contrast'])
                else:
                    myContrast = 0xbb
                newlcd = NokiaLCD(pin_SCE=dispdef['pin'], InContrast=myContrast)
                newlcd.setwidth(dispdef['width'])
                newlcd.setheight(dispdef['height'])
                self.lcd[ctrlid]=newlcd
                print("Control " + ctrlid + " is nokia on pin " + dispdef['pin'])
                SCEPins.append(dispdef['pin'])
        for pin in SCEPins:
            GPIO.output(pin, GPIO.LOW)
        PCD.screenInit()
        for pin in SCEPins:
            GPIO.output(pin, GPIO.HIGH)
        for ctrlid in sortedlist:
            dispdef = config['local']['controls'][ctrlid]['display']
            if dispdef['type'] == 'nokia':
                self.lcd[ctrlid].setContrast()

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
            elif self.mytimeoutdisplayblocks > blockstodisplay:
                self.lcd["0"].setCursor(blockstodisplay, 3)
                self.lcd["0"].message((self.mytimeoutdisplayblocks - blockstodisplay ) * ' ')
            self.mytimeoutdisplayblocks = blockstodisplay
            
            
    def clear(self, ctrlid):
        self.lcd[ctrlid].clear()

    #Pretty print to the LCDs taking into account width
    def display(self, message, width, ctrlid, doClear=True):
        """Pretty print to the LCDs taking into account width"""
        words = message.split(" ")
        line = ""
        pos=0
        if doClear:
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
        lcdWidth = self.lcd[ctrlid].getwidth()
        lcdHeight = self.lcd[ctrlid].getheight()
        combinedstr = leftstr + " "*(lcdWidth - len(leftstr) - len(rightstr)) + rightstr
        self.lcd[ctrlid].setCursor(0, lcdHeight-1)
        self.lcd[ctrlid].message(combinedstr)

	#Display values centred on the fourth row, for Nokia displays
    def displayValueLine(self, valuestr, ctrlid):
        """Display values centred on the fourth row, for Nokia displays"""
        lcdWidth = self.lcd[ctrlid].getwidth()
        lcdHeight = self.lcd[ctrlid].getheight()
        if lcdHeight > 4:
            leftpad = (lcdWidth - len(valuestr)) // 2
            combinedstr = (" " * leftpad) + valuestr + (" " * (lcdWidth - len(valuestr) - leftpad))
            self.lcd[ctrlid].setCursor(0, lcdHeight-3)
            self.lcd[ctrlid].message(combinedstr)
