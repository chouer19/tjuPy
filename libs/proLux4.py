'''
/*************************************************
  Copyright (C), 2018.03.28, Tsinghua University & TianJian University.
  File name:   bottom.py 
  Description:    a defination of Lux4 objects
  Others:         // need to be changed when handware environment was different
  Function List:  //
    1. init
    2. ...
    3. ......
  History:        // 
    1. Date:2018.03.28
       Author:XueChong
       Modification:build this file
    2. ...
*************************************************/
'''

import sys
import time
import thread

class Lux4Obj:
    def __init__(self, x1=0, y1=0, x2=0, y2=0, x3=0, y3=0, x4=0, y4=0):
        self.x1 = x1 / 100
        self.y1 = y1 / 100
        self.x2 = x2 / 100
        self.y2 = y2 / 100
        self.x3 = x3 / 100
        self.y3 = y3 / 100
        self.x4 = x4 / 100
        self.y4 = y4 / 100
        self.left = max(self.y1, self.y2, self.y3, self.y4) * -1
        self.right = min(self.y1, self.y2, self.y3, self.y4) * -1
        self.dis= min(self.x1,self.x2,self.x3,self.x4)
        self.width = self.right - self.left
        pass

class Lux4Objs:
    def __init__(self):

        #
        self.small = []

        #
        self.big = []

        #
        self.pedestrian = []

        #
        self.bike = []

        #
        self.car = []

        #
        self.truck = []
        pass

    def getSmall(self,string):
        self.small = []
        
        contents = string.split(' ')[1:-1]
        for content in contents:
            cord = content.split(',')
            obj = Lux4Obj( float(cord[0]), float(cord[1]),  float(cord[2]),  float(cord[3]),  float(cord[4]),  float(cord[5]),  float(cord[6]),  float(cord[7]) )
            self.small.append(obj)
            pass
        pass


    def getBig(self,string):
        self.big = []
        
        contents = string.split(' ')[1:-1]
        for content in contents:
            cord = content.split(',')
            obj = Lux4Obj( float(cord[0]), float(cord[1]),  float(cord[2]),  float(cord[3]),  float(cord[4]),  float(cord[5]),  float(cord[6]),  float(cord[7]) )
            self.big.append(obj)
        pass

    def getPedestrian(self,string):
        self.pedestrian = []
        
        contents = string.split(' ')[1:-1]
        for content in contents:
            cord = content.split(',')
            obj = Lux4Obj( float(cord[0]), float(cord[1]),  float(cord[2]),  float(cord[3]),  float(cord[4]),  float(cord[5]),  float(cord[6]),  float(cord[7]) )
            self.pedestrian.append(obj)
        pass

    def getBike(self,string):
        self.bike = []
        
        contents = string.split(' ')[1:-1]
        for content in contents:
            cord = content.split(',')
            obj = Lux4Obj( float(cord[0]), float(cord[1]),  float(cord[2]),  float(cord[3]),  float(cord[4]),  float(cord[5]),  float(cord[6]),  float(cord[7]) )
            self.bike.append(obj)
        pass

    def getCar(self,string):
        self.car = []
        
        contents = string.split(' ')[1:-1]
        for content in contents:
            cord = content.split(',')
            obj = Lux4Obj( float(cord[0]), float(cord[1]),  float(cord[2]),  float(cord[3]),  float(cord[4]),  float(cord[5]),  float(cord[6]),  float(cord[7]) )
            self.car.append(obj)
        pass

    def getTruck(self,string):
        self.small = []
        
        contents = string.split(' ')[1:-1]
        for content in contents:
            cord = content.split(',')
            obj = Lux4Obj( float(cord[0]), float(cord[1]),  float(cord[2]),  float(cord[3]),  float(cord[4]),  float(cord[5]),  float(cord[6]),  float(cord[7]) )
            self.truck.append(obj)
        pass

