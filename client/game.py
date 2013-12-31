#Console game client - proof of concept demo
#York Hackspace - Bob November 2013
#This runs on a Beaglebone Black

import mosquitto
import Adafruit_BBIO.GPIO as GPIO
from Adafruit_7Segment import SevenSegment
from Adafruit_CharLCD import Adafruit_CharLCD
import commands

#Who am I?
ipaddress = commands.getoutput("/sbin/ifconfig").split("\n")[1].split()[1][5:]

#MQTT client
client = mosquitto.Mosquitto("Game-" + ipaddress) #client ID
server = "192.168.1.30" #fixed IP address of server

#Adafruit I2C 7-segment
segment = SevenSegment(address=0x70)
lookup7segchar = {'0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66, '5': 0x6D,
                  '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F, ' ': 0x00, '_': 0x08,
                  'a': 0x5F, 'A': 0x77, 'b': 0x7C, 'B': 0x7C, 'c': 0x58, 'C': 0x39,
                  'd': 0x5E, 'D': 0x5E, 'e': 0x7B, 'E': 0x79, 'f': 0x71, 'F': 0x71,
                  'g': 0x6F, 'G': 0x3D, 'h': 0x74, 'H': 0x76, 'i': 0x04, 'I': 0x06,
                  'j': 0x1E, 'J': 0x1E, 'k': 0x08, 'K': 0x08, 'l': 0x06, 'L': 0x38,
                  'm': 0x08, 'M': 0x08, 'n': 0x54, 'N': 0x37, 'o': 0x5C, 'O': 0x3F,
                  'p': 0x73, 'P': 0x73, 'q': 0x67, 'Q': 0x67, 'r': 0x50, 'R': 0x31,
                  's': 0x6D, 'S': 0x6D, 't': 0x78, 'T': 0x78, 'u': 0x1C, 'U': 0x3E,
                  'v': 0x08, 'V': 0x07, 'w': 0x08, 'W': 0x08, 'x': 0x08, 'X': 0x08,
                  'y': 0x6E, 'Y': 0x6E, 'z': 0x5B, 'Z': 0x5B, '-': 0x40
                  }

#Three HD44780 LCDs - 20x4 instructions display and two 16x2 control labels
lcd = [Adafruit_CharLCD(), Adafruit_CharLCD(), Adafruit_CharLCD()]
lcdpins = ["P8_9", "P8_16", "P8_10"]

#Bar graph - didn't use a shift register because of space on breadboard
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
        segment.writeDigitRaw(idx,lookup7segchar[digit])
        
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

#Setup displays
displayDigits('0000')
#LCDs share a data bus but have different enable pins
for i in range(3):
	lcd[i].pin_e = lcdpins[i]
	GPIO.setup(lcdpins[i], GPIO.OUT)
	GPIO.output(lcdpins[i], GPIO.LOW)
	
lcd[0].begin(20, 4)
display("Awaiting instructions!", 20, 0)
lcd[1].begin(16, 2)
display("Ready control 1!", 16, 1)
lcd[2].begin(16, 2)
display("Ready control 2!", 16, 2)

#Setup Bar graph
for pin in bar:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
	
#Setup pot

#Setup button
	
#Setup MQTT
client.on_message = on_message
client.connect(server)

client.subscribe("control1")
client.subscribe("control2")
client.subscribe("instruction")
client.subscribe("digit1")
client.subscribe("digit2")

#Set MQTT listening
client.loop_forever()
