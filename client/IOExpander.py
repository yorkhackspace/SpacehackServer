#process is -
#Write to 0B with bit 7 high (to set IOCON.BANK to 1)
#You are now in 8 bit mode!
#If you want 16 bit mode, write a 1 to 05
#Don't!

import smbus
import time

bus = smbus.SMBus(1)

class ioexpander(object):
	COM_IOCON_16 = 0x0b
	BIT_IOCON_BANK = 0b10000000
	COM_IODIRA = 0x00
	COM_IODIRB = 0x10
	COM_GPIOA = 0x09
	COM_GPIOB = 0x19
	def __init__ (self, address):
		self.bus = smbus.SMBus(1)
		self.address = address	
		self.IODirA = 0xff
		self.IODirB = 0xff
		self.GPIOA = 0x00
		self.GPIOB = 0x00
		self.write_byte(ioexpander.COM_IOCON_16, ioexpander.BIT_IOCON_BANK)

	def write_byte(self, reg, data):
		self.bus.write_byte_data(self.address,reg,data)


	def quicktest(self):
		self.write_byte(ioexpander.COM_IODIRA, 0x00)
		self.write_byte(ioexpander.COM_IODIRB, 0x00)
		for i in range(10):
			self.write_byte(ioexpander.COM_GPIOA, 0b10101010)
			self.write_byte(ioexpander.COM_GPIOB, 0b01010101)
			time.sleep(0.5)
			self.write_byte(ioexpander.COM_GPIOB, 0b10101010)
			self.write_byte(ioexpander.COM_GPIOA, 0b01010101)
			time.sleep(0.5)

	def setPinDir(self, pin_id, dir):
		port = pin_id[0]
		pin = pin_id[1]	
		#TODO set the IODirA or B correctly


io = ioexpander(0x20)
io.quicktest()
