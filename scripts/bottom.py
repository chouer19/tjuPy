''' /*************************************************
  Copyright (C), 2018.03.19, Tsinghua University & TianJian University.
  Author: XueChong   Version 1.0    Data:2018.03.19
  File name:   bottom.py 
  Description:    load and read all devices that interact with the driving-brain with CAN or serial port, and
                  send ultimate CAN command to control the car's behavoir
  Others:         // need to be changed when handware environment was different
  Function List:  //
    1. main
    2. readGNSS
    3. readCAN
    4. sendCMD
    5. close all self-driving...
    6. ...
  History:        // 
    1. Date:2018.03.19
       Author:XueChong
       Modification:build up the framework
    2. Date:2018.03.21
       Author:XueChong
       Modification: add more detailed notation and check
                     last steer compare to now steer
    3. Date:2018.03.22
       Author:XueChong
       Modification: run on Dring-brain, isAlive() will result on exception of "*** Stack Smashing Detected ** python terminated"
    4. Date:2018.03.22
       Author:XueChong
       Modification: running on Driving-brain
                     add time.sleep() in the main while not is_exit loop
    5. Data:2018.03.24
       Author:XueChong
       Modification: running on Driving-brain
                     "*** Stack Smashing Detected *** python terminated" back to 23

*************************************************/
'''

#import packages

import sys
import time
import math
import threading
import signal
# some packages' dir
sys.path.append("../libs")
from proContext import *
from proMCU import *
from proPrint import *
import UTM


#define variables
#if Ctrl-C are pressed, default is False
is_exit = False

# what content to display ,default is all(1111)
# gnss only 0001
# steer only 0010
# brake only 0100
# gun only 1000
display = 1111

# read all by this
mcu = MCU()

# zmq tools
ctx = proContext()

# address and port for publish messages
GnssAddr = 'tcp://127.0.0.1:8080'
SteerAddr = 'tcp://127.0.0.1:8082'
GunAddr = 'tcp://127.0.0.1:8086'
BrakeAddr = 'tcp://127.0.0.1:8088'

# address and port for subcribe messages from Policy or monitor
PolicySteerAddr = 'tcp://127.0.0.1:8092'
PolicyGunAddr = 'tcp://127.0.0.1:8095'
PolicyBrakeAddr = 'tcp://127.0.0.1:8096'

#speed and steer for steer limitation
speed = 0
steer = 0

#signal, exit when Ctrl-C
def handler(signum, frame):
    global is_exit
    is_exit = True
    print "receive a signal %d, is_exit = %d"%(signum, is_exit)


#define main functions
def main(args):
    global display
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)


    if len(args) > 0:
        display = int(args[0])

    # a list including all threads
    #threads = []

    # defination of all the threads
    # reading MAP Time IMU
    tGNSS = threading.Thread(target = readGNSS, args = ())
    #threads.append(tGNSS)

    # read steer, brake, gun from CAN
    tCAN = threading.Thread(target = readCAN, args = ())
    #threads.append(tCAN)

    # recv steer cmd from policy
    tSteer = threading.Thread(target = recvSteer, args = ())
    #threads.append(tSteer)

    # recv gun cmd from policy
    tGun = threading.Thread(target = recvGun, args = ())
    #threads.append(tGun)

    # recv brake cmd from policy
    tBrake = threading.Thread(target = recvBrake, args = ())
    #threads.append(tBrake)

    # can be stoped with Ctrl-C
    tGNSS.setDaemon(True)
    tCAN.setDaemon(True)
    tSteer.setDaemon(True)
    tGun.setDaemon(True)
    tBrake.setDaemon(True)

    tGNSS.start()
    tCAN.start()
    tSteer.start()
    tGun.start()
    tBrake.start()
    # start all threads
    #for t in threads:
    #    t.start()

    prGreen('all threads started ......')
    
    # if any thread is alive, go on
    while not is_exit:
        time.sleep(0.5)
        pass
    pass

    prRed('all threads were ended by Ctrl-C')

    # close all self-driving, then hand over to human
    offALL()

