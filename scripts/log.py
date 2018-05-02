''' /*************************************************
  Copyright (C), 2018.03.26, Tsinghua University & TianJian University.
  Author: GaoBin   Version 1.0    Data:2018.03.26
  File name:   log.py 
  Description:    record Gnss Nav and Actuator data based on zmq 
                  subscribe address and port need to be changed when publish changed 
  Function List:  //
    1. main
    2. logGNSS
    3. leogNavi
    4. logActuator
    5. ...
  History:        // 
    1. Date:2018.03.26
       Author:GaoBin
       Modification:build up the framework
    2. ...
**************************************************************/'''
import sys
import zmq
import time
import thread
sys.path.append("../libs")
from proContext import *

#subscribe address and port
#gps spd nav status
GnssAddr = 'tcp://127.0.0.1:8080'
NavAddr = 'tcp://127.0.0.1:8090'
SpeedSetAddr = 'tcp://127.0.0.1:8098'
#current actuator status
SteerAddr = 'tcp://127.0.0.1:8082'
GunAddr = 'tcp://127.0.0.1:8086'
BrakeAddr = 'tcp://127.0.0.1:8088'
#policy actuator status
PolicySteerAddr = 'tcp://127.0.0.1:8092'
PolicyGunAddr = 'tcp://127.0.0.1:8095'
PolicyBrakeAddr = 'tcp://127.0.0.1:8096'

gnssStatus = 0
gnssLat = 0
gnssLon = 0
gnssHead = 0
gnssRoll = 0
gnssPitch = 0
gnssV_n = 0
gnssV_e = 0
gnssV_earth = 0
gnssSpeed = 0
gnssA_n = 0
gnssA_e = 0
gnssA_earth = 0
setSpd = 0
naviSeg = 0
naviRoad = 0
naviDis = 0
naviHead = 0
naviDHead = 0
Steer = 0
GunDepth = 0
BrakeDepth = 0
PolicySteer = 0
PolicyGunDepth = 0
PolicyGunDir = 0
PolicyGunForth = 0
PolicyBrakeDepth = 0
PolicyBrakeDir = 0
PolicyBrakeForth = 0

#global contentSpd
#global contentNavi
#global contentSteer
#global contentGun
#global contentBrake
#global contentPoliSteer
#global contentPoliGun
#global contentPoliBrake

