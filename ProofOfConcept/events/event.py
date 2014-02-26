#!/usr/bin/python env

import Adafruit_BBIO.GPIO as GPIO
import Queue
import threading
from time import sleep
         
#GPIO.setup("P9_12", GPIO.IN)

#GPIO.wait_for_edge("P8_14", GPIO.RISING)

#GPIO.add_event_detect("P9_12", GPIO.FALLING)
#your amazing code here
#detect wherever:
#while True:
#    if GPIO.event_detected("P9_12"):
#        print "event detected!"

queue = Queue.Queue()


class IOEvents(threading.Thread):
	"""Do the events in a thread"""
	def __init__(self, pin, queue,):
		threading.Thread.__init__(self)
		self.pin = pin
		self.queue = queue
		print "Setting up pin: %s" % pin
                GPIO.setup(pin, GPIO.IN)
                GPIO.add_event_detect(pin, GPIO.FALLING)

	def run(self):
	    while True:
		    if GPIO.event_detected(self.pin):
			    # Might want to do something better here
			    level = GPIO.input(self.pin)
			    queue.put((self.pin, level))

class ProcessEvents(threading.Thread):
	"""Do something with the events"""
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
	
	def run(self):
		while True:
			pin, level = self.queue.get()
			print "Pin: %s, Level: %s" % (pin, level)



if __name__ == "__main__":
	pin11 = IOEvents("P9_11", queue)
	pin11.setDaemon(True)
	pin11.start()
	pin12 = IOEvents("P9_12", queue)
	pin12.setDaemon(True)
	pin12.start()
	pin13 = IOEvents("P9_13", queue)
	pin13.setDaemon(True)
	pin13.start()


	events = ProcessEvents(queue)
	events.setDaemon(True)
	events.start()

	#queue.join()
	while True:
		sleep(100)


