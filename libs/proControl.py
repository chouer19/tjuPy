'''
/*************************************************
  Copyright (C), 2018.03.21, Tsinghua University & TianJian University.
  File name:   bottom.py 
  Description:    a defination of speed control
                  called by policy's speed control on-time
                  give an ultimate gun value and brake value given current gun value, current speed, expected speed, gear
  Others:         // need to be changed when handware environment was different
  Function List:  //
    1. init
    2. control
    3. ...
  History:        // 
    1. Date:2018.03.21
       Author:XueChong
       Modification:build this file
    2. Date:2018.03.22
       Author:XueChong
       Modification: add function
    3. Date:2018.03.23
       Author:XueChong
       Modification: new detail
    4. Date:2018.03.25
       Author:XueChong
       Modification: 
                     run on Driving-Brain, change parameters, test brake
    5. Date:2018.03.28
       Author:XueChong
       Modification: move tjuControl to ../libs/proControl
    6. ...
*************************************************/
'''

import sys
import time
import thread
from proPID import *

class Control:
    def __init__(self):

        #speed 0 ~ 10
        self.pid1 = PID(P=26.6, I = 10.6, D = 0.0)

        #speed 11 ~ 19
        self.pid2 = PID(P=18.6, I = 8.6, D = 0.0)

        #speed 20 ~ 28
        self.pid3 = PID(P=16.6, I = 7.6, D = 0.6)

        #speed 29 ~ 36
        self.pid4 = PID(P= 16.6 , I =6.0, D = 10.0)

        pass

    def control(self,speed_set,speed_back,abGun,abBrake,gear):
        gunDir = 2
        brakeDir = 3
        gear = max(1,min(gear,5))
        gunDepth = 0
        gunDir = 2
        if speed_set <=0 :
            return 3,0,1,30 * gear + 30
        if speed_back - speed_set > 3.5:
            return 3,0,1,20 * gear
        pass

        if speed_set > 36:
            speed_set = 36
        self.pid1.SetPoint = speed_set
        self.pid1.update(speed_back)
        self.pid2.SetPoint = speed_set
        self.pid2.update(speed_back)
        self.pid3.SetPoint = speed_set
        self.pid3.update(speed_back)
        self.pid4.SetPoint = speed_set
        self.pid4.update(speed_back)
        #different args for different speed_set
        if speed_set <= 10:
            output  = self.pid1.output
        elif speed_set <= 19:
            output  = self.pid2.output
        elif speed_set <= 28:
            output  = self.pid3.output
        elif speed_set <= 36:
            output = self.pid4.output

        output = int(output)

        Depth = 460 + output - abGun + 100
        
        if Depth < -90 and abBrake < 650:
            pass
        elif Depth < -90 :
            gunDir = 2
            gunDepth = int ( Depth * -0.5 )
            pass
        elif Depth > 15 and speed_set > 20:
            gunDir = 1
            gunDepth = Depth + (gear - 0) * 5
        elif Depth > 10 and speed_set <= 20:
            gunDir = 1
            gunDepth = Depth + (gear - 0) * 3
        elif Depth < -60:
            gunDir = 2
            gunDepth = int ( Depth * -0.5 )
        else:
            gunDir = 2
            gunDepth = 0

        return gunDir,gunDepth,3,0
