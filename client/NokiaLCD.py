"""Class instance wrapper for Nokia LCDs with a PCD8544 controller
This should be duck-type polymorphic with the calls used for the
hd44780 LCDs so we can write to either

York Hackspace January 2014
"""

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_Nokia_LCD as LCD
import Adafruit_GPIO.SPI as SPI
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class NokiaLCD:
    """Wrapper for the NokiaLCD to support many on common
    SPI bus"""
    def __init__(self, pin_DC="P9_26", pin_RST="P9_25",
                 pin_SCE="P9_11", contrast=0xbb):
        self.SCE = pin_SCE
        spi_port = 1
        spi_device = 0
        spi = SPI.SpiDev(spi_port, spi_device, max_speed_hz=4000000)
        self.lcd = LCD.PCD8544(pin_DC, pin_RST, spi=spi)
        self.contrast = contrast
        GPIO.setup(pin_SCE, GPIO.OUT)
        GPIO.output(pin_SCE, GPIO.HIGH)
        self.width = 84
        self.height = 48
        self.buffer = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))
        self.draw = ImageDraw.Draw(self.buffer)
        self.cursor = (0, 0)
        self.font = ImageFont.load_default()


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
        """Display a message at the current cursor"""
        self.draw.text(self.cursor, displaytext, font=self.font)
        self.display_buffer()

    def display_buffer(self):
        """Copy the buffer to the display"""
        self.select_display()
        self.lcd.image(self.buffer)
        self.lcd.display()
        self.unselect_display()

    def clear(self):
        """Clears the display"""
        self.select_display()
        self.lcd.clear()
        self.unselect_display()
        self.clear_buffer()

    def clear_buffer(self):
        """Clears the local buffer"""
        self.draw.rectangle((0, 0, 83, 47), outline=255, fill=255)

    def setCursor(self, col, row):
        self.cursor = (row * 6, col)

