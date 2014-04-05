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
    
    def __init__(self, pinData, pinClock, pinCS, numDevices):
        self.status = [0 for i in range(64)]
        self.spidata = [0 for i in range(16)]
        self.SPI_MOSI = pinData
        self.SPI_CLK = pinClock
        self.SPI_CS = pinCS
        if numDevices <=0 or numDevices > 8:
            numDevices = 8
        self.maxDevices = numDevices
        GPIO.setup(self.SPI_MOSI, GPIO.OUT)
        GPIO.setup(self.SPI_CLK, GPIO.OUT)
        GPIO.setup(self.SPI_CS, GPIO.OUT)
        GPIO.output(self.SPI_CS, GPIO.HIGH)
        for i in range(self.maxDevices):
            self.spiTransfer(i, OP_DISPLAYTEST, 0)
            self.setScanLimit(i, 7)
            self.spiTransfer(i, self.OP_DECODEMODE, 0)
            self.clearDisplay(i)
            self.shutdown(i, True)

    def getDeviceCount(self):
        return self.maxDevices

    def shutdown(self, addr, b):
        if addr < 0 or addr >= self.maxDevices:
            return
        elif b:
            self.spiTransfer(addr, self.OP_SHUTDOWN, 0)
        else:
            self.spiTransfer(addr, self.OP_SHUTDOWN, 1)

    def setScanLimit(self, addr, limit):
        if addr < 0 or addr >= self.maxDevices:
            return
        elif limit >=0 and limit < 8:
            self.spiTransfer(addr, self.OP_SCANLIMIT, limit)

    def setIntensity(self, addr, intensity):
        if addr < 0 or addr >= self.maxDevices:
            return
        elif intensity >=0 and intensity < 16:
            self.spiTransfer(self.OP_INTENSITY, intensity)

    def clearDisplay(self, addr):
        if addr<0 or addr >= self.maxDevices:
            return
        offset = addr * 8
        for i in range(8):
            self.status[offset + i] = 0
            self.spiTransfer(addr, i+1, self.status[offset+i])

    def setLed(self, addr, row, col, state):
        if addr<0 or addr >= self.maxDevices or row < 0 or row>7 or col < 0 or col > 7:
            return
        offset = addr * 8
        val = 2 ** (7-col)
        if state:
            self.status[offset + row] |= val
        else:
            self.status[offset + row] &= 255-val
        self.spiTransfer(addr, row+1, self.status[offset + row])

    def setRow(self, addr, row, value):
        if addr<0 or addr >= self.maxDevices or row < 0 or row>7 or value < 0 or value > 255:
            return
        offset = addr * 8
        self.status[offset + row] = value
        self.spiTransfer(addr, row+1, self.status[offset + row])

    def setColumn(self, addr, col, value):
        if addr<0 or addr >= self.maxDevices or col < 0 or col>7 or value < 0 or value > 255:
            return
        for i in range(8):
            val = value >> (7-row)
            val = val & 1
            self.setLed(addr, row, col, val)

    def shiftOut(self, dataByte):
        for j in range(8):
            GPIO.output(self.SPI_CLK, GPIO.LOW)
            if dataByte >> j & 1 == 0:
                GPIO.output(self.SPI_MOSI, GPIO.LOW)
            else:
                GPIO.output(self.SPI_MOSI, GPIO.HIGH)
            GPIO.output(self.SPI_CLK, GPIO.HIGH)
        
    def spiTransfer(self, addr, opcode, data):
        offset = addr*2
        maxbytes = self.maxDevices * 2
        for i in range(maxbytes):
            self.spiData[offset + 1] = opcode
            self.spiData[offset] = data
            GPIO.output(self.SPI_CS, GPIO.LOW)
            for j in range(maxbytes):
                self.shiftOut(self.spiData[maxbytes-j])
            GPIO.output(self.SPI_CS, GPIO.HIGH)
