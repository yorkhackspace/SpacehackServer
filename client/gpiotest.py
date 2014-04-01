import Adafruit_BBIO.GPIO as GPIO

Run = True
while (Run):
	pin = raw_input("Enter pin name or 'q' to exit: ")
	InPin = True
	if pin == "q":
		Run = False
	else:
		while InPin:
			Command = raw_input("Select command; i-Input, o-Output, r-Read, 1-Set high, 0-Set low, b-Back: ")
			if Command == "i":
				GPIO.setup(pin, GPIO.IN, GPIO.PUD_DOWN)
			elif Command == "o":
				GPIO.setup(pin, GPIO.OUT)
			elif Command == "r":
				print GPIO.input(pin)
			elif Command == "1":
				GPIO.output(pin, GPIO.HIGH)
			elif Command == "0":
				GPIO.output(pin, GPIO.LOW)
			elif Command == "b":
				InPin = False
