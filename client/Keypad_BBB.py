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
 
class keypad():
    # CONSTANTS   
    KEYPAD = [
        ["1", "2", "3", "A"],
        ["4", "5", "6", "B"],
        ["7", "8", "9", "C"],
        ["*", "0", "#", "D"]
    ]
     
    def __init__(self, mode, GPIO, pin_R1, pin_R2, pin_R3, pin_R4, pin_C1, pin_C2, pin_C3, pin_C4):
        self.ROW = [pin_R1, pin_R2, pin_R3, pin_R4]
        self.COLUMN = [pin_C1, pin_C2, pin_C3, pin_C4]
        self.mode = mode
        self.GPIO = GPIO
	if self.mode == "auto":
		#init pins now
		for pin in self.ROW:
			self.GPIO.setup(pin, self.GPIO.IN)
		for pin in self.COLUMN:
			self.GPIO.setup(pin, self.GPIO.IN)

    def getKeyAuto(self):
        rowin = -1
        colin = -1
        #print "raw in " + bin(self.GPIO.get_exp(1).read_byte(0x09))
        for r in range(0,4):
            if self.GPIO.input(self.ROW[r]) == self.GPIO.HIGH:
                #print "high row - " + str(r)
                rowin = r
            if self.GPIO.input(self.COLUMN[r]) == self.GPIO.HIGH:
                #print "high col - " + str(r)
                colin = r
        if rowin>=0 and colin>=0:
            return self.KEYPAD[rowin][colin]
        return

    def getKeyScan(self):
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            self.GPIO.setup(self.COLUMN[j], self.GPIO.OUT)
            self.GPIO.output(self.COLUMN[j], self.GPIO.HIGH)
         
        # Set all rows as input
        for i in range(len(self.ROW)):
            self.GPIO.setup(self.ROW[i], self.GPIO.IN, self.GPIO.PUD_DOWN)
         
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = self.GPIO.input(self.ROW[i])
            if tmpRead == 1:
                rowVal = i
                 
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal < 0 or rowVal > 3:
            self.exit()
            return
         
        # Convert columns to input
        for j in range(len(self.COLUMN)):
            self.GPIO.setup(self.COLUMN[j], self.GPIO.IN, self.GPIO.PUD_DOWN)
         
        # Convert rows to output
        for i in range(len(self.ROW)):
            self.GPIO.setup(self.ROW[i], self.GPIO.OUT)
            self.GPIO.output(self.ROW[i], self.GPIO.LOW)
            
        # Switch the i-th row found from scan to output
        self.GPIO.output(self.ROW[rowVal], self.GPIO.HIGH)
 
        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 3.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = self.GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                 
        # if colVal is not 0 thru 3 then no button was pressed and we can exit
        if colVal < 0 or colVal > 3:
            self.exit()
            return
 
        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
         
    def getKey(self):
        if self.mode == "scan":
            return self.getKeyScan()
        elif self.mode == "auto":
            return self.getKeyAuto()

    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                self.GPIO.setup(self.ROW[i], self.GPIO.IN, self.GPIO.PUD_DOWN) 
        for j in range(len(self.COLUMN)):
                self.GPIO.setup(self.COLUMN[j], self.GPIO.IN, self.GPIO.PUD_DOWN)
         
if __name__ == '__main__':
    # Initialize the keypad class
    kp = keypad("P9_11","P9_12","P9_13","P9_14","P9_15","P9_16","P9_23","P9_24")
     
    # Loop while waiting for a keypress
    digit = None
    while digit == None:
        digit = kp.getKey()
     
    # Print the result
    print digit 
