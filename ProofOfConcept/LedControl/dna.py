#Quick test of LedControl library
import LedControl
from math import sin, pi
from time import sleep

INCREMENT = 0.3
GAP = 1
DELAY = 50
SHOWDNA = True

pinData = "P9_11"
pinClock = "P9_13"
pinCS = "P9_15"

lc = LedControl.LedControl(pinData, pinClock, pinCS, 1)

lc.shutdown(0, False)
lc.setIntensity(0, 15)
lc.clearDisplay(0)
lc.setLed(0, 2, 3, 1)
lc.setRow(0, 0, 127)

x = 0.0
c = 0
ledBuffer = [0 for i in range(8)]

while True:
    #Shuffle down
    for i in range(7):
        ledBuffer[7-i] = ledBuffer[6-i]
    pos = int((sin(x) + 1.0) * 4.0)
    ledBuffer[0] = 1 << pos
    
    #dna stuff
    
    for i in range(8):
        lc.setRow(0, i, ledBuffer[i])
    x += INCREMENT
    sleep(1000.0 / DELAY)
