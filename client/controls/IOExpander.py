#process is -
#Write to 0B with bit 7 high (to set IOCON.BANK to 1)
#You are now in 8 bit mode!
#If you want 16 bit mode, write a 1 to 05
#Don't!

import smbus
import time

bus = smbus.SMBus(1)


def setBit(i, bit, data):
	if data == 0:
		return (i & (~(1<<bit)))
	return (i | (1<<bit))

class ioexpander(object):
	COM_IOCON_16 = 0x0b
	BIT_IOCON_BANK = 0b10000000
	COM_IODIRA = 0x00
	COM_IODIRB = 0x10
	COM_GPIOA = 0x09
	COM_GPIOB = 0x19
	DIR_OUTPUT = 0
	DIR_INPUT = 1
	def __init__ (self, address):
		self.bus = smbus.SMBus(1)
		self.address = address	
		self.IODirA = 0xff
		self.IODirB = 0xff
		self.GPIOA = 0x00
		self.GPIOB = 0x00
		self.write_byte(ioexpander.COM_IOCON_16, ioexpander.BIT_IOCON_BANK)

	def get_address(self):
		return self.address

	def write_byte(self, reg, data):
		self.bus.write_byte_data(self.address, reg, data)

	def read_byte(self, reg):
		return self.bus.read_byte_data(self.address, reg)

	def setPinDir(self, pin_id, dir):
		port = pin_id[0]
		pin = pin_id[1]

		if (port == 'A'):
			self.IODirA = setBit(self.IODirA, int(pin), dir)
		elif (port == 'B'):
			self.IODirB = setBit(self.IODirB, int(pin), dir)
		else:
			print("Error, unknown port: " + port + ".")
		self.write_byte(ioexpander.COM_IODIRA, self.IODirA)
		self.write_byte(ioexpander.COM_IODIRB, self.IODirB)


	def setPinData(self, pin_id, data):
		port = pin_id[0]
		pin = pin_id[1]

		if (port == 'A'):
			self.GPIOA = setBit(self.GPIOA, int(pin), data)
		elif (port == 'B'):
			self.GPIOB = setBit(self.GPIOB, int(pin), data)
		else:
			print("Error, unknown port: " + port + ".")
		self.write_byte(ioexpander.COM_GPIOA, self.GPIOA)
		self.write_byte(ioexpander.COM_GPIOB, self.GPIOB)

	def getPinData(self, pin_id):
		port = pin_id[0]
		pin = pin_id[1]
		readData = 0
		if (port == 'A'):
			readData = self.read_byte(self.COM_GPIOA)
		elif (port == 'B'):
			readData = self.read_byte(self.COM_GPIOB)
		else:
			print("Error, unknown port: " + port + ".")

		if ((readData & (1<<int(pin))) > 0):
			return 1
		return 0

#io = ioexpander(0x20)
#
#outputs = ["B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "A7", "A6", "A5"]
#inputs = ["A4", "A3", "A2", "A1", "A0"]
##
#for out_pin in outputs:
#	io.setPinDir(out_pin, ioexpander.DIR_OUTPUT)
#while(1):
#	for out_pin in outputs:
#		io.setPinData(out_pin, 1)
#	time.sleep(0.5)
#
#	for out_pin in outputs:
#		io.setPinData(out_pin, 0)
#	time.sleep(0.5)
#
#	for in_pin in inputs:
#		print in_pin + " = " + str(io.getPinData(in_pin))
