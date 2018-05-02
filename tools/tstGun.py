import sys
import time
import math
import threading
sys.path.append("../libs")
from proContext import *
from proMCU import *
import UTM

mcu = MCU()
is_exit = False

def readGNSS(num,show):
    global mcu
    i = 0
    while not is_exit:
        i = (i + 1) % 9999
        time.sleep(0.05)
        mcu.readGNSS()
        uartSpeed = math.sqrt (mcu.gnssRead.v_n ** 2 + mcu.gnssRead.v_e ** 2 + mcu.gnssRead.v_earth ** 2 )
        content = {"Length":mcu.gnssRead.length,"Mode":mcu.gnssRead.mode,"Time1":mcu.gnssRead.time1,"Time2":mcu.gnssRead.time2, \
                   "Num":mcu.gnssRead.num,"Lat":mcu.gnssRead.lat,"Lon":mcu.gnssRead.lon,"Height":mcu.gnssRead.height, \
                   "V_n":mcu.gnssRead.v_n,"V_e":mcu.gnssRead.v_e,"V_earth":mcu.gnssRead.v_earth, \
                   "Roll":mcu.gnssRead.roll,"Pitch":mcu.gnssRead.pitch,"Head":mcu.gnssRead.head , \
                   "A_n":mcu.gnssRead.a_n,"A_e":mcu.gnssRead.a_e,"A_earth":mcu.gnssRead.a_earth, \
                   "V_roll":mcu.gnssRead.v_roll,"V_pitch":mcu.gnssRead.v_pitch,"V_head":mcu.gnssRead.v_head, \
                   "Status":mcu.gnssRead.status,"Speed":uartSpeed}
        if content['Head'] > 360:
            content['Head'] = content['Head'] - 360
        if num == 0 and i%20 == 0 or num %5 == 0:
            if show == 'all':
                print(content)
            else:
                print(content[show])
    pass

steerContent = {}
def readCAN(num,show):
    global steerContent
    global mcu
    select = 1
    i = 0
    while not is_exit:
        time.sleep(0.02)
        i = i + 1
        if select == 1:
            select = 2
            mcu.readSteer()
            content = {'Mode':mcu.steerRead.Mode, \
                       'Angle':mcu.steerRead.AngleH * 256 + mcu.steerRead.AngleL - 1024}
            if num == 1 and i%50 == 0 or num %5 == 0:
                if show == 'all':
                    print(content)
                else:
                    print(content[show])

        if select == 2:
            select = 3
            mcu.readGun()
            content = {'Mode':mcu.gunRead.Mode, 'Temper':mcu.gunRead.Temper, 'Button': mcu.gunRead.Button, 'BrakeLight':mcu.gunRead.BrakeLight,\
                       'BrakePadel': mcu.gunRead.BrakePadel, 'Depth':mcu.gunRead.Depth}
            steerContent = content
            if num == 2 and i%50 == 0 or num%5 == 0:
                if show == 'all':
                    print(content)
                else:
                    print(content[show])
            continue

        if select == 3:
            select = 1
            mcu.readBrake()
            content = {'Mode':mcu.brakeRead.Mode, 'Temper':mcu.brakeRead.Temper, 'Estop': mcu.brakeRead.Estop, 'Depth':mcu.brakeRead.Depth}
            if num == 3 and i%50 == 0 or num%5 == 0:
                if show == 'all':
                    print(content)
                else:
                    print(content[show])
            continue
    pass

def handler(signum, frame):
    global is_exit
    is_exit = True
    print "receive a signal %d, is_exit = %d"%(signum, is_exit)


def sendCmd(content):
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

def main(args):

    tGNSS = threading.Thread(target = readGNSS, args = (-1,'all'))
    tCAN = threading.Thread(target = readCAN, args = (-1,'all'))

    tGNSS.setDaemon(True)
    tCAN.setDaemon(True)

    tGNSS.start()
    tCAN.start()

    alive = True
    while alive:
        alive = alive or tGNSS.isAlive() or tCAN.isAlive()
        mode,dire,depth= input()
        content = {'Who':'Gun','Mode':mode,'Dir':dire,'Depth':depth,'Forth':0}
        sendCmd(content)
        print(steerContent)
        pass
    pass
    print('ended')


if __name__ == "__main__":
    main(sys.argv[1:])

