import ctypes
import struct

class GNSS:
    def __init__(self):
        self.lib = ctypes.CDLL('/home/ubuntu/workspace/35SmartPy/libs/UART/UARTlib.so')
        #self.lib = ctypes.CDLL('./UART/UARTlib.o')
        self.init = self.lib.init
        #self.init()

        self.readGNSS = self.lib.readGNSS
        self.readGNSS.restype = ctypes.POINTER(ctypes.c_ubyte* 61)
        self.bytes = self.readGNSS().contents
        self.bytes_new = self.readGNSS().contents
        #for i in range(0,len(self.bytes_new)):
        #    self.bytes_new[i] = self.bytes_new[i] - 127

    def read(self):

        self.bytes = self.bytes_new
        self.byte_new = self.readGNSS().contents
        #for i in range(0,len(self.bytes_new)):
        #    self.bytes_new[i] = self.bytes_new[i] - 127
        mark = 0
        for i in range(0,60):
            mark = i
            if self.bytes[i] == 0xaa and self.bytes[i+1] == 0x55:
                break
        
        
        if mark == 59 and not(self.bytes[60] == 0xaa and self.bytes_new[1] == 0x55):
            mark = 61
        res = self.bytes[mark:61]

        for i in range(0,mark):
            res.append(self.bytes_new[i])

        result    = struct.unpack('<2B1H1I1B8i1I6h1B1B',bytearray(res[2:]))

        self.length = result[0]
        self.mode = result[1]
        self.time1 = result[2]
        self.time2 = result[3]
        self.num = result[4]
        self.lat = float (result[5] )/ (10 ** 7)
        self.lon = float (result[6] )/ (10**7)
        self.height = float (result[7] )/ (1000)
        self.v_n = float (result[8] )/ (1000)
        self.v_e = float (result[9] )/ (1000)
        self.v_earth = float (result[10] )/ (1000)
        self.roll = float (result[11] )/ (1000)
        self.pitch = float (result[12] )/ (1000)
        self.head = float (result[13] )/ (1000)
        self.a_n = float (result[14] )/ (1000)
        self.a_e = float (result[15] )/ (1000)
        self.a_earth = float (result[16] )/ (1000)
        self.v_roll = float (result[17] )/ (1000)
        self.v_pitch = float (result[18] )/ (1000)
        self.v_head = float (result[19] )/ (1000)
        self.status = result[20]
