#process is -
#Write to 0B with bit 7 high (to set IOCON.BANK to 1)
#You are now in 8 bit mode!
#If you want 16 bit mode, write a 1 to 05
#Don't!

import smbus

bus = smbus.SMBus(1)

class ioexpander(object):
	IOCON_16 = 0x0b
	IOCON_BANK = 0b1000000
	def __init__ (self, address):
		self.bus = smbus.SMBus(1)
		self.address = address	
		self.IODirA = 0xff
		self.IODirB = 0xff
		self.GPIOA = 0x00
		self.GPIOB = 0x00
		self.write_byte(ioexpander.IOCON_16, ioexpander.IOCON_BANK)

	def write_byte(self, reg, data):
		self.bus.write_byte_data(self.address,reg,data)


	def setPinDir(self, pin_id, dir):
		port = pin_id[0]
		pin = pin_id[1]	
		#TODO set the IODirA or B correctly


io = ioexpander(0x71)
