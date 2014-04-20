#!/usr/bin/env python

import PCD8544_BBB as pc
import sys
import time

import Adafruit_BBIO.GPIO as GPIO


CE_0="P9_11"
CE_1="P9_13"
CE_2="P9_15"
GPIO.setup(CE_0, GPIO.OUT)
GPIO.setup(CE_1, GPIO.OUT)
GPIO.setup(CE_2, GPIO.OUT)

pc.init()

GPIO.output(CE_0, GPIO.LOW)
GPIO.output(CE_1, GPIO.LOW)
GPIO.output(CE_2, GPIO.LOW)

pc.screenInit()

GPIO.output(CE_1, GPIO.HIGH)
GPIO.output(CE_2, GPIO.HIGH)

raw_input("sdf")
f=0
while True:
    GPIO.output(CE_0, GPIO.LOW)
    time.sleep(0.1)
    pc.text("LCD 0")
    pc.text("%s" % f )
    f  = f + 1
    time.sleep(0.1)
    GPIO.output(CE_0, GPIO.HIGH)
    GPIO.output(CE_1, GPIO.LOW)
    time.sleep(0.1)
    pc.text("LCD 1")
    time.sleep(0.1)
    GPIO.output(CE_1, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(CE_2, GPIO.LOW)
    time.sleep(0.1)
    pc.text("LCD 2")
    time.sleep(0.1)
    GPIO.output(CE_2, GPIO.HIGH)
