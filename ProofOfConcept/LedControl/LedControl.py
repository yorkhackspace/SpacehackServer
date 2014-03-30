from math import sin, pi
import Adafruit_BBIO.GPIO as GPIO

class LedControl:
    OP_NOOP = 0
    OP_DIGIT0 = 1
    OP_DIGIT1 = 2
    OP_DIGIT2 = 3
    OP_DIGIT3 = 4
    OP_DIGIT4 = 5
    OP_DIGIT5 = 6
    OP_DIGIT6 = 7
    OP_DIGIT7 = 8
    OP_DECODEMODE = 9
    OP_INTENSITY = 10
    OP_SCANLIMIT = 11
    OP_SHUTDOWN = 12
    OP_DISPLAYTEST = 15
    
    self.status = [0 for i in range(64)]
    self.spidata = [0 for i in range(16)]
    def __init__(self, pinData, pinClock, pinCS, numDevices):
        self.SPI_MOSI = pinData
        self.SPI_CLK = pinClock
        self.SPI_CS = pinCS
        if numDevices <=0 or numDevices > 8:
            numDevices = 8
        self.maxDevices = numDevices
        GPIO.setup(SPI_MOSI, GPIO.OUTPUT)
        GPIO.setup(SPI_CLK, GPIO.OUTPUT)
        GPIO.setup(SPI_CS, GPIO.OUTPUT)
        GPIO.output(SPI_CS, GPIO.HIGH)
        for i in range(self.maxDevices):
            spiTransfer(self, i, OP_DISPLAYTEST, 0)
            setScanLimit(self, i, 7)
            spiTransfer(self, i, OP_DECODEMODE, 0)
            clearDisplay(self, i)
            shutdown(self, i, True)

    def getDeviceCount(self):
        return self.maxDevices

    def shutdown(self, addr, b):
        if addr < 0 or addr >= self.maxDevices:
            return
        elif b:
            spiTransfer(self, addr, OP_SHUTDOWN, 0)
        else:
            spiTransfer(self, addr, OP_SHUTDOWN, 1)

    def setScanLimit(self, addr, limit):
        if addr < 0 or addr >= self.maxDevices:
            return
        elif limit >=0 and limit < 8:
            spiTransfer(addr, OP_SCANLIMIT, limit)

    def setIntensity(self, addr, intensity):
        if addr < 0 or addr >= self.maxDevices:
            return
        elif intensity >=0 and intensity < 16:
            spiTransfer(self, OP_INTENSITY, intensity)

    def clearDisplay(self, addr):
        if addr<0 or addr >= self.maxDevices:
            return
        offset = addr * 8
        for i in range(8):
            self.status[offset + i] = 0
            spiTransfer(self, addr, i+1, self.status[offset+i])

    def setLed(self, addr, row, col, state):
        if addr<0 or addr >= self.maxDevices or row < 0 or row>7 or col < 0 or col > 7:
            return
        offset = addr * 8
        val = 2 ** (7-col)
        if state:
            self.status[offset + row] |= val
        else:
            self.status[offset + row] &= 255-val
        spiTransfer(self, addr, row+1, self.status[offset + row])

    def setRow(self, addr, row, value):
        if addr<0 or addr >= self.maxDevices or row < 0 or row>7 or value < 0 or value > 255:
            return
        offset = addr * 8
        self.status[offset + row] = value
        spiTransfer(self, addr, row+1, self.status[offset + row])

    def setColumn(self, addr, col, value):
        if addr<0 or addr >= self.maxDevices or col < 0 or col>7 or value < 0 or value > 255:
            return
        for i in range(8):
            val = value >> (7-row)
            val = val & 1
            setLed(self, addr, row, col, val)

    def spiTransfer(self, addr, opcode, data):
        offset = addr*2
        maxbytes = self.maxDevices * 2
        for i in range(maxbytes):
            self.spiData[offset + 1] = opcode
            self.spiData[offset] = data
            GPIO.output(self.SPI_CS, GPIO.LOW)
            for j in range(maxbytes):
                GPIO.shiftOut(self.SPI_MOSI, self.SPI_CLK, GPIO.MSBFIRST, self.spiData[maxbytes-j])
            GPIO.output(self.SPI_CS, GPIO.HIGH)
