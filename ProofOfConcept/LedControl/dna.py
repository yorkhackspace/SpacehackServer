#Quick test of LedControl library
import LedControl

lc = LedControl.LedControl("P9_11", "P9_13", "P9_15", 1)
lc.shutdown(0, False)
lc.setIntensity(0, 15)
lc.clearDisplay(0)
lc.setLed(0, 2, 3, 1)
lc.setRow(0, 0, 127)
