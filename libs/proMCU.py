import ctypes
import struct
import time

#msg for CAN of 35 smart car
#ID: 0x199, read this gun message from CAN
class Gun_read:
    def __init__(self, Mode=0x00 , Temper = 0x00, Monitor = 0x00, BrakeLight = 0x00 , BrakePadel = 0x00, Depth=0x00 ):
        #byte[0] 0:manual control, 1: pc control
        self.Mode = Mode
        #byte[1] control Depth
        self.Depth = Depth
        self.Temper = Temper
        self.Button = Monitor
        self.BrakeLight = BrakeLight
        self.BrakePadel = BrakePadel
        pass

#ID: 0x200, send this gun message to CAN
class Gun_send:
    def __init__(self, Mode = 0x00 , Dir = 3, Depth = 0x00 , Light = 2):
        #byte[0] control Mode, 0:manual control, 1:pc control
        self.Mode = Mode
        self.Dir = Dir
        #byte[2] control Depth
        self.Depth = Depth
        self.Light = Light
        pass

#ID: 0X100, read this brake message from CAN
class Brake_read:
    def __init__(self,Mode = 0x00, Temper = 0x00, Estop = 0x00, Depth = 0x00 ):
        self.Mode = Mode
        self.Temper = Temper
        self.Estop = Estop
        self.Depth = Depth
        pass

#ID: 0x99, send this message of brake to CAN
class Brake_send:
    def __init__(self, Mode=0x00 , Dir = 3, Depth=0x00, Time = 100):
        #byte[0], 0:start braking, 1:stop braking
        self.Mode = Mode
        self.Dir = Dir
        #byte[2], control Depth
        self.Depth = Depth
        self.Time = Time

#ID: 0x401, read this steer message from CAN
class Steer_read:
    def __init__(self, Mode=0x00 , torque= 0x00 , exception= 0x00 , AngleH= 0x00 , AngleL= 0x00 , Calib= 0x00 , check= 0x00 ):
        #byte[0], 0x00:stop control, 0x10: manul control, 0x20: pc control, 0x55: xor check error
        self.Mode = Mode
        #byte[1], torque
        self.Torque = torque
        #byte[2], error message
        #0x21    0x22    0x23    0x24    0x25    0x26
        #0x32    0x34    0x35
        #0x31
        self.EException = exception
        #byte[3]
        self.AngleH = AngleH
        #byte[4], Angle = byte[3] * 256 + byte[4] - 1024
        self.AngleL = AngleL
        #byte[5], no, done, failed, success
        self.Calib = Calib
        self.By6 = 0x00
        #byte[7], xor check
        self.Check = check

class Steer_send:
    def __init__(self, Mode= 0x00, AngleH = 0x00, AngleL= 0x00 , Calib= 0x00):
        #byte[0], 0x00:stop control, 0x10:manual control, 0x20:pc control
        self.Mode = Mode
        #byte[3]
        self.AngleH = AngleH
        #byte[4]
        self.AngleL = AngleL
        #byte[5], 0x55, only worked when manual control
        self.Calib = Calib

class GNSS_read:
    def __init__(self):
        self.length = 0
        self.mode = 0
        self.time1 = 0
        self.time2 = 0
        self.num = 0
        self.lat = 0
        self.lon = 0
        self.height = 0
        self.v_n = 0
        self.v_e = 0
        self.v_earth = 0
        self.roll = 0
        self.pitch = 0
        self.head = 0
        self.a_n = 0
        self.a_e = 0
        self.a_earth = 0
        self.v_roll = 0
        self.v_pitch = 0
        self.v_head = 0
        self.status = 0
        pass

