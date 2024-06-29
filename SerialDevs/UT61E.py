'''This file is designed to connect to ant interface with a
    UNI-T UT61E with the rs232 backpack. It has not been tested
    with any other backpack or multimeter. The starting point
    for this is based on these posts:
        
        http://www.starlino.com/uni-t-ut61e-multimiter-serial-protocol-reverse-engineering.html
        http://gushh.net/blog/ut61e-protocol/
        '''

import asyncio
import serial

def comAndVom(port):
    """This is just a testing function to start to get used/play with the dmm. 
       My goal is to connect to the DMM, write it's data to the stdout, and 
       hopefully be able to pause data collection until a wanted time, then 
       get a value and pause again

    Args:
        port (str): String name of the dmm port eg. "COM 5"
    """
    
    dmm = serial.Serial(port, baudrate=19200, bytesize=7, parity=serial.PARITY_ODD,
                        stopbits=serial.STOPBITS_ONE, timeout=2)
    dmm.dtr = False
    dmm.rts = False
    # dmm.open()
    
    print(dmm.readline())
    dmm.dtr = True
    print(dmm.readline())
    dmm.dtr = False
    print(dmm.readline())
    
    dmm.close()
    
class UT61E():
    
    def __init__(self, com_port, timeout=2):
        self.dmm = serial.Serial(com_port, baudrate=19200, bytesize=7, parity=serial.PARITY_ODD,
                    stopbits=serial.STOPBITS_ONE, timeout=timeout)
        self.dmm.dtr = True #was flase
        self.dmm.rts = False
        self.dmm.read_all()
    
    def read_v(self):
        # self.dmm.dtr = True
        self.dmm.flushInput()
        reading = self.dmm.readline().strip(b'\n\r')
        while reading.startswith(b'\x00') or len(reading) != 12:
            reading = self.dmm.readline().strip(b'\n\r')
        # self.dmm.dtr = False
                
        range = chr(reading[0])
        value = reading[1:6].decode()
        mode = reading[6]
        status = reading[7]
        options = reading[8:]
        
        range = int(range) + 1
        value = value[:range] + '.' + value[range:]
        if status & 0b100 == 4:
            value = '-' + value
        value = float(value)

        return value

    def close(self):
        self.dmm.close()

if __name__ == "__main__":
    
    meter = UT61E('COM8')
    
    while True:
        print(meter.read_v())
    