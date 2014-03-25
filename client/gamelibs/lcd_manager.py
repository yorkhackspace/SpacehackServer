#spacehack game client LCD handling utility library

import Adafruit_BBIO.GPIO as GPIO
from Adafruit_CharLCD import Adafruit_CharLCD
from NokiaLCD import NokiaLCD

lcd={}

def initLCDs(sortedlist, config):
    for ctrlid in sortedlist:
        dispdef = config['local']['controls'][ctrlid]['display']
        if dispdef['type'] == 'hd44780':
	        newlcd = Adafruit_CharLCD()
	        newlcd.pin_e = dispdef['pin']
	        GPIO.setup(newlcd.pin_e, GPIO.OUT)
	        GPIO.output(newlcd.pin_e, GPIO.LOW)
	        newlcd.begin(dispdef['width'], dispdef['height'])
	        lcd[ctrlid]=newlcd
	        print("Control " + ctrlid + " is hd44780 on pin " + newlcd.pin_e)
        else:
	        newlcd = NokiaLCD(pin_SCE=dispdef['pin'])
	        lcd[ctrlid]=newlcd
	        print("Control " + ctrlid + " is nokia on pin " + dispdef['pin'])
    return lcd
