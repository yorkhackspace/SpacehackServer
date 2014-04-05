#Quick test of LedControl library
import LedControl
from math import sin, pi, cos
from time import sleep

INCREMENT = 0.4
GAP = 1
DELAY = 10
SHOWDNA = True

pinData = "P9_11"
pinClock = "P9_13"
pinCS = "P9_15"

lc = LedControl.LedControl(pinData, pinClock, pinCS, 1)

lc.shutdown(0, False)
lc.setIntensity(0, 15)
lc.clearDisplay(0)

x = 0.0
c = 0
ledBuffer = [0 for i in range(8)]

while True:
    #Shuffle down
    for i in range(7):
        ledBuffer[7-i] = ledBuffer[6-i]
    pos = int((sin(x) + 1.0) * 4.0)
    ledBuffer[0] = 1 << pos
    
    if SHOWDNA:
        pos2 = int((cos(x + 0.6) + 1.0) * 4.0)
        ledBuffer[0] |= 1 << pos2
        
        c += 1
        if c == GAP: #Draw the connecting bar
            if pos2 < pos:
                pos, pos2 = pos2, pos
            for i in range(pos, pos2):
                ledBuffer[0] |= 1 << i
            c = 0

    for i in range(8):
        lc.setRow(0, i, ledBuffer[i])
    x += INCREMENT
    sleep(DELAY / 1000.0)