class MCU:
    def __init__(self):
        self.gunRead = Gun_read()
        self.gunSend = Gun_send()
        self.brakeRead = Brake_read()
        self.brakeSend = Brake_send()
        self.steerRead = Steer_read()
        self.steerSend = Steer_send()
        self.gnssRead = GNSS_read()

        self.lib = ctypes.CDLL('/home/ubuntu/workspace/TJUPy/libs/MCU/MCUlib.so')
        self.MCUinit = self.lib.init
        #run init
        self.MCUinit()

        self.UARTreadGNSS = self.lib.readGNSS
        self.UARTreadGNSS.restype = ctypes.POINTER(ctypes.c_ubyte* 61)
        self.bytes = []
        self.bytes_new = []
        
        self.CANreadGun = self.lib.readGun
        self.CANreadGun.restype = ctypes.POINTER(ctypes.c_ubyte * 8)

        self.CANreadBrake = self.lib.readBrake
        self.CANreadBrake.restype = ctypes.POINTER(ctypes.c_ubyte * 8)

        self.CANreadSteer= self.lib.readSteer
        self.CANreadSteer.restype = ctypes.POINTER(ctypes.c_ubyte * 8)

        self.CANsendGun = self.lib.sendGun
        self.CANsendGun.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]

        self.CANsendBrake = self.lib.sendBrake
        self.CANsendBrake.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]

        self.CANsendSteer= self.lib.sendSteer
        self.CANsendSteer.argtypes = [ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ubyte]
        

    def readGNSS(self):
        if len(self.bytes_new) < 61:
            self.bytes_new = self.UARTreadGNSS().contents
            #print(self.bytes_new)
        self.bytes = self.bytes_new
        self.bytes_new = self.UARTreadGNSS().contents
        mark = 0
        for i in range(0,59):
            mark = i
            if self.bytes[i] == 0xaa and self.bytes[i+1] == 0x55:
                break
        if mark == 58 and not(self.bytes[59] == 0xaa and self.bytes_new[0] == 0x55):
            mark = 60
        res = self.bytes[mark:60]
        for i in range(0,mark):
            res.append(self.bytes_new[i])
        result  = struct.unpack('<2B1H1I1B8i1I6h1B',bytearray(res[2:]))
        self.gnssRead.length = result[0]
        self.gnssRead.mode = result[1]
        self.gnssRead.time1 = result[2]
        self.gnssRead.time2 = result[3]
        self.gnssRead.num = result[4]
        self.gnssRead.lat = float (result[5] )/ (10 ** 7)
        self.gnssRead.lon = float (result[6] )/ (10**7)
        self.gnssRead.height = float (result[7] )/ (1000)
        self.gnssRead.v_n = float (result[8] )/ (1000)
        self.gnssRead.v_e = float (result[9] )/ (1000)
        self.gnssRead.v_earth = float (result[10] )/ (1000)
        self.gnssRead.roll = float (result[11] )/ (1000)
        self.gnssRead.pitch = float (result[12] )/ (1000)
        self.gnssRead.head = float (result[13] )/ (1000)
        self.gnssRead.a_n = float (result[14] )/ (1000)
        self.gnssRead.a_e = float (result[15] )/ (1000)
        self.gnssRead.a_earth = float (result[16] )/ (1000)
        self.gnssRead.v_roll = float (result[17] )/ (1000)
        self.gnssRead.v_pitch = float (result[18] )/ (1000)
        self.gnssRead.v_head = float (result[19] )/ (1000)
        self.gnssRead.status = result[20] & 0x3f

    def readGun(self):
        read = self.CANreadGun().contents
        self.gunRead.Mode = read[0]
        self.gunRead.Temper = read[1]
        self.gunRead.Button = int (read[2] & 0x08)/8
        self.gunRead.BrakeLight = int (read[2] & 0x40)/64
        self.gunRead.BrakePadel = int (read[2] & 0x80) / 128
        self.gunRead.Depth = int(read[3] & 0x0f) * 256 + read[4]

    def readBrake(self):
        read = self.CANreadBrake().contents
        self.brakeRead.Mode = read[0]
        self.brakeRead.Temper = read[1]
        self.brakeRead.Estop = int (read[2] & 0x80) / 128
        self.brakeRead.Depth = int(read[3] & 0x0f) * 256 + read[4]

    def readSteer(self):
        read = self.CANreadSteer().contents
        while read[7] != read[0] ^ read[1] ^ read[2] ^ read[3] ^ read[4] ^ read[5] ^ read[5] ^ read[6]:
            read = self.CANreadSteer().contents

        self.steerRead.Mode = read[0]
        self.steerRead.AngleH = read[3]
        self.steerRead.AngleL = read[4]
        self.steerRead.Check = read[7]

    def sendBrake(self):
        self.CANsendBrake(self.brakeSend.Mode, self.brakeSend.Dir, self.brakeSend.Depth, self.brakeSend.Time)

    def sendGun(self):
        self.CANsendGun(self.gunSend.Mode, self.gunSend.Dir, self.gunSend.Depth, self.gunSend.Light )

    def sendSteer(self):
        self.CANsendSteer(self.steerSend.Mode, self.steerSend.AngleH, self.steerSend.AngleL, self.steerSend.Calib)

    def sendStop(self):
        self.CANsendBrake(self.brakeSend.Mode, self.brakeSend.Dir, self.brakeSend.Depth, self.brakeSend.Time)
