import sys
sys.path.append('./bigsevseg')
import Adafruit_MCP230xx as ExpIO
import time
print "imports done"
sevenSeg = ExpIO.Adafruit_MCP230XX(0x20, 16)
print "init done"
for i in range(0, 15):
    sevenSeg.config(i, ExpIO.Adafruit_MCP230XX.OUTPUT)

print "All pins set to output"

while True:
    print "blink"
    for i in range(0, 15):
        sevenSeg.output(i, 1)    
        time.sleep(0.1)
    time.sleep(0.5)
    for i in range(0, 15):
        sevenSeg.output(i, 0)
        time.sleep(0.1)
    time.sleep(0.5)
