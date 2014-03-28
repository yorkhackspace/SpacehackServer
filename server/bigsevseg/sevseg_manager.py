sys.path.append('./bigsevseg')
import Adafruit_MCP230xx as ExpIO
import time

sevenSeg = ExpIO.Adafruit_MCP230XX(0x20, 16)
for i in range(0, 15):
    sevenSeg.config(i, ExpIO.Adafruit_MCP230XX.OUTPUT)

while true:
    for i in range(0, 15):
        sevenSeg.output(i, 1)    
    time.sleep(0.5)
    for i in range(0, 15):
        sevenSeg.output(i, 0)
    time.sleep(0.5)
