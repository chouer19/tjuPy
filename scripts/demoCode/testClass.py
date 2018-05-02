'''
/*************************************************
  Copyright (C), 2018.03.19, Tsinghua University & TianJian University.
  File name:   nav.py 
  Author: XueChong   Version 1.0    Data:2018.03.19
  Description:    load map
                  load road
                  recv CurGNSS
                  compute
                  give all posible road error
  Others:         // dependent of map
  Function List:  //
    1. main
    2. recvGNSS
    3. readMap
    4. readRoad
    5. error    return the current error, current gnss with road
    6. stepSeg    step another seg(road)
    7. alpha(ve)    preSight point
    8. ...
  History:        // 
    1. Date:2018.03.19
       Author:XueChong
       Modification:build up the framework
    2. Data:2018.03.19
       Author:XueChong
       Modification:add detail of function, defination of point, road, segment
    3. Data:2018.03.20
       Author:XueChong
       Modification:add all contents of function,like read Map
    4. Data:2018.03.20
       Author:XueChong
       Modification:realize almost all functions, eg. recvGNSS(), readRoad()
                    add new function, eg. error(), stepSeg()
    5. Data:2018.03.20
       Author:XueChong
       Modification:add details and check
    6. ...
*************************************************/
'''
#import packages
import sys
import time
import threading
import signal
import os.path

#defination of structures
# one point
class RoadPoint:
    def __init__(self,lat = -1,lon = -1,head = -1):
        self.lat = lat
        self.lon = lon
        self.head = head
        pass

# road consists of points, with id, left, right, speed, width
class Road:
    def __init__(self,ID = -1):
        self.id = ID
        self.left = -1
        self.right = -1
        self.speed = 10
        self.width = 3.5
        self.points = []
        pass

# segment consists of roads
class Segment:
    def __init__(self,ID = -1):
        self.id = ID
        self.roads = []
        pass

point = RoadPoint()
road = Road()

def test():
    ro = Road()


test()
