#Console game client - proof of concept demo
#York Hackspace - Bob November 2013
#This runs on a Beaglebone Black

import mosquitto
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_7Segment import SevenSegment
from Adafruit_CharLCD import Adafruit_CharLCD
import socket

#Who am I?
ipaddress = socket.gethostbyname(socket.gethostname())

#MQTT client
client = mosquitto.Mosquitto("Game-" + ipaddress) #client ID
server = "192.168.1.30" #fixed IP address of server

#Adafruit I2C 7-segment
segment = SevenSegment(address=0x70)

#Three HD44780 LCDs - 20x4 instructions display and two 16x2 control labels
lcd = [Adafruit_CharLCD(), Adafruit_CharLCD(), Adafruit_CharLCD()]
bar = ["P9_11", "P9_12", "P9_13", "P9_14", "P9_15", "P9_16", "P9_21", "P9_22", "P9_23", "P9_24"]

#Pretty print to the LCDs taking into account width
def display(message, width, screen):
    words = message.split(" ")
    line = ""
    pos=0
    lcd[screen].clear()
    for word in words:
        if len(line) + len(word) > width:
            lcd[screen].setCursor(0, pos)
            lcd[screen].message(line.rstrip() + '\n')
            line = word + " "
            pos += 1
        else:
            line += word + " "
    lcd[screen].setCursor(0, pos)
    lcd[screen].message(line.rstrip())

#Print to the 7-seg
def displayDigits(digits):
    disp = -len(digits) % 4 * ' ' + digits
    for i in range(4):
        digit=disp[i]
        if i < 2:
            idx = i
        else:
            idx = i+1
        if digit==' ':
            segment.writeDigitRaw(idx,0x0)
        if digit >= '0' and digit <= '9':
            segment.writeDigit(idx, ord(digit) - ord('0'))

#Bar graph
def barGraph(digit):
    for i in range(10):
        if digit > i:
            GPIO.output(bar[i], GPIO.HIGH)
        else:
            GPIO.output(bar[i], GPIO.LOW)

#MQTT message arrived
def on_message(mosq, obj, msg):
    print(msg.topic + " - " + str(msg.payload))
    if msg.topic == "instruction":
        display(str(msg.payload), 20, 0)
    if msg.topic == "control1":
        display(str(msg.payload), 16, 1)
    if msg.topic == "control2":
        display(str(msg.payload), 16, 2)
    if msg.topic == "digit1":
        displayDigits(str(msg.payload))
    if msg.topic == "digit2":
        barGraph(int(str(msg.payload)))

#Setup MQTT
client.on_message = on_message
client.connect(server)

client.subscribe("control1")
client.subscribe("control2")
client.subscribe("instruction")
client.subscribe("digit1")
client.subscribe("digit2")

#Setup displays
displayDigits('0000')
#LCDs share a data bus but have different enable pins
lcd[0].pin_e="P8_9"
lcd[0].begin(20, 4)
display("Awaiting instructions!", 20, 0)
lcd[1].pin_e="P8_16"
lcd[1].begin(16, 2)
display("Ready control 1!", 16, 1)
lcd[2].pin_e="P8_10"
lcd[2].begin(16, 2)
display("Ready control 2!", 16, 2)

#Setup Bar graph
for pin in bar:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
	
#Setup pot

#Setup button
	
#Set MQTT listening
client.loop_forever()
