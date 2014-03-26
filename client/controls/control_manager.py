import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
import Keypad_BBB

controls = {}

class SHControl:
    """Spacehack control abstract type"""

    #constructor
    def __init__(self, controlconfig):
        self.pins=controlconfig['pins']
        self.hardwaretype = controlconfig['hardware']

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        print "Error: SHControl.poll() should never be called. Please override it."

    def processValueAssignment(self, value, ctrlid, override=False):
        print "Error: SHControl.processValueAssignment() should never be called. Please override it."

class SHControlPhoneStyleMenu(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(self.pins['BTN_1'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.pins['BTN_2'], GPIO.IN, GPIO.PUD_DOWN)
        PWM.start(self.pins['RGB_R'], 0.0)
        PWM.start(self.pins['RGB_G'], 0.0)
        PWM.start(self.pins['RGB_B'], 0.0)

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        btn1 = GPIO.input(self.pins['BTN_1'])
        btn2 = GPIO.input(self.pins['BTN_2'])
        state = [btn1, btn2]
        if ctrlstate != state:
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
        return state

        
class SHControlBargraphPot(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        bar = []
        for barnum in range(10):
            pin = self.pins['BAR_' + str(barnum+1)]
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
            bar.append(pin)
            ADC.setup(self.pins['POT'])

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        pot = ADC.read(pins['POT'])
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
            state = translateCalibratedValue(pot, controlsetup['calibration'][ctrltype])
            value = int(state)
        return state
        
class SHControlCombo7SegColourRotary(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        #segment defined at module scope
        GPIO.setup(self.pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
        PWM.start(self.pins['RGB_R'], 1.0) #common anode so 1.0 = off, 0.0 = on
        PWM.start(self.pins['RGB_G'], 1.0)
        PWM.start(self.pins['RGB_B'], 1.0)
        #What to do about rotary?

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        btn = GPIO.input(pins['BTN'])
        #rotary movement is handled separately not sampled
        if ctrlstate != state:
            if ctrltype == 'button':
                value = state
            elif ctrltype == 'toggle':
                if state:
                    value = int(not ctrlvalue)
        return state

class SHControlSwitchbank(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        for i in range(1,5):
            GPIO.setup(self.pins['SW_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)
            GPIO.setup(self.pins['LED_' + str(i)], GPIO.OUT)
            GPIO.output(self.pins['LED_' + str(i)], GPIO.LOW)

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        sw1 = GPIO.input(pins['SW_1'])
        sw2 = GPIO.input(pins['SW_2'])
        sw3 = GPIO.input(pins['SW_3'])
        sw4 = GPIO.input(pins['SW_4'])
        GPIO.output(pins['LED_1'], sw1)
        GPIO.output(pins['LED_2'], sw2)
        GPIO.output(pins['LED_3'], sw3)
        GPIO.output(pins['LED_4'], sw4)
        state = [sw1, sw2, sw3, sw4]
        if not ctrlstate == state:
            if ctrltype == 'toggle':
                if state == [1, 1, 1, 1]:
                    value = 1
                elif state == [0, 0, 0, 0]:
                    value = 0
                else:
                    value = ctrlvalue
        return state

class SHControlIlluminatedButton(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(self.pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(self.pins['LED'], GPIO.OUT)
        GPIO.output(self.pins['LED'], GPIO.LOW)

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        btn = GPIO.input(pins['BTN'])
        state = btn
        if ctrlstate != state:
            if ctrltype == 'button':
                value = state
            elif ctrltype == 'toggle':
                if state:
                    value = int(not ctrlvalue)
            GPIO.output(pins['LED'], value)
        return state

class SHControlPot(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        ADC.setup(self.pins['POT'])

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        pot = ADC.read(pins['POT'])
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
            state = translateCalibratedValue(pot, controlsetup['calibration'][ctrltype])
            value = int(state)
        elif ctrltype == 'colour':
            state = translateCalibratedValue(pot, controlsetup['calibration'][ctrltype])
            value = str(state)
        elif ctrltype == 'words':
            state = translateCalibratedValue(pot, controlsetup['calibration'][ctrltype])
            value = str(ctrldef['pool'][int(state)])
        elif ctrltype == 'verbs':
            state = translateCalibratedValue(pot, controlsetup['calibration']['words'])
            value = str(ctrldef['pool'][int(state)])
        return state

class SHControlIlluminatedToggle(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(self.pins['SW'], GPIO.IN, GPIO.PUD_DOWN)    
    def __init__(self, controlconfig):
        GPIO.setup(self.pins['LED'], GPIO.OUT)
        GPIO.output(self.pins['LED'], GPIO.HIGH) #common anode, so HIGH for off, LOW for on

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        sw = GPIO.input(pins['SW'])
        state = sw
        if ctrlstate != state:
            if ctrltype == 'toggle':
                if state:
                    int(value = not ctrlvalue)
        return state

class SHControlFourButtons(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        for i in range(1,5):
            GPIO.setup(self.pins['BTN_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
        btn1 = GPIO.input(pins['BTN1'])
        btn2 = GPIO.input(pins['BTN2'])
        btn3 = GPIO.input(pins['BTN3'])
        btn4 = GPIO.input(pins['BTN4'])
        state = [btn1, btn2, btn3, btn4]
        if not ctrlstate == state:
            for i in range(4):
                if state[i] - ctrlstate[i] == 1:
                    #button i has been newly pushed
                    if ctrltype == 'verbs':
                        value = str(ctrldef['list'][i])
                    elif ctrltype == 'colour':
                        value = str(ctrldef['values'][i])
        return state

class SHControlKeypad(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        keypad = Keypad_BBB.keypad(self.pins['ROW_1'], self.pins['ROW_2'], self.pins['ROW_3'], self.pins['ROW_4'], self.pins['COL_1'], self.pins['COL_2'], self.pins['COL_3'], self.pins['COL_4'])

    def poll(self, ctrldef, ctrltype, ctrlstate, ctrlvalue):
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
        return state

def initialiseControls(config, sortedlist):
    for ctrlid in sortedlist:
        hardwaretype = config['local']['controls'][ctrlid]['hardware'] 
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
                value = ctrlvalue
                state = controls[ctrlid].poll(ctrldef, ctrltype, ctrlstate, ctrlvalue)
                    
                if value != ctrlvalue:
                    controls[ctrlid].processValueAssignment(value, ctrlid)
                    print("Publishing control " + ctrlid + " which is " + hardwaretype + " / " + ctrltype)
                    print ("value = " + str(value))
                    mqttclient.publish("clients/" + ipaddress + "/" + ctrlid + "/value", value)
                    ctrldef['value'] = value
                ctrldef['state'] = state
