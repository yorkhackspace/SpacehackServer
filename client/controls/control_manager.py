import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
from Adafruit_7Segment import SevenSegment
from collections import OrderedDict
import Keypad_BBB

controls = {}
allcontrolsconfig = {}
myLcdManager = {}

class SHControl(object):
    """Spacehack control abstract type"""

    #constructor
    def __init__(self, controlconfig):
        self.controlsetup = controlconfig
        self.pins=controlconfig['pins']
        self.hardwaretype = controlconfig['hardware']

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        print "Error: SHControl.poll() should never be called. Please override it."

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        self.roundsetup = roundconfig['controls'][ctrlid]
        self.ctrltype = self.roundsetup['type']
        self.ctrldef = self.roundsetup['definition']
        return 'value' not in self.ctrldef or self.ctrldef['value'] != value or override

    def processRoundConfig(self):
        print "Error: SHControl.processRoundConfig() should never be called"

class SHControlPhoneStyleMenu(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(self.pins['BTN_1'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.pins['BTN_2'], GPIO.IN, GPIO.PUD_DOWN)
        
        GPIO.setup(self.pins['RGB_R'], GPIO.OUT)
        GPIO.setup(self.pins['RGB_G'], GPIO.OUT)
        GPIO.setup(self.pins['RGB_B'], GPIO.OUT)

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        
        btn1 = GPIO.input(self.pins['BTN_1'])
        btn2 = GPIO.input(self.pins['BTN_2'])
        state = [btn1, btn2]
        if ctrlstate != state:
            print "phone button pressed"
            if ctrlstate == None:
                leftchanged = True
                rightchanged = True
            else:
                leftchanged = ctrlstate[0] != state[0]
                rightchanged = ctrlstate[1] != state[1]
            leftpressed = state[0]
            rightpressed = state[1]
            if ctrltype == 'toggle':
                if rightchanged and rightpressed: #On
                    value = 1
                elif leftchanged and leftpressed: #Off
                    value = 0
            elif ctrltype == 'selector':
                if rightchanged and rightpressed:
                    if ctrlvalue < ctrldef['max']:
                        value = ctrlvalue + 1
                elif leftchanged and leftpressed:
                    if ctrlvalue > ctrldef['min']:
                        value = ctrlvalue - 1
            elif ctrltype == 'colours':
                #get current index from pool of values
                idx = ctrldef['values'].index(ctrlvalue)
                if rightchanged and rightpressed:
                    if idx < len(ctrldef['values']) - 1:
                        idx += 1
                    else:
                        idx = 0
                elif leftchanged and leftpressed:
                    if idx > 0:
                        idx -= 1
                    else:
                        idx = len(ctrldef['values']) - 1
                value = str(ctrldef['values'][idx])
            elif ctrltype == 'words':
                #get current index from pool of values
                idx = ctrldef['pool'].index(ctrlvalue)
                if rightchanged and rightpressed:
                    if idx < len(ctrldef['pool']) - 1:
                        idx += 1
                    else:
                        idx = 0
                elif leftchanged and leftpressed:
                    if idx > 0:
                        idx -= 1
                    else:
                        idx = len(ctrldef['pool']) - 1
                value = str(ctrldef['pool'][idx])
            elif ctrltype == 'verbs':
                if rightchanged and rightpressed:
                    value = str(ctrldef['pool'][1])
                elif leftchanged and leftpressed:
                    value = str(ctrldef['pool'][0])
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            RGB = [0, 0, 0]
            if self.ctrltype == 'toggle':
       	        if self.controlsetup['display']['height'] > 3:
                    if value:
                        myLcdManager.displayValueLine("On", ctrlid)
                        RGB = [1, 0, 0]
                    else:
                        myLcdManager.displayValueLine("Off", ctrlid)
            elif self.ctrltype == 'selector':
                if self.controlsetup['display']['height'] > 3:
                    myLcdManager.displayValueLine(str(value), ctrlid)
            elif self.ctrltype == 'colour':
                if self.controlsetup['display']['height'] > 3:
                    myLcdManager.displayValueLine(str(value), ctrlid)
                #Light the LED the right colours
                RGB = controlsetup['colours'][str(value)]
            elif self.ctrltype == 'words':
                if self.controlsetup['display']['height'] > 3:
                    myLcdManager.displayValueLine(value, ctrlid)
            GPIO.output(self.pins['RGB_R'], RGB[0])
            GPIO.output(self.pins['RGB_G'], RGB[1])
            GPIO.output(self.pins['RGB_B'], RGB[2])

class SHControlPot(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        ADC.setup(self.pins['POT'])

    def __translateCalibratedValue(self, rawvalue, calibrationdict):
        """Calculate a calibrated value from a raw value and translation dictionary"""
        sortedlist = OrderedDict(sorted(calibrationdict.items(), key=lambda t: t[1]))
        for value in sortedlist:
            if rawvalue < calibrationdict[value]:
                return value

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        pot = ADC.read(self.pins['POT'])
        if ctrltype == 'toggle':
            if ctrlvalue == None: #We'll take the mid line to decide
                if pot < 0.5:
                    state = 0
                else:
                    state = 1
            elif pot < 0.4: #Dead zone in the middle
                state = 0
            elif pot > 0.6:
                state = 1
            else:
                state = ctrlstate #if not decisively left or right, stay the same
            if state != ctrlstate:
                value = state
        elif ctrltype == 'selector':
            state = SHControlPot.__translateCalibratedValue(self, pot, controlsetup['calibration'][ctrltype])
            value = int(state)
        elif ctrltype == 'colour':
            state = SHControlPot.__translateCalibratedValue(self, pot, controlsetup['calibration'][ctrltype])
            value = str(state)
        elif ctrltype == 'words':
            state = SHControlPot.__translateCalibratedValue(self, pot, controlsetup['calibration'][ctrltype])
            value = str(ctrldef['pool'][int(state)])
        elif ctrltype == 'verbs':
            state = SHControlPot.__translateCalibratedValue(self, pot, controlsetup['calibration']['words'])
            value = str(ctrldef['pool'][int(state)])
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            if self.ctrltype == 'toggle':
                if self.controlsetup['display']['height']>3:
                    if value:
                        myLcdManager.displayValueLine("On", ctrlid)
                        #Light the LED red
                    else:
                        myLcdManager.displayValueLine("Off", ctrlid)
                        #Switch off LED
            elif self.ctrltype == 'selector':
                if self.controlsetup['display']['height']>3:
                    myLcdManager.displayValueLine(str(value), ctrlid)
            elif self.ctrltype == 'colour':
                if self.controlsetup['display']['height']>3:
                    myLcdManager.displayValueLine(str(value), ctrlid)
                #Light the LED the right colours
            elif self.ctrltype == 'words':
                if self.controlsetup['display']['height']>3:
                    myLcdManager.displayValueLine(value, ctrlid)
            elif self.ctrltype == 'verbs':
                if self.controlsetup['display']['height']>3:
                    myLcdManager.displayValueLine(value, ctrlid)      

class SHControlBargraphPot(SHControlPot):   

    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        SHControlPot.__init__(self, controlconfig)
        self.bar = []
        for barnum in range(10):
            pin = self.pins['BAR_' + str(barnum+1)]
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
            self.bar.append(pin)

    def __translateCalibratedValue(self, rawvalue, calibrationdict):
        """Calculate a calibrated value from a raw value and translation dictionary"""
        sortedlist = OrderedDict(sorted(calibrationdict.items(), key=lambda t: t[1]))
        for value in sortedlist:
            if rawvalue < calibrationdict[value]:
                return value

    def __updateDisplay(self, digit):
        """Display Bar graph"""
        for i in range(10):
            if digit > i:
                GPIO.output(self.bar[i], GPIO.HIGH)
            else:
                GPIO.output(self.bar[i], GPIO.LOW) 

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        pot = ADC.read(self.pins['POT'])
        #Interpretation varies by control type
        if ctrltype == 'toggle':
            if ctrlvalue == None: #We'll take the mid line to decide
                if pot < 0.5:
                    state = 0
                else:
                    state = 1
            elif pot < 0.4: #Dead zone in the middle
                state = 0
            elif pot > 0.6:
                state = 1
            else:
                state = ctrlstate #if not decisively left or right, stay the same
            if state != ctrlstate:
                value = state
        elif ctrltype == 'selector':
            state = SHControlBargraphPot.__translateCalibratedValue(self, pot, controlsetup['calibration'][ctrltype])
            value = int(state)
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            if self.roundsetup['enabled']:
                if self.ctrltype == 'toggle':
                    if value:
                        SHControlBargraphPot.__updateDisplay(self, 10)
                    else:
                        SHControlBargraphPot.__updateDisplay(self, 0)
                elif self.ctrltype == 'selector':
                    SHControlBargraphPot.__updateDisplay(self, value)
            else:
                SHControlBargraphPot.__updateDisplay(self, 0)
        
class SHControlCombo7SegColourRotary(SHControl):
    
    #Adafruit I2C 7-segment
    segment = SevenSegment(address=0x70)
    lookup7segchar = {'0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66, '5': 0x6D,
                  '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F, ' ': 0x00, '_': 0x08,
                  'a': 0x5F, 'A': 0x77, 'b': 0x7C, 'B': 0x7C, 'c': 0x58, 'C': 0x39,
                  'd': 0x5E, 'D': 0x5E, 'e': 0x7B, 'E': 0x79, 'f': 0x71, 'F': 0x71,
                  'g': 0x6F, 'G': 0x3D, 'h': 0x74, 'H': 0x76, 'i': 0x04, 'I': 0x06,
                  'j': 0x1E, 'J': 0x1E, 'k': 0x08, 'K': 0x08, 'l': 0x06, 'L': 0x38,
                  'm': 0x08, 'M': 0x08, 'n': 0x54, 'N': 0x37, 'o': 0x5C, 'O': 0x3F,
                  'p': 0x73, 'P': 0x73, 'q': 0x67, 'Q': 0x67, 'r': 0x50, 'R': 0x31,
                  's': 0x6D, 'S': 0x6D, 't': 0x78, 'T': 0x78, 'u': 0x1C, 'U': 0x3E,
                  'v': 0x08, 'V': 0x07, 'w': 0x08, 'W': 0x08, 'x': 0x08, 'X': 0x08,
                  'y': 0x6E, 'Y': 0x6E, 'z': 0x5B, 'Z': 0x5B, '-': 0x40
                  }

    #Print to the 7-seg
    def __displayDigits(self, digits):
        """Print to the 7-seg"""
        disp = -len(digits) % 4 * ' ' + digits
        for i in range(4):
            digit=disp[i]
            if i < 2:
                idx = i
            else:
                idx = i+1
            self.segment.writeDigitRaw(idx,self.lookup7segchar[digit])

    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        #segment defined at module scope
        GPIO.setup(self.pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.pins['RGB_R'], GPIO.OUT)
        GPIO.setup(self.pins['RGB_G'], GPIO.OUT)
        GPIO.setup(self.pins['RGB_B'], GPIO.OUT)
        GPIO.output(self.pins['RGB_R'], GPIO.HIGH)
        GPIO.output(self.pins['RGB_G'], GPIO.HIGH)
        GPIO.output(self.pins['RGB_B'], GPIO.HIGH)
        SHControlCombo7SegColourRotary.__displayDigits(self, "    ")
        #What to do about rotary?

    

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        btn = GPIO.input(self.pins['BTN'])
        state = btn
        #rotary movement is handled separately not sampled
        if ctrlstate != state:
            if ctrltype == 'button':
                value = state
            elif ctrltype == 'toggle':
                if state:
                    value = int(not ctrlvalue)
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            RGB = [0, 0, 0]
            if self.roundsetup['enabled']:
                if self.ctrltype in ['toggle', button]:
                    if value:
                        SHControlCombo7SegColourRotary.__displayDigits(self, 'On')
                        RGB = [1, 0, 0]
                    else:
                        SHControlCombo7SegColourRotary.__displayDigits(self, 'Off')
                        #Switch off LED
                elif self.ctrltype == 'selector':
                    SHControlCombo7SegColourRotary.__displayDigits(self, str(value))
                    #Switch off LED
                elif self.ctrltype == 'colour':
                    #Light LED appropriate colour
                    if value == 'red':
                        SHControlCombo7SegColourRotary.__displayDigits(self, "RED")
                    elif value == 'green':
                        SHControlCombo7SegColourRotary.__displayDigits(self, "GREN")
                    elif value == 'blue':
                        SHControlCombo7SegColourRotary.__displayDigits(self, "BLUE")
                    elif value == 'yellow':
                        SHControlCombo7SegColourRotary.__displayDigits(self, "YELO")
                    elif value == 'cyan':
                        SHControlCombo7SegColourRotary.__displayDigits(self, "CYAN")
                    RGB = controlsetup['colours'][str(value)]
                elif self.ctrltype == 'words':
                    #Switch off LED
                    SHControlCombo7SegColourRotary.__displayDigits(self, value.upper())
            else:
                SHControlCombo7SegColourRotary.__displayDigits(self, "    ")
            
            GPIO.output(self.pins['RGB_R'], 1 - RGB[0])
            GPIO.output(self.pins['RGB_G'], 1 - RGB[1])
            GPIO.output(self.pins['RGB_B'], 1 - RGB[2])

class SHControlSwitchbank(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        for i in range(1,5):
            GPIO.setup(self.pins['SW_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)
            GPIO.setup(self.pins['LED_' + str(i)], GPIO.OUT)
            GPIO.output(self.pins['LED_' + str(i)], GPIO.LOW)

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        sw1 = GPIO.input(self.pins['SW_1'])
        sw2 = GPIO.input(self.pins['SW_2'])
        sw3 = GPIO.input(self.pins['SW_3'])
        sw4 = GPIO.input(self.pins['SW_4'])
        GPIO.output(self.pins['LED_1'], sw1)
        GPIO.output(self.pins['LED_2'], sw2)
        GPIO.output(self.pins['LED_3'], sw3)
        GPIO.output(self.pins['LED_4'], sw4)
        state = [sw1, sw2, sw3, sw4]
        if not ctrlstate == state:
            if ctrltype == 'toggle':
                if state == [1, 1, 1, 1]:
                    value = 1
                elif state == [0, 0, 0, 0]:
                    value = 0
                else:
                    value = ctrlvalue
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            #TODO
            print "todo\n"

class SHControlIlluminatedButton(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(self.pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.pins['LED'], GPIO.OUT)
        GPIO.output(self.pins['LED'], GPIO.LOW)

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        btn = GPIO.input(self.pins['BTN'])
        state = btn
        if ctrlstate != state:
            if ctrltype == 'button':
                value = state
                GPIO.output(self.pins['LED'], value)
            elif ctrltype == 'toggle':
                if state:
                    value = int(not ctrlvalue)
                    GPIO.output(self.pins['LED'], value)
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            if self.ctrltype == 'toggle':
                if value:
                    GPIO.output(self.pins['LED'], GPIO.HIGH)
                else:
                    GPIO.output(self.pins['LED'], GPIO.LOW)

class SHControlIlluminatedToggle(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(self.pins['SW'], GPIO.IN, GPIO.PUD_DOWN)    
        GPIO.setup(self.pins['LED'], GPIO.OUT)
        GPIO.output(self.pins['LED'], GPIO.HIGH) #common anode, so HIGH for off, LOW for on

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        sw = GPIO.input(self.pins['SW'])
        state = sw
        if ctrlstate != state:
            if ctrltype == 'toggle':
                if state:
                    int(value = not ctrlvalue)
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            if self.ctrltype == 'toggle':
                if controlsetup['display']['height']>3:
                    if value:
    	                displayValueLine("On", ctrlid)
                        GPIO.output(self.pins['LED'], GPIO.LOW)
                    else:
                        displayValueLine("Off", ctrlid)
                        GPIO.output(self.pins['LED'], GPIO.HIGH)

class SHControlFourButtons(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        for i in range(1,5):
            GPIO.setup(self.pins['BTN_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        btn1 = GPIO.input(self.pins['BTN1'])
        btn2 = GPIO.input(self.pins['BTN2'])
        btn3 = GPIO.input(self.pins['BTN3'])
        btn4 = GPIO.input(self.pins['BTN4'])
        state = [btn1, btn2, btn3, btn4]
        if not ctrlstate == state:
            for i in range(4):
                if state[i] - ctrlstate[i] == 1:
                    #button i has been newly pushed
                    if ctrltype == 'verbs':
                        value = str(ctrldef['list'][i])
                    elif ctrltype == 'colour':
                        value = str(ctrldef['values'][i])
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            #TODO
            print "todo\n"

class SHControlKeypad(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        keypad = Keypad_BBB.keypad(self.pins['ROW_1'], self.pins['ROW_2'], self.pins['ROW_3'], self.pins['ROW_4'], self.pins['COL_1'], self.pins['COL_2'], self.pins['COL_3'], self.pins['COL_4'])

    def poll(self, controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        value = ctrlvalue
        state = keypad.getKey()
        if (ctrlstate != state) and (state != None):
            if not 'buffer' in ctrldef:
                ctrldef['buffer'] = ""
            if ctrltype == 'pin':
                if state in "0123456789":
                    ctrldef['buffer'] += state
                    if len(ctrldef['buffer']) == 4:
                        value = ctrldef['buffer']
                        ctrldef['buffer'] = ''
            elif ctrltype == 'selector':
                if state in "0123456789":
                    value = state
            elif ctrltype == 'words':
                if state in "ABCD":
                    ctrldef['buffer'] += state
                elif state == '0':
                    ctrldef['buffer'] += 'O'
                elif state == '1':
                    ctrldef['buffer'] += 'I'
                elif state == '2':
                    ctrldef['buffer'] += 'Z'
                elif state == '3':
                    ctrldef['buffer'] += 'E'
                elif state == '5':
                    ctrldef['buffer'] += 'S'
                elif state == '#':
                    value = ctrldef['buffer']
                    ctrldef['buffer'] = ''
        return value, state

    def processValueAssignment(self, roundconfig, value, ctrlid, override=False):
        if SHControl.processValueAssignment(self, roundconfig, value, ctrlid, override = False):
            displayValueLine(value)

def initialiseControls(config, sortedlist, lcdManager):

    global allcontrolsconfig, myLcdManager
    myLcdManager = lcdManager
    allcontrolsconfig = config['local']['controls']
    for ctrlid in sortedlist:
        hardwaretype = allcontrolsconfig[ctrlid]['hardware'] 
        if hardwaretype != 'instructions':
            controlconfig = config['local']['controls'][ctrlid]
            if hardwaretype == 'phonestylemenu': # 2 buttons, RGB LED
                controls[ctrlid] = (SHControlPhoneStyleMenu(controlconfig))                
            elif hardwaretype == 'bargraphpotentiometer': #10k pot, 10 LEDs
                controls[ctrlid] =(SHControlBargraphPot(controlconfig))
            elif hardwaretype == 'combo7SegColourRotary': #I2C 7Seg, button, rotary, RGB
                controls[ctrlid] =(SHControlCombo7SegColourRotary(controlconfig))                
            elif hardwaretype == 'switchbank': #Four switches, four LEDs
                controls[ctrlid] =(SHControlSwitchbank(controlconfig))                
            elif hardwaretype == 'illuminatedbutton': #one button, one LED
                controls[ctrlid] =(SHControlIlluminatedButton(controlconfig))                
            elif hardwaretype == 'potentiometer': #slide or rotary 10k pot
                controls[ctrlid] =(SHControlPot(controlconfig))                
            elif hardwaretype == 'illuminatedtoggle': #one switch, one LED            
                controls[ctrlid] =(SHControlIlluminatedToggle(controlconfig))                
            elif hardwaretype == 'fourbuttons': #four buttons
                controls[ctrlid] =(SHControlFourButtons(controlconfig))                
            elif hardwaretype == 'keypad': #four rows, four cols
                controls[ctrlid] =(SHControlKeypad(controlconfig))                
            else:
                print "Unknown control type in config file"
                controls.append(SHControl(controlconfig))


#Poll controls, interpret into values, recognise changes, inform server
def pollControls(config, roundconfig, controlids, mqttclient, ipaddress):
    """Poll controls, interpret into values, recognise changes, inform server"""
    if len(roundconfig) > 0:
        for ctrlid in controlids:
            roundsetup = roundconfig['controls'][ctrlid]
            controlsetup = config['local']['controls'][ctrlid]
            if 'definition' in roundsetup and roundsetup['enabled']:
                ctrltype = roundsetup['type'] #Which supported type are we this time
                ctrldef = roundsetup['definition']
                pins = controlsetup['pins']
                #State is physical state of buttons etc
                if 'state' in ctrldef:
                    ctrlstate = ctrldef['state']
                else:
                    ctrlstate = None
                #Value is as interpreted by the abstracted control type
                if 'value' in ctrldef:
                    ctrlvalue = ctrldef['value']
                else:
                    ctrlvalue = None
                hardwaretype = config['local']['controls'][ctrlid]['hardware'] #Which hardware implementation
                #For the particular hardware, poll the controls and decide what it means
                value, state = controls[ctrlid].poll(controlsetup, ctrldef, ctrltype, ctrlstate, ctrlvalue)
                    
                if value != ctrlvalue:
                    controls[ctrlid].processValueAssignment(roundconfig, value, ctrlid)
                    print("Publishing control " + ctrlid + " which is " + hardwaretype + " / " + ctrltype)
                    print ("value = " + str(value))
                    mqttclient.publish("clients/" + ipaddress + "/" + ctrlid + "/value", value)
                    ctrldef['value'] = value
                ctrldef['state'] = state


#Process control value assignment
def processControlValueAssignment(roundconfig, value, ctrlid, override=False):
    """Process control value assignment"""
    controls[ctrlid].processValueAssignment(roundconfig, value, ctrlid, override)

def processRoundConfig(config, roundconfig, controlids):
    for ctrlid in controlids:
        roundsetup = roundconfig['controls'][ctrlid]
        controlsetup = config['local']['controls'][ctrlid]
        myLcdManager.display(roundsetup['name'], controlsetup['display']['width'], ctrlid)
        if 'definition' in roundsetup and roundsetup['enabled']:
            ctrltype = roundsetup['type']
            ctrldef = roundsetup['definition']
            hardwaretype = config['local']['controls'][ctrlid]['hardware']
            if hardwaretype == 'phonestylemenu':
                if ctrltype == 'toggle':
                    displayButtonsLine("Off", "On", ctrlid)
                elif ctrltype == 'verbs':
                    displayButtonsLine(ctrldef['pool'][0], ctrldef['pool'][1], ctrlid)
                else:
                    displayButtonsLine("<<<<", ">>>>", ctrlid)
            elif hardwaretype == 'combo7SegColourRotary':
                if ctrltype == 'button':
                    displayDigits("PUSH")
            if 'value' in ctrldef:
                processControlValueAssignment(roundconfig, ctrldef['value'], ctrlid, True)

