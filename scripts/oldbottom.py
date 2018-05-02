import sys
import time
import thread
import math
sys.path.append("../libs")
from proContext import *
from proMCU import *
import UTM

global speed_set
global speed_back
global speed_mode
global output
global speed_way
global canSpeed
global canSteer
global planSteer
global lastSteer
global uartSpeed

output = 0


mcu = MCU()
ctx = proContext()

pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:8080')

pubCAN = ctx.socket(zmq.PUB)
pubCAN.bind('tcp://*:8088')
def main():
    global mcu
    global uartSpeed
    global canSpeed
    global canSteer
    global planSteer
    global lastSteer


    canSpeed = 0
    uartSpeed = 0
    canSteer = 0

    lastCmd = 0
    lastSteer = 0
    control = True

    thread.start_new_thread(readGNSS, ())
    thread.start_new_thread(readSteer, ())
    #thread.start_new_thread(readGun, ())
    #thread.start_new_thread(readBrake, ())
    thread.start_new_thread(recvSteer, ())
    thread.start_new_thread(recvSpeed, ())

    i = 0
    while True:
        i = (i+1) % 9999
        time.sleep(1)

def readGNSS():
    global mcu
    global pub
    global canSpeed
    global canSteer
    global uartSpeed
    imuError = 0.5
    i = 0
    while True:
        time.sleep(0.05)
        mcu.readGNSS()
        uartSpeed = math.sqrt (mcu.gnssRead.v_n ** 2 + mcu.gnssRead.v_e ** 2 + mcu.gnssRead.v_earth ** 2 )
        content = {"Length":mcu.gnssRead.length,"Mode":mcu.gnssRead.mode,"Time1":mcu.gnssRead.time1,"Time2":mcu.gnssRead.time2, \
                   "Num":mcu.gnssRead.num,"Lat":mcu.gnssRead.lat,"Lon":mcu.gnssRead.lon,"Height":mcu.gnssRead.height, \
                   "V_n":mcu.gnssRead.v_n,"V_e":mcu.gnssRead.v_e,"V_earth":mcu.gnssRead.v_earth, \
                   "Roll":mcu.gnssRead.roll,"Pitch":mcu.gnssRead.pitch,"Head":mcu.gnssRead.head + imuError, \
                   "A_n":mcu.gnssRead.a_n,"A_e":mcu.gnssRead.a_e,"A_earth":mcu.gnssRead.a_earth, \
                   "V_roll":mcu.gnssRead.v_roll,"V_pitch":mcu.gnssRead.v_pitch,"V_head":mcu.gnssRead.v_head, \
                   "Status":mcu.gnssRead.status,"Speed":uartSpeed}
        if content['Head'] > 360:
            content['Head'] = content['Head'] - 360
        i = (i+1) % 9999
        if i% 40 ==0:
            print(content)
            print('**********************************************************************************************************************************')
        pub.sendPro('CurGNSS',content)
    pass

def readSteer():
    global mcu
    global pub
    global pubCAN
    global canSpeed
    global canSteer
    select = 1
    i = 0
    while True:
        time.sleep(0.02)
        i = i + 1
        if select == 1:
            select = 2
            mcu.readSteer()
            content = {'Mode':mcu.steerRead.Mode, \
                       'AngleH':mcu.steerRead.AngleH, 'AngleL':mcu.steerRead.AngleL, \
                       'Check':mcu.steerRead.Check}
            canSteer = mcu.steerRead.AngleH * 256 + mcu.steerRead.AngleL - 1024
            if i % 40 == 0:
                print(content)
                print('--------------------------------------------------------------------------------------------------------------------------------')
                print('now steer is :  ' ,canSteer)
                print('--------------------------------------------------------------------------------------------------------------------------------')
            pubCAN.sendPro('CANSteer',content)
            continue

        if select == 2:
            select = 3
            mcu.readGun()
            content = {'Mode':mcu.gunRead.Mode, 'Temper':mcu.gunRead.Temper, 'Button': mcu.gunRead.Button, 'BrakeLight':mcu.gunRead.BrakeLight,\
                       'BrakePadel': mcu.gunRead.BrakePadel, 'Depth':mcu.gunRead.Depth}
            if i % 40 == 0:
                print(content)
                print('--------------------------------------------------------------------------------------------------------------------------------')
                print('--------------------------------------------------------------------------------------------------------------------------------')
            pubCAN.sendPro('CANGun',content)
            continue

        if select == 3:
            select = 1
            mcu.readBrake()
            content = {'Mode':mcu.brakeRead.Mode, 'Temper':mcu.brakeRead.Temper, 'Estop': mcu.brakeRead.Estop, 'Depth':mcu.brakeRead.Depth}
            if i % 40 == 0:
                print(content)
                print('--------------------------------------------------------------------------------------------------------------------------------')
                print('--------------------------------------------------------------------------------------------------------------------------------')
            pubCAN.sendPro('CANBrake',content)
            continue
    pass

