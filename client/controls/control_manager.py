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
        
class SHControlBargraphPot(SHControl):
    
    def __init__(self, controlconfig):
        SHControl.__init__(self, controlconfig)
        bar = []
        for barnum in range(10):
            pin = pins['BAR_' + str(barnum+1)]
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
            bar.append(pin)
            ADC.setup(pins['POT'])
        

def initialiseControls(config, sortedlist):
    for ctrlid in sortedlist:
        hardwaretype = config['local']['controls'][ctrlid]['hardware'] 
        if hardwaretype != 'instructions':
            pins = config['local']['controls'][ctrlid]['pins']
            if hardwaretype == 'phonestylemenu': # 2 buttons, RGB LED
                GPIO.setup(pins['BTN_1'], GPIO.IN, GPIO.PUD_DOWN)
                GPIO.setup(pins['BTN_2'], GPIO.IN, GPIO.PUD_DOWN)
                PWM.start(pins['RGB_R'], 0.0)
                PWM.start(pins['RGB_G'], 0.0)
                PWM.start(pins['RGB_B'], 0.0)
            elif hardwaretype == 'bargraphpotentiometer': #10k pot, 10 LEDs
                controls.append(SHControlBargraphPot(config['local']['controls'][ctrlid]))
            elif hardwaretype == 'combo7SegColourRotary': #I2C 7Seg, button, rotary, RGB
                #segment defined at module scope
                GPIO.setup(pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
                PWM.start(pins['RGB_R'], 1.0) #common anode so 1.0 = off, 0.0 = on
                PWM.start(pins['RGB_G'], 1.0)
                PWM.start(pins['RGB_B'], 1.0)
                #What to do about rotary?
            elif hardwaretype == 'switchbank': #Four switches, four LEDs
                for i in range(1,5):
                    GPIO.setup(pins['SW_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)
                    GPIO.setup(pins['LED_' + str(i)], GPIO.OUT)
                    GPIO.output(pins['LED_' + str(i)], GPIO.LOW)
            elif hardwaretype == 'illuminatedbutton': #one button, one LED
                GPIO.setup(pins['BTN'], GPIO.IN, GPIO.PUD_DOWN)
                GPIO.setup(pins['LED'], GPIO.OUT)
                GPIO.output(pins['LED'], GPIO.LOW)
            elif hardwaretype == 'potentiometer': #slide or rotary 10k pot
                ADC.setup(pins['POT'])
            elif hardwaretype == 'illuminatedtoggle': #one switch, one LED            
                GPIO.setup(pins['SW'], GPIO.IN, GPIO.PUD_DOWN)
                GPIO.setup(pins['LED'], GPIO.OUT)
                GPIO.output(pins['LED'], GPIO.HIGH) #common anode, so HIGH for off, LOW for on
            elif hardwaretype == 'fourbuttons': #four buttons
                for i in range(1,5):
                    GPIO.setup(pins['BTN_' + str(i)], GPIO.IN, GPIO.PUD_DOWN)
            elif hardwaretype == 'keypad': #four rows, four cols
                keypad = Keypad_BBB.keypad(pins['ROW_1'], pins['ROW_2'], pins['ROW_3'], pins['ROW_4'], 
                                           pins['COL_1'], pins['COL_2'], pins['COL_3'], pins['COL_4'])
            else:
                controls.append(SHControl(config['local']['controls'][ctrlid]))
