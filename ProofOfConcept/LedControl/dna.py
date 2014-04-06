#Quick test of LedControl library
import LedControl
from math import sin, pi, cos
from time import sleep
import threading

class DNA(threading.Thread):
    def __init__(self, pinData = "P9_11", pinClock = "P9_13", pinCS = "P9_15", increment = 0.3, delay = 10, showdna = True, gap = 1):
        self.GAP = gap
        self.INCREMENT = increment
        self.DELAY = delay
        self.SHOWDNA = showdna

        self.lc = LedControl.LedControl(pinData, pinClock, pinCS, 1)
    
        self.lc.shutdown(0, False)
        self.lc.setIntensity(0, 15)
        self.lc.clearDisplay(0)
    
        self.x = 0.0
        self.c = 0
        self.ledBuffer = [0 for i in range(8)]

    def run(self):
        while True:
            #Shuffle down
            for i in range(7):
                self.ledBuffer[7-i] = self.ledBuffer[6-i]
            pos = int((sin(self.x) + 1.0) * 4.0)
            self.ledBuffer[0] = 1 << pos
            
            if self.SHOWDNA:
                pos2 = int((cos(self.x + 0.6) + 1.0) * 4.0)
                self.ledBuffer[0] |= 1 << pos2
                
                if self.c == self.GAP: #Draw the connecting bar
                    if pos2 < pos:
                        pos, pos2 = pos2, pos
                    for i in range(pos, pos2):
                        self.ledBuffer[0] |= 1 << i
                    self.c = 0
                else:
                    self.c += 1
        
            for i in range(8):
                self.lc.setRow(0, i, self.ledBuffer[i])
            self.x += self.INCREMENT
            sleep(self.DELAY / 1000.0)

if __name__ == '__main__':
    dna = DNA()
    dna.run()
    
    while True:
        sleep(100)
