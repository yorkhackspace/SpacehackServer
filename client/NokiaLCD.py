# Class instance wrapper for Nokia LCDs with a PCD8544 controller
# This should be duck-type polymorphic with the calls used for the
# hd44780 LCDs so we can write to either 
# York Hackspace January 2014

import Adafruit_BBIO.GPIO as GPIO
import PCD8544_BBB as PCD

nokiasinitialised = False

class NokiaLCD:
    def __init__(self, pin_DC="P9_26", pin_RST="P9_25", pin_LED="P9_27",
                 pin_SCE="P9_11", pin_SCLK="P9_14", pin_DIN="P9_12"):
        self.DC, self.RST, self.LED = pin_DC, pin_RST, pin_LED
        self.SCE, self.SCLK, self.DIN = pin_SCE, pin_SCLK, pin_DIN
        PCD.SCE=self.SCE
        GPIO.setup(pin_SCE, GPIO.OUT)
        GPIO.output(pin_SCE, GPIO.HIGH)
        global nokiasinitialised
        if not nokiasinitialised:
            PCD.init()
            nokiasinitialised = True

    def message(self, displaytext):
        PCD.SCE=self.SCE
        PCD.text(displaytext)

    def clear(self):
        PCD.SCE=self.SCE
        PCD.cls()

    def setCursor(self, col, row):
        PCD.SCE=self.SCE
        PCD.gotorc(row, col)
