import Adafruit_BBIO.ADC as ADC
import time
#37, 38, 39, 40
pin = "P9_39"
ADC.setup(pin)
while True:
  print ADC.read(pin)
  time.sleep (0.0100)
