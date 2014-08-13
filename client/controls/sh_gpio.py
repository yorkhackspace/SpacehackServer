import Adafruit_BBIO.GPIO as GPIO
import smbus
import IOExpander as IOX


IN = 0
OUT = 1
HIGH = 1
LOW = 0

RISING      = 1
FALLING     = 2
BOTH        = 3

PUD_OFF  = 0
PUD_DOWN = 1
PUD_UP   = 2

global bus
bus = None

global expanders
expanders = []

def init_smbus(bus_id):
	bus = smbus.SMBus(bus_id)


def attach_expander(expander_id):
	expanders.append(IOX.ioexpander(0x20 + int(expander_id)))	
	print "Attached expander at address " + str(0x20 + int(expander_id))

def expander_error(exp_id):
	raise Exception("No such expander attached: " + str(exp_id) +  ". call attach_expander(" + str(exp_id) + ") first.")

def get_exp(exp_id):
	for expander in expanders:
		if expander.get_address() == int(exp_id) + 0x20:
			return expander
	expander_error(exp_id)
	return None

def pin_id_error():
	raise Expection("Pin ID not recognised, expected [PE][0-9]_[AB(0-46)], eg P8_40 or E0_A7, A and B only for E pins")

def setup(pin_id, dir, pull=PUD_OFF):
	if pin_id[0] == 'P':
		GPIO.setup(pin_id, dir, pull)
	elif pin_id[0] == 'E':
		exp_id = pin_id[1]	
		get_exp(exp_id).setPinDir(pin_id[3:5], 1 if dir==IN else 0)
	else:
		pin_id_error()
	
def output(pin_id, data):
	if pin_id[0] == 'P':
		GPIO.output(pin_id, data == HIGH)
	elif pin_id[0] == 'E':
		exp_id = pin_id[1]	
		get_exp(exp_id).setPinData(pin_id[3:5], data)
	else:
		pin_id_error()


def input(pin_id):
	if pin_id[0] == 'P':
		return GPIO.input(pin_id)
	elif pin_id[0] == 'E':
		exp_id = pin_id[1]	
		return get_exp(exp_id).getPinData(pin_id[3:5])==HIGH
	else:
		pin_id_error()
	return 0


def add_event_detect(pin_id, edge):
	if pin_id[0] == 'P':
		return GPIO.add_event_detect(pin_id,edge)
	elif pin_id[0] == 'E':
		raise Exception("Interupt feature is not yet implemented on this pin (" + pin + ")")
	else:
		pin_id_error()
	return 0