def main():
    def logGNSS():
        global gnssStatus
        global gnssLat 
        global gnssLon
        global gnssHead 
        global gnssRoll 
        global gnssPitch
        global gnssV_n 
        global gnssV_e 
        global gnssV_earth 
        global gnssSpeed 
        global gnssA_n 
        global gnssA_e
        global gnssA_earth

        sub = ctx.socket(zmq.SUB)
        sub.connect(GnssAddr)
        sub.setsockopt(zmq.SUBSCRIBE,'CurGNSS')
        contentGNSS = sub.recvPro()
        
        gnssStatus = contentGNSS['Status']
        gnssLat = contentGNSS['Lat']
        gnssLon = contentGNSS['Lon']
        gnssHead = contentGNSS['Head']
        gnssRoll = contentGNSS['Roll']
        gnssPitch = contentGNSS['Pitch']
        gnssV_n = contentGNSS['V_n']
        gnssV_e = contentGNSS['V_e']
        gnssV_earth = contentGNSS['V_earth']
        gnssSpeed = contentGNSS['Speed']
        gnssA_n = contentGNSS['A_n']
        gnssA_e = contentGNSS['A_e']
        gnssA_earth = contentGNSS['A_earth']
    
    def logSpd():
        global setSpd
        
        sub = ctx.socket(zmq.SUB)
        sub.connect(GnssAddr)
        sub.setsockopt(zmq.SUBSCRIBE,'SpeedSet')
        contentSpd = sub.recvPro()   

        setSpd = contentSpd

    def logNav():
        global naviSeg
        global naviRoad
        global naviDis
        global naviHead

        sub = ctx.socket(zmq.SUB)
        sub.connect(NavAddr)
        sub.setsockopt(zmq.SUBSCRIBE,'Road') 
        contentNavi = sub.recvPro()           

        naviSeg = contentNavi['SegID']
        naviRoad = contentNavi['RoadID']
        naviDis = contentNavi['Dis']
        naviHead = contentNavi['Head']
        naviDHead = contentNavi['DHead']
    
    def logSteer():
        global Steer

        subSteer = ctx.socket(zmq.SUB)
        subSteer.connect(SteerAddr)
        subSteer.setsockopt(zmq.SUBSCRIBE,'CANSteer')
        contentSteer = subSteer.recvPro()

        Steer = contentSteer['Angle']

    def logGun(): 
        global GunDepth

        subGun = ctx.socket(zmq.SUB)
        subGun.connect(GunAddr)
        subGun.setsockopt(zmq.SUBSCRIBE,'CANGun')
        contentGun = subGun.recvPro()

        GunDepth = contentGun['Depth']
    
    def logBrake():
        global BrakeDepth

        subBrake = ctx.socket(zmq.SUB)
        subBrake.connect(BrakeAddr)
        subBrake.setsockopt(zmq.SUBSCRIBE,'CANBrake')
        contentBrake = subBrake.recvPro()

        BrakeDepth = contentBrake['Depth']
    
    def logPoliSteer():
        global PolicySteer

        subPoliSteer = ctx.socket(zmq.SUB)
        subPoliSteer.connect(PolicySteerAddr)
        subPoliSteer.setsockopt(zmq.SUBSCRIBE,'PoliSteer')
        contentPoliSteer = subPoliSteer.recvPro()

        PolicySteer = contentPoliSteer['Value']
    
    def logPoliGun():
        global PolicyGunDepth
        global PolicyGunDir
        global PolicyGunForth
        
        subPoliGun = ctx.socket(zmq.SUB)
        subPoliGun.connect(PolicyGunAddr)
        subPoliGun.setsockopt(zmq.SUBSCRIBE,'PoliGun')
        contentPoliGun = subPoliGun.recvPro()

        PolicyGunDepth = contentPoliGun['Depth']
        PolicyGunDir  = contentPoliGun['Dir']
        PolicyGunForth = contentPoliGun['Forth']
    
    def logPoliBrake():
        global PolicyBrakeDepth
        global PolicyBrakeDir
        global PolicyBrakeForth
        
        subPoliBrake = ctx.socket(zmq.SUB)
        subPoliBrake.connect(PolicyBrakeAddr)
        subPoliBrake.setsockopt(zmq.SUBSCRIBE,'PoliBrake')
        contentPoliBrake = subPoliBrake.recvPro()

        PolicyBrakeDepth = contentPoliBrake['Depth']
        PolicyBrakeDir  = contentPoliBrake['Dir']
        PolicyBrakeForth = contentPoliBrake['Forth']

    thread.start_new_thread(logGNSS,())
    thread.start_new_thread(logSpd,())
    thread.start_new_thread(logNav,())
    thread.start_new_thread(logSteer,())    
    thread.start_new_thread(logGun,())    
    thread.start_new_thread(logBrake,())    
    thread.start_new_thread(logPoliSteer,())    
    thread.start_new_thread(logPoliGun,())    
    thread.start_new_thread(logPoliBrake,())    
   
    filename = time.strftime("../data/log/log_%Y_%m_%d_%H_%M.txt", time.localtime())
    f = open(filename, 'w')
    f.write('Time\t'+'Status\t'+'Lat\t'+'Lon\t'+'Head\t'+'Roll\t'+'Pitch\t'+'V_n\t'+'V_e\t'+'V_earth\t'+'Speed\t'+'setSpd\t'+'A_n\t'+'A_e\t'+'A_earth\t'+'SegID\t'+'RoadID\t'+'Dis\t'+'Head\t'+'dHead\t'+'Steer\t'+'PolicySteer\t'+'GunDepth\t'+'PolicyGunDepth\t'+'PolicyGunDir\t'+'PolicyGunForth\t'+'BrakeDepth\t'+'PolicyBrakeDepth\t'+'PolicyBrakeDir\t'+'PolicyBrakeForth\n')

    i = 0
    while True:
        i = (i + 1) % 999999
        time.sleep(0.1)
        ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        logdata = ctime + '\t' + \
        str(gnssStatus)  + '\t' + \
        str(gnssLat)  + '\t' + \
        str(gnssLon)  + '\t' + \
        str(gnssHead)  + '\t' + \
        str(gnssRoll)  + '\t' + \
        str(gnssPitch)  + '\t' + \
        str(gnssV_n)  + '\t' + \
        str(gnssV_e)  + '\t' + \
        str(gnssV_earth)  + '\t' + \
        str(gnssSpeed)  + '\t' + \
        str(setSpd)  + '\t' + \
        str(gnssA_n)  + '\t' + \
        str(gnssA_e)  + '\t' + \
        str(gnssA_earth)  + '\t' + \
        str(naviSeg)  + '\t' + \
        str(naviRoad)  + '\t' + \
        str(naviDis)  + '\t' + \
        str(naviHead) + '\t' + \
        str(naviDHead)  + '\t' + \
        str(Steer)  + '\t' + \
        str(PolicySteer)  + '\t' + \
        str(GunDepth)  + '\t' + \
        str(PolicyGunDepth)  + '\t' + \
        str(PolicyGunDir)  + '\t' + \
        str(PolicyGunForth)  + '\t' + \
        str(BrakeDepth)  + '\t' + \
        str(PolicyBrakeDepth)  + '\t' + \
        str(PolicyBrakeDir)  + '\t' + \
        str(PolicyBrakeForth)  + '\n'

        if i % 20 == 0:
            print logdata
        f.write(logdata)

if __name__=="__main__":
    ctx = proContext()
    main()
