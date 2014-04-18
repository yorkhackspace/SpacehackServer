import Adafruit_BBIO.ADC as ADC
import time

ADC.setup("P9_33")
while True:
  print ADC.read("P9_33")
  time.sleep (100)
