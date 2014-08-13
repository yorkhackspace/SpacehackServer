

import smbus

bus = smbus.SMBus(1)

class ioexpander(object):
	def __init__ (self, address):
		self.bus = smbus.SMBus(1)
		self.address = address	
		self.IODirA = 0xff
		self.IODirB = 0xff
		self.GPIOA = 0x00
		self.GPIOB = 0x00

	def write_byte(self, reg, data):
		self.bus.write_byte_data(self.address,reg,data)


	def setPinDir(self, pin_id, dir):
		port = pin_id[0]
		pin = pin_id[1]	
		#TODO set the IODirA or B correctly



