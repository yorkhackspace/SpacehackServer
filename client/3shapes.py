#!/usr/bin/env python

import time
from time import sleep

import Adafruit_Nokia_LCD as LCD
#import PCD8544_BBB as LCD
import Adafruit_GPIO.SPI as SPI
import Adafruit_BBIO.GPIO as GPIO

print (LCD.__file__)

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#
DC = 'P9_15'
RST = 'P9_12'
SPI_PORT = 1
SPI_DEVICE = 0

CE0="P9_23"
CE1="P9_24"
CE2="P9_25"
#CES=[CE0, CE1, CE2]
CES=[CE2,CE0,CE1]

print LCD.LCDWIDTH, LCD.LCDHEIGHT

for CE in CES:
    print("Set CE " + CE)
    GPIO.setup(CE, GPIO.OUT)
    GPIO.output(CE, GPIO.HIGH)

print("reset")
disp = LCD.PCD8544(DC, RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=4000000))
disp.reset()

for CE in CES:
    GPIO.output(CE, GPIO.HIGH)
    print("Disable CE " + CE)

contrasts=[50, 60, 60]
# Setup all the displays
tc=0

#for CE in CES:
#    GPIO.output(CE, GPIO.LOW)
#    disp.begin(contrast=60)
#    GPIO.output(CE, GPIO.HIGH)

for CE in CES:
    GPIO.output(CE, GPIO.LOW)

#for CE in CES:
#    print("Reset display with CE " + CE)
#    GPIO.output(CE, GPIO.LOW)
    #disp.begin(contrast=contrasts[tc])
#    disp.begin(contrast=170)
#    tc=tc+1
#    disp.clear()
#    disp.display()
#    GPIO.output(CE, GPIO.HIGH)
disp.begin(contrast=60)
disp.clear()
disp.display()

for CE in CES:
    GPIO.output(CE, GPIO.HIGH)

tc=0
for CE in CES:
    GPIO.output(CE, GPIO.LOW)
    disp.set_contrast(contrasts[tc])
    tc = tc + 1
    GPIO.output(CE, GPIO.HIGH)

image = Image.new('1', (LCD.LCDWIDTH, LCD.LCDHEIGHT))

draw = ImageDraw.Draw(image)

# empty box
def empty():
    draw.rectangle((0,0,LCD.LCDWIDTH,LCD.LCDHEIGHT), outline=255, fill = 255)

font = ImageFont.load_default()
def box(x,y,text):
    draw.rectangle((0+x,0+y,32+x,22+y), outline=0, fill=255)
    draw.text((2+x, 2+y), text, font=font)
  

#draw.ellipse((2,2,22,22), outline=0, fill=255)
#draw.rectangle((24,2,44,22), outline=0, fill=255)

def write_image(display):
    GPIO.output(display, GPIO.LOW)
    disp.image(image)
    disp.display()
    GPIO.output(display, GPIO.HIGH)

xoffset = 0
dir = 1
while True:
   for CE in CES:
       empty()
       box(xoffset,2,CE)
       write_image(CE)
   xoffset += dir
   if xoffset > 48 or xoffset < 0:
       dir = -dir
  
