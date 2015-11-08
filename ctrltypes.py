# Spacehack Control type definitions

import controls
import random

def getCtrlClass(ctrltype):
    types = {
       'button':   ButtonControl,
       'toggle':   ToggleControl,
       'selector': SelectorControl,
       'colour':   ColourControl,
       'words':    WordsControl,
       'verbs':    VerbsControl,
       'pin':      PinControl
       }
    return types[ctrltype]

def pickNewControl(ictrl, sctrl):
    """ Return an appropriate control object """
    imodes = [x for x in ictrl['supported'] if 'enabled' not in x or x['enabled'] == 1]
    imode = random.choice(imodes)
    return getCtrlClass(imode['type'])(ictrl, sctrl, imode)

class BaseControl:
    """ Note this can't actually be instantiated! """
    def __init__(self, ictrl, sctrl, imode):
        # Physical control information
        self.ictrl = ictrl
        # Logical control information
        self.sctrl = sctrl
        # Basic setup
        ctype = imode['type']
        atype = self.archetype()
        if not ctype in self.supportedTypes():
            raise ValueError("Incompatible control type %s for control archetype %s" % [ctype, atype])
        # Set up the name and type, copy the definition, configure, and enable the control
        self.pickName()
        self.sctrl['type'] = ctype
        self.sctrl['definition'] = dict(imode)
        self._configure()
        self.sctrl['enabled'] = 1
    
    def _configure(self):
        pass
    
    @property
    def id(self):
        return self.ictrl['id']
    
    @property
    def ctrldef(self):
        return self.sctrl['definition']
    
    @property
    def name(self):
        if 'name' in self.sctrl:
            return self.sctrl['name']
        else:
            return ''
    
    @property
    def type(self):
        return self.sctrl['type']
    
    @property
    def value(self):
        if 'value' in self.ctrldef:
            return self.ctrldef['value']
        else:
            return ''
    
    @property
    def assignable(self):
        return 'assignable' in self.ctrldef and self.ctrldef['assignable']
    
    @property
    def scalefactor(self):
        if 'scalefactor' in self.ctrldef:
            return self.ctrldef['scalefactor']
        return 1.0
    
    def supportedTypes(self):
        """ What control types are supported?  The default is just the archetype """
        return [ self.archetype() ]
    
    def pickName(self):
        if 'fixedname' in self.ictrl:
            self.sctrl['name'] = self.ictrl['fixedname']
        else:
            self.sctrl['name'] = controls.getControlName(self.ictrl['width'], 2, 12)
    
    def _pickValue(self, exclude=None):
        """ Pick a value, optionally excluding the current one """
        everything = set( self.validValues() )
        return random.choice( list( everything - set([exclude]) ) )
    
    def randomize(self):
        """ Randomize the current control value, if permitted """
        if self.assignable:
            self.ctrldef['value'] = self._pickValue()
    
    def pickTargetValue(self):
        return self._pickValue(self.value)
    
    def acknowledgeUpdate(self, value):
        """ Should we acknowledge updates for the given value? """
        return true
    
    def recordValue(self, value):
        """ Record a received value for this control """
        """ Indicate whether the value was updated """
        if value in self.validValues() and value != self.value:
            self.ctrldef['value'] = value
            return self.acknowledgeUpdate(value)
        else:
            return false

class ButtonControl(BaseControl):
    def archetype(self):
        return 'button'
    def validValues(self):
        return ['0','1']
    def pickTargetValue(self):
        return '1'
    def getActionString(self, targetvalue):
        return controls.getButtonAction(self.name)
    def acknowledgeUpdate(self, value):
        """ Should we acknowledge updates for the given value? """
        return (value=='1')

class ToggleControl(BaseControl):
    def archetype(self):
        return 'toggle'
    def validValues(self):
        return ['0','1']
    def getActionString(self, targetvalue):
        return controls.getToggleAction(self.name, int(targetvalue))

class SelectorControl(BaseControl):
    def archetype(self):
        return 'selector'
    @property
    def range(self):
        return range(self.ctrldef['min'], self.ctrldef['max'] + 1)
    def validValues(self):
        return [str(x) for x in self.range]
    def getActionString(self, targetvalue):
        return controls.getSelectorAction(self.name, self.range, int(targetvalue), int(self.value))

class ColourControl(BaseControl):
    def archetype(self):
        return 'colour'
    def validValues(self):
        return self.ctrldef['values']
    def getActionString(self, targetvalue):
        return controls.getColourAction(self.name, targetvalue)

class WordsControl(BaseControl):
    def archetype(self):
        return 'words'
    def validValues(self):
        return self.ctrldef['pool']
    def getActionString(self, targetvalue):
        ctrldef = self.ctrldef
        if 'list' in ctrldef:
            if ctrldef['list'] == 'passwd':
                return controls.getPasswdAction(self.name, targetvalue)
            elif ctrldef['list'] == 'verbs':
                return controls.getVerbListAction(self.name, targetvalue)
        return controls.getWordAction(self.name, targetvalue)
    def _configure(self):
        ctrldef = self.ctrldef
        if 'fixed' in ctrldef and ctrldef['fixed']:
            ctrldef['pool'] = ctrldef['list']
        else:
            words = self._getWords()
            finished = False
            while not finished:
                wordpool = random.sample(words, ctrldef['quantity'])
                # If this control is displaying two words, ensure there's space
                if ctrldef['quantity'] == 2:
                    total_length = sum([len(word) for word in wordpool])
                    max_length = self.ictrl['width']
                    if total_length < max_length:
                        finished = True
                else:
                    finished = True
            ctrldef['pool'] = sorted(wordpool)
    
    def _getWords(self):
        ctrldef = self.ctrldef
        # TODO: Consider making 'safe' another type of 'list'
        if 'safe' in ctrldef and ctrldef['safe']:
            return controls.safewords
        elif 'list' in ctrldef:
            if ctrldef['list']=='passwd':
                return controls.passwd
            elif ctrldef['list']=='verbs':
                return controls.verbs
        return self._defaultWords()
    
    def _defaultWords(self):
        return controls.allcontrolwords

# NOTE: It looks like 'verbs' can now be done with 'words'
class VerbsControl(WordsControl):
    def archetype(self):
        return 'verbs'
    def getActionString(self, targetvalue):
        return controls.getVerbListAction(self.name, targetvalue)
    def _defaultWords(self):
        return controls.verbs

class PinControl(BaseControl):
    def archetype(self):
        return 'pin'
    def randomize(self):
        self.ctrldef['value'] = ''
    def validValues(self):
        return [format(x,'04d') for x in range(10000)]
    def getActionString(self, targetvalue):
        return controls.getPinAction(self.name, targetvalue)
