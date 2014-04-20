# Class instance wrapper for Nokia LCDs with a PCD8544 controller
# This should be duck-type polymorphic with the calls used for the
# hd44780 LCDs so we can write to either 
# York Hackspace January 2014

import Adafruit_BBIO.GPIO as GPIO
import PCD8544_BBB as PCD

nokiasinitialised = False

class NokiaLCD:
    def __init__(self, pin_DC="P9_26", pin_RST="P9_25", pin_LED="P9_27",
                 pin_SCE="P9_11", pin_SCLK="P9_14", pin_DIN="P9_12", InContrast=0xbb):
        self.DC, self.RST, self.LED = pin_DC, pin_RST, pin_LED
        self.SCE, self.SCLK, self.DIN = pin_SCE, pin_SCLK, pin_DIN
        self.contrast = InContrast
        GPIO.setup(pin_SCE, GPIO.OUT)
        GPIO.output(pin_SCE, GPIO.HIGH)
        global nokiasinitialised
        if not nokiasinitialised:
            PCD.init()
            nokiasinitialised = True
            
    width = 1
    height = 1

    def getheight(self):
        return self.height
    
    def getwidth(self):
        return self.width

    def setheight(self, height):
        self.height = height
    
    def setwidth(self, width):
        self.width = width

    def message(self, displaytext):
        GPIO.output(self.SCE, GPIO.LOW)
        PCD.text(displaytext)
        GPIO.output(self.SCE, GPIO.HIGH)

    def clear(self):
        GPIO.output(self.SCE, GPIO.LOW)
        PCD.cls()
        GPIO.output(self.SCE, GPIO.HIGH)

    def setCursor(self, col, row):
        GPIO.output(self.SCE, GPIO.LOW)
        PCD.gotorc(row, col)
        GPIO.output(self.SCE, GPIO.HIGH)
        
    def setContrast(self):
        GPIO.output(pin_SCE, GPIO.LOW)
        PCD.set_contrast(contrast)
        GPIO.output(pin_SCE, GPIO.HIGH)
