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

seg = dict(A = 7, B = 9, C = 10, D = 11, E = 12, F = 13, G = 14)

for i in seg:
    print seg[i]
    sevenSeg.config(seg[i], ExpIO.Adafruit_MCP230XX.OUTPUT)

print "All pins set to output"

while True:
    print "blink"
    for i in seg:
        sevenSeg.output(seg[i], 1)    
        time.sleep(0.1)
    time.sleep(0.5)
    for i in seg:
        sevenSeg.output(seg[i], 0)
        time.sleep(0.1)
    time.sleep(0.5)
