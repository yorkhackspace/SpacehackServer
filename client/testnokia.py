#!/usr/bin/env python

import PCD8544_BBB as pc
import sys
import time

import Adafruit_BBIO.GPIO as GPIO


CE_0="P9_23"
CE_1="P9_25"
GPIO.setup(CE_0, GPIO.OUT)
GPIO.setup(CE_1, GPIO.OUT)

GPIO.output(CE_0, GPIO.HIGH)
GPIO.output(CE_1, GPIO.HIGH)


pc.init()

GPIO.output(CE_1, GPIO.LOW)

raw_input("sdf")
f=0
while True:
    GPIO.output(CE_0, GPIO.HIGH)
    time.sleep(0.1)
    pc.text("John is Ace!")
    pc.text("%s" % f )
    f  = f + 1
    time.sleep(0.1)
    GPIO.output(CE_0, GPIO.LOW)
    GPIO.output(CE_1, GPIO.HIGH)
    time.sleep(0.1)
    pc.text("HackSpace!")
    time.sleep(0.1)
    GPIO.output(CE_1, GPIO.LOW)
    # time.sleep(0.1)
