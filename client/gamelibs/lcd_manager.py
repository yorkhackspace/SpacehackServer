#spacehack game client LCD handling utility library

import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from NokiaLCD import NokiaLCD
import time

class LcdManager(object):
    lcd = {}

    def __init__(self, sortedlist, config):
        nokia_lcds = []
        #get bus pins first
        hd44780bus = config['local']['buses']['hd44780']
        nokiabus = config['local']['buses']['nokia']
        hd44780data_pins = []
        for i in range(8):
            thispin = 'LCD_D'+str(i)
            if thispin in hd44780bus:
                hd44780data_pins.append(hd44780bus[thispin])

        for ctrlid in sortedlist:
            dispdef = config['local']['controls'][ctrlid]['display']
            if dispdef['type'] == 'hd44780':


                newlcd = Adafruit_CharLCD(pin_rs = hd44780bus['LCD_RS'], pins_db=hd44780data_pins)
                newlcd.pin_e = dispdef['pin']
                GPIO.setup(newlcd.pin_e, GPIO.OUT)
                GPIO.output(newlcd.pin_e, GPIO.LOW)
                newlcd.begin(dispdef['width'], dispdef['height'])
                self.lcd[ctrlid] = newlcd
                print "Control %s is hd44780 on pin %s" % (ctrlid, newlcd.pin_e)
            else:
                if "contrast" in dispdef:
                    contrast = int(dispdef['contrast'])
                else:
                    contrast = 0xbb
                newlcd = NokiaLCD(pin_SCE=dispdef['pin'], contrast=contrast)
                newlcd.width = dispdef['width']
                newlcd.height = dispdef['height']
                newlcd.display_init()
                self.lcd[ctrlid] = newlcd
                nokia_lcds.append(newlcd)
                print "Control %s is nokia on pin %s" % (ctrlid, dispdef['pin'])
        # Do this now as it does not work in the big loop for some reason.
        if len(nokia_lcds) > 0:
            nokia_lcds[0].reset_all_displays()
            for nokia_lcd in nokia_lcds:
                nokia_lcd.disaply()


    mytimeoutdisplayblocks = 0

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

    def display(self, message, width, ctrlid, doClear=True):
        """Pretty print to the LCDs taking into account width"""
        words = message.split(" ")
        line = ""
        pos = 0
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

    def displayButtonsLine(self, leftstr, rightstr, ctrlid):
        """Display words on the left and right sides of the bottom row, for Nokia displays"""
        lcd_width = self.lcd[ctrlid].width
        lcd_height = self.lcd[ctrlid].height
        combinedstr = leftstr + " "*(lcd_width - len(leftstr) - len(rightstr)) + rightstr
        self.lcd[ctrlid].setCursor(0, lcd_height-1)
        self.lcd[ctrlid].message(combinedstr)

    def displayValueLine(self, valuestr, ctrlid):
        """Display values centred on the fourth row, for Nokia displays"""
        lcd_width = self.lcd[ctrlid].width
        lcd_height = self.lcd[ctrlid].height
        if lcd_height > 4:
            leftpad = (lcd_width - len(valuestr)) // 2
            combinedstr = (" " * leftpad) + valuestr + (" " * (lcd_width - len(valuestr) - leftpad))
            self.lcd[ctrlid].setCursor(0, lcd_height-3)
            self.lcd[ctrlid].message(combinedstr)
