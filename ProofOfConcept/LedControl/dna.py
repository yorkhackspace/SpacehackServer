import LedControl

lc = LedControl.LedControl("P9_11", "P9_13", "P9_15", 1)
lc.setIntensity(0, 15)
lc.setLed(0, 2, 3, 1)
lc.setRow(0, 0, 127)
while True:
    #do nothing
    x = 1
