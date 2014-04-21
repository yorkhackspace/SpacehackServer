from Adafruit_I2C import Adafruit_I2C
import time
Addr = 0x04
i2c = Adafruit_I2C(address=Addr)
i2c.write8(ord('M'), ord('s'))
time.sleep(1)
i2c.write8(ord('1'), ord('g'))