# sholw title
def showAbstract():
    pass
# load IP
def loadIP():
    pass

#define recv gnss
def readGNSS():
    #should there be a pre-processing code block?
    global mcu
    global ctx
    global speed
    # for publish gnss message
    pub= ctx.socket(zmq.PUB)
    pub.bind(GnssAddr)
    
    prGreen('start reading IMU ................')

    i = 0
    while not is_exit:
        i = (i + 1) % 9999
        time.sleep(0.05)
        mcu.readGNSS()
        speed = math.sqrt (mcu.gnssRead.v_n ** 2 + mcu.gnssRead.v_e ** 2 + mcu.gnssRead.v_earth ** 2 )
        #pub all imu message
        content = {"Length":mcu.gnssRead.length,"Mode":mcu.gnssRead.mode,"Time1":mcu.gnssRead.time1,"Time2":mcu.gnssRead.time2, \
                   "Num":mcu.gnssRead.num,"Lat":mcu.gnssRead.lat,"Lon":mcu.gnssRead.lon,"Height":mcu.gnssRead.height, \
                   "V_n":mcu.gnssRead.v_n,"V_e":mcu.gnssRead.v_e,"V_earth":mcu.gnssRead.v_earth, \
                   "Roll":mcu.gnssRead.roll,"Pitch":mcu.gnssRead.pitch,"Head":mcu.gnssRead.head, \
                   "A_n":mcu.gnssRead.a_n,"A_e":mcu.gnssRead.a_e,"A_earth":mcu.gnssRead.a_earth, \
                   "V_roll":mcu.gnssRead.v_roll,"V_pitch":mcu.gnssRead.v_pitch,"V_head":mcu.gnssRead.v_head, \
                   "Status":mcu.gnssRead.status,"Speed":speed}
        pub.sendPro("CurGNSS",content)
        if content['Head'] > 360:
            content['Head'] = content['Head'] - 360
        if i%20 == 0 and display % 10 >= 1:
            show = "GNSS message => \n\tStatus: "+ str(content['Status']) + "\t" + "Lat: "+ str(content['Lat']) + "\t" + "Lon: "+ str(content['Lon']) + "\t" + "Head: "+ str(content['Head']) + "\tSpeed: "+ str(content['Speed'])
            if content['Status'] == 2:
                prGreen(show)
            elif content['Status'] == 1:
                prYellow(show)
            else:
                prRed(show)

    print('GNSS thread ended by Ctrl-C')
    pass


#define recv CAN
def readCAN():
    global mcu
    global ctx
    global steer

    # publish steer message
    pubSteer = ctx.socket(zmq.PUB)
    pubSteer.bind(SteerAddr)

    # publish brake message
    pubBrake = ctx.socket(zmq.PUB)
    pubBrake.bind(BrakeAddr)

    # publish gun message
    pubGun = ctx.socket(zmq.PUB)
    pubGun.bind(GunAddr)

    prGreen('start reading CAN................')

    select = 1
    i = 0
    while not is_exit:
        time.sleep(0.02)
        i = i + 1
        if select == 1:
            select = 2
            mcu.readSteer()
            steer = mcu.steerRead.AngleH * 256 + mcu.steerRead.AngleL - 1024
            content = {'Mode':mcu.steerRead.Mode, \
                       'Angle':steer}
            pubSteer.sendPro("CANSteer",content)
            if i%50 == 0 and display % 100 >= 10:
                show = "Steer message => \n"
                prCyan(show)
                prCyan('\t'+str(content) )
            continue

        if select == 2:
            select = 3
            mcu.readGun()
            content = {'Mode':mcu.gunRead.Mode, 'Temper':mcu.gunRead.Temper, 'Button': mcu.gunRead.Button, 'BrakeLight':mcu.gunRead.BrakeLight,\
                       'BrakePadel': mcu.gunRead.BrakePadel, 'Depth':mcu.gunRead.Depth}
            pubGun.sendPro("CANGun",content)
            if i%50 == 0 and display % 1000 >= 100:
                show = "Gun message => \n\tMode: " + str(content['Mode']) + "\tDepth: " + str(content['Depth'])
                prBlue(show)
            continue

        if select == 3:
            select = 1
            mcu.readBrake()
            content = {'Mode':mcu.brakeRead.Mode, 'Temper':mcu.brakeRead.Temper, 'Estop': mcu.brakeRead.Estop, 'Depth':mcu.brakeRead.Depth}
            pubBrake.sendPro("CANBrake",content)
            if i%10 == 0 and display % 10000 >= 1000:
                show = "Brake message => \n\tMode: " + str(content['Mode']) + "\tDepth: " + str(content['Depth'])
                prBlue(show)
            continue
    print('CAN thread ended by Ctrl-C')
    pass


