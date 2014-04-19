import Adafruit_BBIO.GPIO as GPIO
q = Queue.Queue()
enc = OpticalEncoder(q, "Flux Matrix", ["P8_22", "P9_31"], GPIO)
enc.setDaemon(True)
enc.start()

while True:
    state = q.get()
    print state
