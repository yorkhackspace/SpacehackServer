# Keypad_BBB - adapted from matrixKeypad_RPi_GPIO.py
# Adapted to BeagleBone Black and BBBIO from Raspberry Pi version
# February 2014 York Hackspace, originally for the SpaceHack project

# #####################################################
# Python Library for 3x4 matrix keypad using
# 7 of the avialable GPIO pins on the Raspberry Pi. 
# 
# This could easily be expanded to handle a 4x4 but I 
# don't have one for testing. The KEYPAD constant 
# would need to be updated. Also the setting/checking
# of the colVal part would need to be expanded to 
# handle the extra column.
# 
# Written by Chris Crumpacker
# May 2013
#
# main structure is adapted from Bandono's
# matrixQPI which is wiringPi based.
# https://github.com/bandono/matrixQPi?source=cc
# #####################################################
 
import Adafruit_BBIO.GPIO as GPIO

class keypad():
    # CONSTANTS   
    KEYPAD = [
        ["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"]
    ]
     
    def __init__(self, pin_R1, pin_R2, pin_R3, pin_R4, pin_C1, pin_C2, pin_C3, pin_C4):
        self.ROW = [pin_R1, pin_R2, pin_R3, pin_R4]
        self.COLUMN = [pin_C1, pin_C2, pin_C3, pin_C4]


    def getKey(self):
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.HIGH)
         
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, GPIO.PUD_DOWN)
         
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 1:
                rowVal = i
                 
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal < 0 or rowVal > 3:
            self.exit()
            return
         
        # Convert columns to input
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.IN, GPIO.PUD_DOWN)
         
        # Convert rows to output
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.OUT)
            GPIO.output(self.ROW[i], GPIO.LOW)
            
        # Switch the i-th row found from scan to output
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)
 
        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 3.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                 
        # if colVal is not 0 thru 3 then no button was pressed and we can exit
        if colVal < 0 or colVal > 3:
            self.exit()
            return
 
        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
         
    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, GPIO.PUD_DOWN) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, GPIO.PUD_DOWN)
         
if __name__ == '__main__':
    # Initialize the keypad class
    kp = keypad("P9_11","P9_12","P9_13","P9_14","P9_15","P9_16","P9_23","P9_24")
     
    # Loop while waiting for a keypress
    digit = None
    while digit == None:
        digit = kp.getKey()
     
    # Print the result
    print digit 
