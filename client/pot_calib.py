import Adafruit_BBIO.ADC as ADC

ADC.setup("P9_33")
while True:
  print ADC.read("P9_33")
  sleep (100)