def readGun():
    global mcu
    global pubCAN
    while True:
        time.sleep(0.05)
        mcu.readGun()
        content = {'Mode':mcu.gunRead.Mode, 'Temper':mcu.gunRead.Temper, 'Button': mcu.gunRead.Button, 'BrakeLight':mcu.gunRead.BrakeLight, 'BrakePadel': mcu.gunRead.BrakePadel, 'Depth':mcu.gunRead.Depth}
        pubCAN.sendPro('CANGun',content)


def readBrake():
    global mcu
    while True:
        time.sleep(0.05)
        mcu.readBrake()
        content = {'Mode':mcu.brakeRead.Mode, 'Temper':mcu.brakeRead.Temper, 'Estop': mcu.brakeRead.Estop, 'Depth':mcu.brakeRead.Depth}
        pubCAN.sendPro('CANBrake',content)


def alpha(v):
    return 100/ (v**2)

def sendCmd(content):
    global mcu
    global uartSpeed
    global planSteer
    if content['Who'] == 'Brake':
        mcu.brakeSend.Mode = content['Mode']
        mcu.brakeSend.Dir = content['Dir']
        mcu.brakeSend.Depth = content['Depth']
        mcu.brakeSend.Time = content['Forth']
        mcu.sendBrake()
        pass
    elif content['Who'] == 'Gun':
        mcu.gunSend.Mode = content['Mode']
        mcu.gunSend.Dir = content['Dir']
        mcu.gunSend.Depth = content['Depth']
        mcu.gunSend.Light = content['Forth']
        mcu.sendGun()
        pass
    elif content['Who'] == 'Steer':
        steer = content['Value']
        #print('send steer is : ',steer)
        mcu.steerSend.Mode = content['Mode']
        mcu.steerSend.AngleH =  int( (steer + 1024)/256)
        mcu.steerSend.AngleL =  int ( (steer + 1024) % 256)
        mcu.sendSteer()
        pass
    pass

def recvSpeed():
    global mcu
    subSpeed = ctx.socket(zmq.SUB)
    subSpeed.connect('tcp://localhost:8082')
    subSpeed.setsockopt(zmq.SUBSCRIBE,'Cmd')
    while True:
        con = subSpeed.recvPro()
        sendCmd(con)

def recvSteer():
    global mcu
    global lastSteer
    global canSpeed
    global uartSpeed
    steer_limit = []
    def loadSteerConfig():
        with open('config') as f:
            for line in f.readlines():
                steer_limit.append(int(line))
    loadSteerConfig()
    subSteer = ctx.socket(zmq.SUB)
    subSteer.connect('tcp://localhost:8081')
    subSteer.setsockopt(zmq.SUBSCRIBE,'PlanSteer')
    lastSteer = 0
    steer = 0
    i = 0
    while True:
        content = subSteer.recvPro()
        #content = {'Value':0,'Mode':0x10}
        steer = content['Value']
        #print('canSpeed',canSpeed)
        if uartSpeed > 0:
            canSpeed = int(uartSpeed * 3.6)
            gap = 0
            if (canSpeed < len(steer_limit)):
                gap = steer_limit[int(canSpeed)]
            if steer - lastSteer > gap:
                steer = lastSteer + gap
            elif steer - lastSteer < -1 * gap:
                steer = lastSteer - gap
            lastSteer = steer
        #content = {'Who':'Steer','Mode':content['Mode'],'Value':steer}
        steer = min(520, max(steer, -520))
        content = {'Who':'Steer','Mode':content['Mode'],'Value':steer}
        i = (i + 1)% 9999
        if i % 50 == 0:
            print('========================================================================================control')
            print('control content is : ',content)
            print('========================================================================================control')
            pass
        sendCmd(content)
    pass
    

if __name__ == "__main__":
    main()
