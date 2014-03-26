import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.PWM as PWM
import Adafruit_BBIO.ADC as ADC
import Keypad_BBB

controls = []

class SHControl:
    """Spacehack control abstract type"""

    #constructor
    def __init__(self, controlconfig):
        self.pins=controlconfig['pins']
        self.hardwaretype = controlconfig['hardware']

    def poll():
        print "SHControl.poll() should never be called"

class SHControlPhoneStyleMenu(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(pins['BTN_1'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(pins['BTN_2'], GPIO.IN, GPIO.PUD_DOWN)
        PWM.start(pins['RGB_R'], 0.0)
        PWM.start(pins['RGB_G'], 0.0)
        PWM.start(pins['RGB_B'], 0.0)
        
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
        
class SHControlCombo7SegColourRotary(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        #segment defined at module scope
        GPIO.setup(pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
        PWM.start(pins['RGB_R'], 1.0) #common anode so 1.0 = off, 0.0 = on
        PWM.start(pins['RGB_G'], 1.0)
        PWM.start(pins['RGB_B'], 1.0)
        #What to do about rotary?

class SHControlSwitchbank(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        for i in range(1,5):
            GPIO.setup(pins['SW_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)
            GPIO.setup(pins['LED_' + str(i)], GPIO.OUT)
            GPIO.output(pins['LED_' + str(i)], GPIO.LOW)

class SHControlIlluminatedButton(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(pins['LED'], GPIO.OUT)
        GPIO.output(pins['LED'], GPIO.LOW)

class SHControlPot(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        ADC.setup(pins['POT'])

class SHControlIlluminatedToggle(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        GPIO.setup(pins['SW'], GPIO.IN, GPIO.PUD_DOWN)
        GPIO.setup(pins['LED'], GPIO.OUT)
        GPIO.output(pins['LED'], GPIO.HIGH) #common anode, so HIGH for off, LOW for on

class SHControlFourButtons(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        for i in range(1,5):
            GPIO.setup(pins['BTN_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)

class SHControlKeypad(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        keypad = Keypad_BBB.keypad(pins['ROW_1'], pins['ROW_2'], pins['ROW_3'], pins['ROW_4'], pins['COL_1'], pins['COL_2'], pins['COL_3'], pins['COL_4'])

def initialiseControls(config, sortedlist):
    for ctrlid in sortedlist:
        hardwaretype = config['local']['controls'][ctrlid]['hardware'] 
        if hardwaretype != 'instructions':
            controlconfig = config['local']['controls'][ctrlid]
            if hardwaretype == 'phonestylemenu': # 2 buttons, RGB LED
                controls.append(SHControlPhoneStyleMenu(controlconfig))                
            elif hardwaretype == 'bargraphpotentiometer': #10k pot, 10 LEDs
                controls.append(SHControlBargraphPot(controlconfig))
            elif hardwaretype == 'combo7SegColourRotary': #I2C 7Seg, button, rotary, RGB
                controls.append(SHControlCombo7SegColourRotary(controlconfig))                
            elif hardwaretype == 'switchbank': #Four switches, four LEDs
                controls.append(SHControlSwitchbank(controlconfig))                
            elif hardwaretype == 'illuminatedbutton': #one button, one LED
                controls.append(SHControlIlluminatedButton(controlconfig))                
            elif hardwaretype == 'potentiometer': #slide or rotary 10k pot
                controls.append(SHControlPot(controlconfig))                
            elif hardwaretype == 'illuminatedtoggle': #one switch, one LED            
                controls.append(SHControlIlluminatedToggle(controlconfig))                
            elif hardwaretype == 'fourbuttons': #four buttons
                controls.append(SHControlFourButtons(controlconfig))                
            elif hardwaretype == 'keypad': #four rows, four cols
                controls.append(SHControlKeypad(controlconfig))                
            else:
                print "Unknown control type in config file"
                controls.append(SHControl(controlconfig))
