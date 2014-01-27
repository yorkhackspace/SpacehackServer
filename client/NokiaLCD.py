# Class instance wrapper for Nokia LCDs
# York Hackspace January 2014

import Adafruit_BBIO.GPIO as GPIO
import PCD8544_BBB as PCD

class NokiaLCD:
    def __init__(self, pin_DC="P9_26", pin_RST="P9_25", pin_LED="P9_27",
                 pin_SCE="P9_11", pin_SCLK="P9_14", pin_DIN="P9_12"):
        self.DC, self.RST, self.LED = pin_DC, pin_RST, pin_LED
        self.SCE, self.SCLK, self.DIN = pin_SCE, pin_SCLK, pin_DIN
        PCD.SCE=self.SCE
        PCD.init()

    def display(self, displaytext):
        PCD.SCE=self.SCE
        PCD.text(displaytext)

    def cls(self):
        PCD.SCE=self.SCE
        PCD.cls()

    def goto(self, row, column):
        PCD.SCE=self.SCE
        PCD.gotorc(row, column)
