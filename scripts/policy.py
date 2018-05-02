'''
/*************************************************
  Copyright (C), 2018.03.19, Tsinghua University & TianJian University.
  File name:   bottom.py 
  Description:    recv navigator message, for compute steer
                  recv GNSS for get speed back, for control, track speed
                  recv Gun and Brake, for control
                  recv lidar message, for change lane or stop
                  recv camera message, for traffic light
                  dicide where to go
                  steerControl
                  speedControl
                  compute steer, gun, brake
  Others:         // need to be changed when handware environment was different
  Function List:  //
    1. main
    2. recvNav
    3. recvLidar
    4. recvCamera
    5. ...
  History:        // 
    1. Date:2018.03.19
       Author:XueChong
       Modification:build this file
    2. Date:2018.03.21
       Author:XueChong
       Modification: add function
    3. Date:2018.03.22
       Author:XueChong
       Modification: new detail
    4. Date:2018.03.26
       Author:XueChong
       Modification: move tjuControl to ../libs/proControl
    5. Date:2018.03.28
       Author:XueChong
       Modification: add lux4 policy
    6. ...
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
from proControl import *
from proLux4 import *
import UTM


#define variables
#if Ctrl-C are pressed, default is False
is_exit = False

# address and port for publish messages
GnssAddr = 'tcp://127.0.0.1:8080'
SteerAddr = 'tcp://127.0.0.1:8082'
GunAddr = 'tcp://127.0.0.1:8086'
BrakeAddr = 'tcp://127.0.0.1:8088'

# address and port for subcribe messages from Policy or monitor
PolicySteerAddr = 'tcp://127.0.0.1:8092'
PolicyGunAddr = 'tcp://127.0.0.1:8095'
PolicyBrakeAddr = 'tcp://127.0.0.1:8096'

# address and port for subcribe lux4 messages from tx1_3
Lux41addr = 'tcp://192.168.1.103:9060'
Lux42addr = 'tcp://192.168.1.103:9062'
Lux43addr = 'tcp://192.168.1.103:9063'
Lux44addr = 'tcp://192.168.1.103:9065'
Lux45addr = 'tcp://192.168.1.103:9066'
Lux46addr = 'tcp://192.168.1.103:9068'

# get speed set
SpeedSetAddr = 'tcp://127.0.0.1:8098'

NavAddr = 'tcp://127.0.0.1:8090'

#all control mode
speedMode = 1
steerMode = 0x20
abGun = 0
abBrake = 0

speedBack = 0
speedSet = 0
gear = 2
brakeDepth = 60
gunDepth = 0
#nav variables
#sometimes need offset the road, when change lane
node = {"SegID":0,"Left":0,"Right":0,"Speed":0,"Width":0,"Dis":0,"Head":0,"DHead":0}
SegID = 0
offset = 0

#lidar variables
lux4objs = Lux4Objs()
changeLane = False
stopLidar = False

aheadStartTime = 0
aheadEndTime = 0
isAhead = False
isSmall = False
isPeople = False
isBig = False
isBike = False
isCar = False
isTruck = False
speedLux4 = 10

# zmq tools
ctx = proContext()

#camera variables
activeCamera = False
stopCamera = False


def handler(signum, frame):
    global is_exit
    is_exit = True
    print "receive a signal %d, is_exit = %d"%(signum, is_exit)


#define main functions
def main(args):
    global speedMode
    global steerMode
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    # modify mode of self-driving
    if len(args) > 0:
        if args[0] is not 0:
            steerMode = 0x20
        else:
            steerMode = 0x10
    if len(args) > 1:
        if args[1] is not 0:
            speedMode = 1
        else:
            speedMode = 0

    # a list including all threads
    threads = []

    # defination of all the threads
    tRecvGNSS = threading.Thread(target = recvGNSS, args = ())
    #
    tRecvNav = threading.Thread(target = recvNav, args = ())

    tRecvGun = threading.Thread(target = recvGun, args = ())

    tRecvBrake = threading.Thread(target = recvBrake, args = ())

    tSteerControl = threading.Thread(target = steerControl, args = ())

    tSpeedControl = threading.Thread(target = speedControl, args = ())

    tGetSpeed = threading.Thread(target = getSpeedSet, args = ())

    tGetLux1 = threading.Thread(target = recvLux41, args = ())
    tGetLux2 = threading.Thread(target = recvLux42, args = ())
    tGetLux3 = threading.Thread(target = recvLux43, args = ())
    tGetLux4 = threading.Thread(target = recvLux44, args = ())
    tGetLux5 = threading.Thread(target = recvLux45, args = ())
    tGetLux6 = threading.Thread(target = recvLux46, args = ())

    tRecvGNSS.setDaemon(True)
    tRecvNav.setDaemon(True)
    tRecvGun.setDaemon(True)
    tRecvBrake.setDaemon(True)
    tSteerControl.setDaemon(True)
    tSpeedControl.setDaemon(True)
    tGetSpeed.setDaemon(True)
    tGetLux1.setDaemon(True)
    tGetLux2.setDaemon(True)
    tGetLux3.setDaemon(True)
    tGetLux4.setDaemon(True)
    tGetLux5.setDaemon(True)
    tGetLux6.setDaemon(True)

    tRecvGNSS.start()
    time.sleep(0.1)
    tRecvNav.start()
    time.sleep(0.1)
    tRecvGun.start()
    time.sleep(0.1)
    tRecvBrake.start()
    time.sleep(0.1)
    # steer control
    tSteerControl.start()
    time.sleep(0.1)
    tGetSpeed.start()
    time.sleep(0.1)
    tSpeedControl.start()
    tGetLux1.start()
    tGetLux2.start()
    tGetLux3.start()
    tGetLux4.start()
    tGetLux5.start()
    tGetLux6.start()

    # start all threads
    #for t in threads:
    #    t.start()

    prGreen('all threads started ......')

    alive = True
    while not is_exit:
        time.sleep(0.5)
        #alive = False
        #for t in threads:
        #    alive = alive or t.isAlive()
        pass
    pass

    prRed('all threads were ended by Ctrl-C')
    time.sleep(1)

    off()

# sholw title
def showAbstract():
    pass
# load IP
def loadIP():
    pass

steer = 0
def steerControl():
    global steer
    global SegID
    global offset
    global changeLane
    changing = True
    pub= ctx.socket(zmq.PUB)
    pub.bind(PolicySteerAddr)

    i = 0
    switch = 1
    #by nva
    while not is_exit:
        time.sleep(0.1)
        i = (i+1) % 99999
        if node['SegID'] != SegID:
            SegID = node['SegID']
            changeLane = False
            offset = 0
        if changeLane:
            #if node['Left'] == 1:
            #    offset = -1 * node['Width']
            #elif node['Right'] == 1:
            #    offset = node['Width']
            if offset == -3.5:
                if math.fabs(node['Dis']) < 1.8:
                    steer = int( ( 11.8 * (node['Dis'] + offset ) + 4.0 * (node['Head'] -  10 * math.log( 1 + 2.5 * (1.8 - node['Dis']) ) )    + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                    print(steer)
                elif math.fabs(node['Dis']) > 1.8 and math.fabs(node['Dis']) < 2.8:
                    steer = int( ( 11.8 * (node['Dis'] + offset ) + 4.0 * (node['Head'] + 12 * math.log(  1 + 2 * ( 3.6 - node['Dis']) ) )    + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                    print(steer)
                else:
                    steer = int( ( 11.8 * (node['Dis'] + offset ) + 4.0 * node['Head'] + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                pass
            elif offset == 3.5:
                if math.fabs(node['Dis']) < 3.5 - 1.8:
                    steer = int( ( 11.8 * (node['Dis'] + offset ) + 4.0 * (node['Head'] +  6 * math.log( 2.5 * (3.5 + node['Dis']) ) )    + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                else:
                    steer = int( ( 11.8 * (node['Dis'] + offset ) + 4.0 * node['Head'] + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                pass
            elif offset == -0.01:
                if math.fabs(node['Dis']) > 1.8:
                    steer = int( ( 11.8 * (node['Dis'] ) + 4.0 * (node['Head'] +   6 * math.log( 2.5 * (node['Dis']) ) )    + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                else:
                    steer = int( ( 11.8 * (node['Dis'] ) + 4.0 * node['Head'] + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                pass
            elif offset == 0.01:
                if math.fabs(node['Dis']) > 1.8:
                    steer = int( ( 11.8 * (node['Dis'] ) + 4.0 * (node['Head'] -  6 * math.log( 2.5 * (node['Dis']) ) )    + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                else:
                    steer = int( ( 11.8 * (node['Dis'] ) + 4.0 * node['Head'] + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
                pass
                pass
        #if node['Dis'] > 0.9 and speedBack < 10:
        #    steer =  ( 10.8 * (1 + node['Dis']) * (node['Dis'] + offset ) + 4.1 / (1 + node['Dis']) * node['Head'] + 4.8 * node['DHead'] ) * 0.6 + steer * 0.4
        #else:
        else:
            steer = int( ( 11.8 * (node['Dis'] + offset ) + 4.0 * node['Head'] + 4.0 * node['DHead'] ) * 0.6 + steer * 0.4)
        if node['SegID'] == 49:
            steer = -520
        content = {'Who':'Steer','Mode':steerMode,'Value':steer}
        if(i % 10 == 0):
            if math.fabs(steer) < 10:
                prGreen("steer is : " + str(steer))
            elif math.fabs(steer) < 20:
                prBlue("steer is : " + str(steer))
            elif math.fabs(steer) < 40:
                prYellow("steer is : " + str(steer))
            else:
                prRed("steer is : " + str(steer))
        content = {'Who':'Steer','Mode':steerMode,'Value':steer - 28 - switch}
        switch = 1 - switch
        pub.sendPro('PoliSteer',content)
    content = {'Who':'Steer','Mode':0x10,'Value':0}
    pub.sendPro('PoliSteer',content)
    pass

def getSpeedSet():
    global ctx 
    global speedSet
    global gear
    sub = ctx.socket(zmq.SUB)
    sub.connect(SpeedSetAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'SpeedSet')
    while not is_exit:
        #speed,gear = sub.recvPro()
        speed = sub.recvPro()
        prRed(speed)
        speedSet = int(speed)
        #gear = int(gear)
    pass

def lux4Speed():
    global speedLux4
    global isAhead
    global aheadStartTime
    global aheadEndTime
    global isSmall
    global offset

    global changeLane

    for i,obj in enumerate(lux4objs.small +  lux4objs.big + lux4objs.pedestrian + lux4objs.bike + lux4objs.car + lux4objs.truck):
        if obj.dis < 16 and ( (obj.left > -2 and obj.left < 2) or (obj.right < 2 and obj.right > -2) or (obj.left< -2 and obj.right > 2) ) :
            changeLane = True
            speedLux4 = 5
            isAhead = True
            isSmall = True
            aheadStartTime = int(time.time())
            offset = -3.5
            print('change lane')
            
            return speedLux4
        if obj.dis < 30 and ( (obj.left > -2 and obj.left < 2) or (obj.right < 2 and obj.right > -2) or (obj.left < -2 and obj.right > 2)  ) :
            speedLux4 = 8
            isAhead = True
            isSmall = True
            obj.disStartTime = int(time.time())
            return speedLux4
        pass

    isSmall = False
    aheadEndTime = int(time.time())
    if aheadEndTime - aheadStartTime > 30:
        offset = -0.1

    if aheadEndTime - aheadStartTime > 60 and math.fabs(node['Dis']) < 0.8:
        speedLux4 = speedSet
        changeLane = False

    return speedLux4
    pass

def speedControl():
    
    global brakeDepth
    global gunDepth
    global gear
    global speedSet
    gunDir = 3
    brakeDir = 1
    pubGun = ctx.socket(zmq.PUB)
    pubGun.bind(PolicyGunAddr)

    pubBrake = ctx.socket(zmq.PUB)
    pubBrake.bind(PolicyBrakeAddr)

    control = Control()
    isBraked = False
    i = 0
    while not is_exit:
        time.sleep(0.1)
        #speedSet = node['Speed']
        # get result from controller
        speedset = min(speedSet,lux4Speed())
        #speedset = speedSet
        if math.fabs(speedset - speedBack) > 20:
            gear = 3
        elif math.fabs(speedset - speedBack) > 10:
            gear = 2
        elif math.fabs(speedset - speedBack) > 5:
            gear = 1
        gunDir,gunDepth,brakeDir,brakeDepth = control.control(speedset ,speedBack , abGun, abBrake, gear)

        if i % 15 ==0:
            prGreen("speedSet is : " + str(speedSet) )
            prPink("speedBack is : " + str(speedBack) )
            prRed("speedLux4 is : " + str(speedLux4))

            for index,obj in enumerate(lux4objs.small):
                if ((obj.left > -6 and obj.right < 6) or ( obj.right > -6 and obj.right < 6  )) and (obj.dis < 30):
                    show = "small obj message\n\t ==>\tleft: " + str(obj.left) + "\tright: "  + str(obj.right) + "\tdis: " + str(obj.dis) + "\twidth: " + str(obj.width)
                    prYellow(show);
            for index,obj in enumerate(lux4objs.big):
                if ((obj.left > -6 and obj.right < 6) or ( obj.right > -6 and obj.right < 6  )) and (obj.dis < 30):
                     show = "big obj message\n\t ==>\tleft: " + str(obj.left) + "\tright: "+ str(obj.right) + "\tdis: " + str(obj.dis) + "\twidth: " + str(obj.width)
                     prYellow(show);
            for index,obj in enumerate(lux4objs.pedestrian):
                if ((obj.left > -6 and obj.right < 6) or ( obj.right > -6 and obj.right < 6  )) and (obj.dis < 30):
                    show = "pedestrian obj message\n\t ==>\tleft: " + str(obj.left) + "\tright: " + str(obj.right) + "\tdis: " + str(obj.dis) + "\twidth: " + str(obj.width)
                    prYellow(show);
            for index,obj in enumerate(lux4objs.bike):
                if ((obj.left > -6 and obj.right < 6) or ( obj.right > -6 and obj.right < 6  )) and (obj.dis < 30):
                    show = "bike obj message\n\t ==>\tleft: " + str(obj.left) + "\tright: "+ str(obj.right) + "\tdis: "+ str(obj.dis) + "\twidth: " + str(obj.width)
                    prYellow(show);
            for index,obj in enumerate(lux4objs.car):
                if ((obj.left > -6 and obj.right < 6) or ( obj.right > -6 and obj.right < 6 ) ) and (obj.dis < 30):
                    show = "car obj message\n\t ==>\tleft: " + str(obj.left) + "\tright: " + str(obj.right) + "\tdis: " + str(obj.dis) + "\twidth: " + str(obj.width)
                    prYellow(show);
            for index,obj in enumerate(lux4objs.truck):
                if ((obj.left > -6 and obj.right < 6) or ( obj.right > -6 and obj.right < 6  )) and (obj.dis < 30):
                    show = "truck obj message\n\t ==>\tleft: " + str(obj.left) + "\tright: " + str(obj.right) + "\tdis: " + str(obj.dis) + "\twidth: "+ str(obj.width)
                    prYellow(show);

            print('\n')
        i = (i + 1) % 9999

        if isBraked:
            content = {'Who':'Gun','Mode':speedMode,'Dir':3,'Depth':gunDepth,'Forth':0}
            pubGun.sendPro('PoliGun',content)

        if isBraked and brakeDir == 1 and abBrake >= 660 and speedset == 0:
            continue
            pass
            # control brake

        if isBraked and brakeDir == 1 and abBrake >= 660:
            continue
            pass
            # control brake

        if brakeDir == 1:
            content = {'Who':'Gun','Mode':1,'Dir':3,'Depth':50,'Forth':0}
            pubGun.sendPro('PoliGun',content)
            content = {'Who':'Brake','Mode':1,'Dir':1,'Depth':50,'Forth':brakeDepth}
            pubBrake.sendPro('PoliBrake',content)
            #prBlue("brakeDir is : " + str(brakeDir))
            #prCyan("brakeDepth is : " + str(brakeDepth))
            isBraked = True
            time.sleep(0.5)

        else:
            content = {'Who':'Brake','Mode':speedMode,'Dir':brakeDir,'Depth':50,'Forth':brakeDepth}
            pubBrake.sendPro('PoliBrake',content)
            isBraked = False
            # control gun
            content = {'Who':'Gun','Mode':speedMode,'Dir':gunDir,'Depth':gunDepth,'Forth':0}
            pubGun.sendPro('PoliGun',content)
        pass
    content = {'Who':'Gun','Mode':0,'Dir':0,'Depth':0,'Forth':0}
    pubGun.sendPro('PoliGun',content)
    content = {'Who':'Brake','Mode':0,'Dir':0,'Depth':0,'Forth':0}
    pubBrake.sendPro('PoliBrake',content)
    pass


def recvGun():
    global ctx 
    global node
    global abGun
    sub = ctx.socket(zmq.SUB)
    sub.connect(GunAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'CANGun')

    prGreen('thread recvGun started')
    while not is_exit:
        content = sub.recvPro()
        abGun = content['Depth']
        pass
    print('thread recvGNSS ended by Ctrl-C')
    pass

def recvBrake():
    global ctx 
    global node
    global abBrake
    sub = ctx.socket(zmq.SUB)
    sub.connect(BrakeAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'CANBrake')

    prGreen('thread recvBrake started')
    while not is_exit:
        content = sub.recvPro()
        abBrake = content['Depth']
        pass
    print('thread recvGNSS ended by Ctrl-C')
    pass

#define recv policy command
def recvGNSS():
    global ctx
    global speedBack
    sub = ctx.socket(zmq.SUB)
    sub.connect(GnssAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'CurGNSS')

    prGreen('thread recvGNSS started')
    while not is_exit:
        content = sub.recvPro()
        speedBack = int( content['Speed'] * 3.6)
        pass
    print('thread recvGNSS ended by Ctrl-C')
    pass

def recvNav():
    global ctx
    global node
    sub = ctx.socket(zmq.SUB)
    sub.connect(NavAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'Road')

    prGreen('thread recvNav started')
    while not is_exit:
        content = sub.recvPro()
        node = content
    print('thread recvGNSS ended by Ctrl-C')
    pass

def recvLux41():
    global lux4objs
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(Lux41addr)
    sub.setsockopt(zmq.SUBSCRIBE,'lux1')
    while not is_exit:
        content = sub.recv()
        lux4objs.getSmall(content)
        pass
    pass

def recvLux42():
    global lux4objs
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(Lux42addr)
    sub.setsockopt(zmq.SUBSCRIBE,'lux2')
    while not is_exit:
        content = sub.recv()
        lux4objs.getBig(content)
        pass
    pass

def recvLux43():
    global lux4objs
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(Lux43addr)
    sub.setsockopt(zmq.SUBSCRIBE,'lux3')
    while not is_exit:
        content = sub.recv()
        lux4objs.getPedestrian(content)
        pass
    pass

def recvLux44():
    global lux4objs
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(Lux44addr)
    sub.setsockopt(zmq.SUBSCRIBE,'lux4')
    while not is_exit:
        content = sub.recv()
        lux4objs.getBike(content)
        pass
    pass

def recvLux45():
    global lux4objs
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(Lux45addr)
    sub.setsockopt(zmq.SUBSCRIBE,'lux5')
    while not is_exit:
        content = sub.recv()
        lux4objs.getCar(content)
        pass
    pass

def recvLux46():
    global lux4objs
    global ctx
    sub = ctx.socket(zmq.SUB)
    sub.connect(Lux46addr)
    sub.setsockopt(zmq.SUBSCRIBE,'lux6')
    while not is_exit:
        content = sub.recv()
        lux4objs.getTruck(content)
        pass
    pass

def off():
    steerControl()
    speedControl()
    pass

if __name__ == "__main__":
    #args list
    #args one mapname, default is '../data/map/tju.map'
    main(sys.argv[1:])

