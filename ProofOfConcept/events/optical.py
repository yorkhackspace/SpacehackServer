#!/usr/bin/env python

import Adafruit_BBIO.GPIO as GPIO
import Queue
import threading
from time import sleep

# This seems to work with the common pin on 
# the optical encoder at 3.3v and a 22k resistor
# on each switch pin to ground.

class OpticalEncoder(threading.Thread):
    """Given a queue on startup it spits out
    events to the queue with either "cw" or "ccw"
    """

    def __init__(self, queue, encoder_name, pins):
        """ Expects a queue to send events to
            and an array of the two input pins
        """
        threading.Thread.__init__(self)
        self.queue = queue
        self.pin_a = pins[0]
        self.pin_b = pins[1]
        self.encoder_name = encoder_name
        for pin in pins:
            print "Setting up pin: %s" % pin
            GPIO.setup(pin, GPIO.IN, GPIO.PUD_OFF)
            GPIO.add_event_detect(pin, GPIO.RISING)

    def run(self):
        while True:
            if GPIO.event_detected(self.pin_a):
                # Ignore false triggers
                if GPIO.input(self.pin_a) != 1:
                    continue
                level_b = 0
                # De-bounce
                for count in range(0,8):
                    level_b += GPIO.input(self.pin_b)
                    print(str(level_b))
                if level_b > 5:
                    dir = "cw"
                else:
                    dir = "ccw"
                self.queue.put((self.encoder_name, dir))

if __name__ == "__main__":
    q = Queue.Queue()
    enc = OpticalEncoder(q, "Flux Matrix", ["P8_22", "P8_24"])
    enc.setDaemon(True)
    enc.start()

    while True:
        state = q.get()
        print state

