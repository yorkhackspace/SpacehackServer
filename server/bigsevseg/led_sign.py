from Adafruit_I2C import Adafruit_I2C
import time
Addr = 0x04

REG_Mode = ord('M')
REG_Code1 = ord('1')
REG_Code2 = ord('2')
REG_FlashFreq = ord('F')

CODE_Col_Green = ord('g')
CODE_Col_Red = ord('r')
CODE_Col_Red1 = ord('i')
CODE_Col_Red2 = ord('o')
CODE_Col_Red3 = ord('p')
CODE_Col_Yellow = ord('y')

MODE_Solid = ord('s')
MODE_Flash = ord('f')
MODE_Off = ord('o')

i2c = Adafruit_I2C(address=Addr)

#time.sleep(10)
##Set the mode register to flash
#i2c.write8(REG_Mode, MODE_Flash)
#time.sleep(0.1)
##set the first code to the colour Yellow
#i2c.write8(REG_Code1, CODE_Col_Yellow)
#time.sleep(0.1)
##set the second code to the colour Red
#i2c.write8(REG_Code2, CODE_Col_Red)
#time.sleep(0.1)
##flash frequency register set as delay in ms divided by four, minus 20. The number must be positive
##flash speed 0 is fastest 0*4+20 = period of 20ms = 50Hz
##flash speed 120 is medium 120*4+20 = period of 500ms = 2Hz
##flash speed 245 is slow 245*4+20 = period of 1000ms = 1Hz
#i2c.write8(REG_FlashFreq, 120)

##Sign is now 2Hz red and yellow flash

def LED_sign_solid(solid_code):
    #Set the mode register to solid
    i2c.write8(REG_Mode, MODE_Solid)
    time.sleep(0.1)
    #set the solid code
    i2c.write8(REG_Code1, solid_code)
    
def LED_sign_flash(code1, code2, period):
    #Set the mode register to flash
    i2c.write8(REG_Mode, MODE_Flash)
    time.sleep(0.1)
    #set the first code
    i2c.write8(REG_Code1, code1)
    time.sleep(0.1)
    #set the second code
    i2c.write8(REG_Code2, code2)
    time.sleep(0.1)
    #flash frequency register set as delay in ms divided by four, minus 20. The number must be positive
    #flash speed 0 is fastest 0*4+20 = period of 20ms = 50Hz
    #flash speed 120 is medium 120*4+20 = period of 500ms = 2Hz
    #flash speed 245 is slow 245*4+20 = period of 1000ms = 1Hz
    i2c.write8(REG_FlashFreq, period)
    
def LED_sign_off():
    #Set the mode register to off
    i2c.write8(REG_Mode, MODE_Off)

