import sys
sys.path.append('./bigsevseg')
import Adafruit_MCP230xx as ExpIO
import time
print "imports done"
sevenSeg = ExpIO.Adafruit_MCP230XX(0x20, 16)
print "init done"

#    A
#    _
#F  |_| B
#E  |_| C
#
#    D
#
#Centre: G

seg = dict(A = 1, B = 2, C = 3, D = 4, E = 5, F = 6, G = 8)

for i in seg:
    print i
    sevenSeg.config(i, ExpIO.Adafruit_MCP230XX.OUTPUT)

print "All pins set to output"

while True:
    print "blink"
    for i in seg:
        sevenSeg.output(i, 1)    
        time.sleep(0.1)
    time.sleep(0.5)
    for i in seg:
        sevenSeg.output(i, 0)
        time.sleep(0.1)
    time.sleep(0.5)
