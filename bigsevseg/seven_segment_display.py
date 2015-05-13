import sys
sys.path.append('./bigsevseg')
import Adafruit_MCP230xx as ExpIO
import time
sevenSeg = ExpIO.Adafruit_MCP230XX(0x20, 16)

#    A
#    _
#F  |_| B
#E  |_| C
#
#    D
#
#Centre: G

#seg = dict(A = 7, B = 9, C = 10, D = 11, E = 12, F = 13, G = 14)

seg = dict(A = 13, B = 9, C = 12, D = 14, E = 7, F = 11, G = 10)

digit_1 = [     'B', 'C'                    ]
digit_2 = ['A', 'B',      'D', 'E',      'G']
digit_3 = ['A', 'B', 'C', 'D',           'G']
digit_4 = [     'B', 'C',           'F', 'G']
digit_5 = ['A',      'C', 'D',      'F', 'G']
digit_6 = ['A',      'C', 'D', 'E', 'F', 'G']
digit_7 = ['A', 'B', 'C'                    ]
digit_8 = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
digit_9 = ['A', 'B', 'C', 'D',      'F', 'G']
digit_0 = ['A', 'B', 'C', 'D', 'E', 'F'     ]

test_1 = ['A']
test_2 = ['B']
test_3 = ['C']
test_4 = ['D']
test_5 = ['E']
test_6 = ['F']
test_7 = ['G']

digits = [digit_0, digit_1, digit_2, digit_3, digit_4, digit_5, digit_6, digit_7, digit_8, digit_9]
tests = [test_1, test_2, test_3, test_4, test_5, test_6, test_7]

for i in seg:
    sevenSeg.config(seg[i], ExpIO.Adafruit_MCP230XX.OUTPUT)

def clear():
    for i in seg:
        sevenSeg.output(seg[i], 0)

def digit(digit):
    for s in digit:
        sevenSeg.output(seg[s], 1)
        
def displayDigit(num):
    clear()
    digit(digits[num])

if __name__ == "__main__":
    while True:
        for i in range(10):
            time.sleep(1)
            displayDigit(i)