#define recv policy command
# steer limit and config
# recv steer from policy
def recvSteer():
    steer_limit = []
    # load steer limitation first
    def loadSteerConfig():
        with open('../data/config/steerLimit.cfg') as f:
            for line in f.readlines():
                steer_limit.append(int(line))
    loadSteerConfig()
    
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(PolicySteerAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'PoliSteer')
    i = 0
    while not is_exit:
        i = (i+1) % 9999
        content = sub.recvPro()
        if i% 50 ==0:
            prPink(content)
        if speed > 0:
            gap = 0
            if (speed * 3.6 < len(steer_limit)):
                gap = steer_limit[int(speed * 3.6)]
            if content['Value'] - steer > gap:
                content['Value'] = steer + gap
            elif content['Value'] - steer < -1 * gap:
                content['Value'] = steer - gap
        content['Value'] = min(520, max(content['Value'], -520))
        sendCMD(content)
        pass
    content = {'Who':'Steer','Mode':0x10,'Value':0x00}
    sendCMD(content)
    print('thread recvSteer ended by Ctrl-C')
    pass

# recv gun from policy
def recvGun():
    global ctx
    #subcribe
    sub = ctx.socket(zmq.SUB)
    sub.connect(PolicyGunAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'PoliGun')
    while not is_exit:
        content = sub.recvPro()
        sendCMD(content)
    content = {'Who':'Gun','Mode':0,'Dir':0,'Depth':0,'Forth':0}
    sendCMD(content)
    print('thread recvGun ended by Ctrl-C')
    pass

# recv brake from policy
def recvBrake():
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(PolicyBrakeAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'PoliBrake')
    while not is_exit:
        content = sub.recvPro()
        sendCMD(content)
    content = {'Who':'Brake','Mode':0,'Dir':0,'Depth':0,'Forth':0}
    sendCMD(content)
    print('thread recvSteer ended by Ctrl-C')
    pass


#define send command to car CAN
#there should be a pre-cessing code block
def sendCMD(content):
    global mcu
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
        mcu.steerSend.Mode = content['Mode']
        mcu.steerSend.AngleH =  int( (steer + 1024)/256)
        mcu.steerSend.AngleL =  int ( (steer + 1024) % 256)
        mcu.sendSteer()
        pass
    pass


# when Ctrl-C are pressed, all control should be handled over to human driver naming close self-driving
def offALL():
    #close steer
    content = {'Who':'Steer','Mode':0x10,'Value':0x00}
    sendCMD(content)
    #close gun
    content = {'Who':'Gun','Mode':0,'Dir':0,'Depth':0,'Forth':0}
    sendCMD(content)
    #close brake
    content = {'Who':'Brake','Mode':0,'Dir':0,'Depth':0,'Forth':0}
    sendCMD(content)
    pass


#with args
if __name__ == "__main__":
    main(sys.argv[1:])
