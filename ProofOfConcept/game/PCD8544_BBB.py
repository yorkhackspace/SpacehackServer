# Nokia LCD driver for Beaglebone Black, adapted from code meant for Raspberry Pi
# Original WiringPi version by Xavier Berger
# Adaptation by York Hackspace Bob November 2013

import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
from Adafruit_BBIO.SPI import SPI
import time
from PIL import Image,ImageDraw,ImageFont
from nokiafont import FONT

# White backlight
CONTRAST = 0xaa

ROWS = 6
COLUMNS = 14
PIXELS_PER_ROW = 6
ON = 1
OFF = 0
BITBANG = True

#gpio's :
DC   = "P9_26"
RST  = "P9_25"
LED  = "P9_27"

# SPI connection
SCE  = "P9_17"
SCLK = "P9_22"
DIN  = "P9_18"


CLSBUF=[0]*(ROWS * COLUMNS * PIXELS_PER_ROW)

ORIGINAL_CUSTOM = FONT['\x7f']

def bit_reverse(value, width=8):
  result = 0
  for _ in xrange(width):
    result = (result << 1) | (value & 1)
    value >>= 1

  return result

BITREVERSE = map(bit_reverse, xrange(256))

spi = SPI(0,0)

def writebytes(value):
    if BITBANG:
      for byte in value:
        bits = bin(byte)[2:]
        bits = '0' * (8 - len(bits)) + bits
        GPIO.output(SCE, GPIO.HIGH)
        for bit in bits:
            if bit=='0':
                GPIO.output(DIN, GPIO.LOW)
            else:
                GPIO.output(DIN, GPIO.HIGH)
            GPIO.output(SCLK, GPIO.LOW)
            GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(SCE, GPIO.LOW)
    else:
        spi.writebytes(value)
        
def init(dev=(0,0),speed=4000000, brightness=256, contrast=CONTRAST):
    if BITBANG:
        for pin in [SCE, SCLK, DIN]:
            GPIO.setup(pi, GPIO.OUT)
    else:
        spi.open(dev[0],dev[1])
        #spi.max_speed_hz=speed

    # Set pin directions.
    for pin in [DC, RST]:
        GPIO.setup(pin, GPIO.OUT)

    # Toggle RST low to reset.
    GPIO.output(RST, GPIO.LOW)
    time.sleep(0.100)
    GPIO.output(RST, GPIO.HIGH)
    # Extended mode, bias, vop, basic mode, non-inverted display.
    set_contrast(contrast)

    # if LED == 1 set pin mode to PWM else set it to OUT
    if LED == 1:
        PWM.start(LED, 0)
    else:
        GPIO.setup(LED, GPIO.OUT)
        GPIO.output(LED, GPIO.LOW)
 


def lcd_cmd(value):
    GPIO.output(DC, GPIO.LOW)
    writebytes([value])


def lcd_data(value):
    GPIO.output(DC, GPIO.HIGH)
    writebytes([value])


def cls():
    gotoxy(0, 0)
    GPIO.output(DC, GPIO.HIGH)
    writebytes(CLSBUF)


def backlight(value):
    set_brightness(value * 100 / 255)


def set_brightness(led_value):
    if  LED == 1:
        if (0 <= led_value <= 100):
            PWM.set_duty_cycle(LED,led_value)
    else:
        if led_value == 0:
            GPIO.output(LED, GPIO.LOW)
        else:
            GPIO.output(LED, GPIO.HIGH)


def set_contrast(contrast):
    if ( 0x80 <= contrast < 0xFF):
        GPIO.output(DC, GPIO.LOW)
        writebytes([0x21, 0x14, contrast, 0x20, 0x0c])


def gotoxy(x, y):
    if ( (0 <= x < COLUMNS) and (0 <= y < ROWS)):
        GPIO.output(DC, GPIO.LOW)
        writebytes([x+128,y+64])


def gotorc(r, c):
    gotoxy(c*6,r)


def text(string, font=FONT):
    for char in string:
        display_char(char, font)


def centre_text(r, word):
    gotorc(r, max(0, (COLUMNS - len(word)) // 2))
    text(word)


def show_custom_char(font=FONT):
    display_char('\x7f', font)


def define_custom_char(values):
    FONT['\x7f'] = values


def restore_custom_char():
    define_custom_char(ORIGINAL_CUSTOM)


def alt_custom_char():
    define_custom_char([0x00, 0x50, 0x3C, 0x52, 0x44])


def pi_custom_char():
    define_custom_char([0x19, 0x25, 0x5A, 0x25, 0x19])


def display_char(char, font=FONT):
    try:
        GPIO.output(DC, GPIO.HIGH)
        writebytes(font[char]+[0])

    except KeyError:
        pass # Ignore undefined characters.


def load_bitmap(filename, reverse=False):
    mask = 0x00 if reverse else 0xff
    gotoxy(0, 0)
    with open(filename, 'rb') as bitmap_file:
        for x in xrange(6):
          for y in xrange(84):
            bitmap_file.seek(0x3e + y * 8 + x)
            lcd_data(BITREVERSE[ord(bitmap_file.read(1))] ^ mask)


def show_image(im):
    # Rotate and mirror the image
    rim = im.rotate(-90).transpose(Image.FLIP_LEFT_RIGHT)

    # Change display to vertical write mode for graphics
    GPIO.output(DC, GPIO.LOW)
    writebytes([0x22])

    # Start at upper left corner
    gotoxy(0, 0)
    # Put on display with reversed bit order
    GPIO.output(DC, GPIO.HIGH)
    writebytes( [ BITREVERSE[ord(x)] for x in list(rim.tostring()) ] )

    # Switch back to horizontal write mode for text
    GPIO.output(DC, GPIO.LOW)
    writebytes([0x20])
