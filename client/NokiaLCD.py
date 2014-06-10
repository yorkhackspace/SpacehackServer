"""Class instance wrapper for Nokia LCDs with a PCD8544 controller
This should be duck-type polymorphic with the calls used for the
hd44780 LCDs so we can write to either

York Hackspace January 2014
"""

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI


class NokiaLCD:
    """Wrapper for the NokiaLCD to support many on common
    SPI bus"""
    def __init__(self, pin_DC="P9_26", pin_RST="P9_25",
                 pin_SCE="P9_11", contrast=0xbb):
        self.SCE = pin_SCE
        spi_port = 0
        spi_device = 0
        spi = SPI.SpiDev(spi_port, spi_device, max_speed_hz=4000000)
        self.lcd = LCD.PCD8544(pin_DC, pin_RST, spi)
        self.contrast = contrast
        GPIO.setup(pin_SCE, GPIO.OUT)
        GPIO.output(pin_SCE, GPIO.HIGH)
        self.width = 1
        self.height = 1

    def reset_all_displays(self):
        """This will reset all the connected displays"""
        self.lcd.reset()

    def select_display(self):
        """Set display to receive a command"""
        GPIO.output(self.SCE, GPIO.LOW)

    def unselect_display(self):
        """Set display to stop receiving commands"""
        GPIO.output(self.SCE, GPIO.HIGH)

    def display_init(self):
        """Setup the display bias and contrast"""
        self.select_display()
        self.lcd.set_bias(4)
        self.lcd.set_contrast(self.contrast)
        self.unselect_display()

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
        GPIO.output(self.SCE, GPIO.LOW)
        PCD.set_contrast(self.contrast)
        GPIO.output(self.SCE, GPIO.HIGH)
