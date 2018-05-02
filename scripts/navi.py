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
    5. Data:2018.03.23
       Author:XueChong
       Modification:add details and check
    6. Data:2018.03.23
       Author:XueChong
       Modification:run on Driving-brain
                    smooth the head and tarHead at map head * 5 / 5
                    compute dhead, not only the forehead but the backward
                    alpha(ve), the minimum is six but not zero, min(6,y)
    7. Data:2018.03.28
       Author:XueChong
       Modification: new U-Turn of segID=40
                    
    8. ...
*************************************************/
'''
#import packages
import sys
import time
import math
import threading
import signal
import os.path
# some packages' dir
sys.path.append("../libs")
from proContext import *
from proMCU import *
from proPrint import *
import UTM

#defination of structures
# one point
class RoadPoint:
    def __init__(self,lat = -1,lon = -1,head = -1):
        self.lat = lat
        self.lon = lon
        self.head = head
        pass

# road consists of points, with id, left, right, speed, width
class ROad:
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

#define variables
#if Ctrl-C are pressed, default is False
is_exit = False

# zmq tools
ctx = proContext()

map_file = '../data/map/tju.map'
road_file = '../data/map/tju.road'
#Map is all map content, a list including segments which include roads which include points
Map = []
#Road is a tourp net that 
#list of segID,roadID
Road = []
#list of lat,lon,head for following
Path = []
PathMark = 0

Left = -1
Right = -1
Speed = 10
Width = 3.5
SegID = -1
RoadID = -1
nextLeft = -1
nextRight = -1
nextSpeed = 10
nextWidth = 3.5
nextSegID = -1
nextRoadID = -1

# global variable of node for searching
node = {"Status":0,"Lat":0,"Lon":0,"Speed":0,"Head":0}
# address and port for publish messages
GnssAddr = 'tcp://127.0.0.1:8080'
NavAddr = 'tcp://127.0.0.1:8090'

def handler(signum, frame):
    global is_exit
    is_exit = True
    print "receive a signal %d, is_exit = %d"%(signum, is_exit)

#define main functions
def main(args):
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    # get file path from args
    global map_file
    global road_file
    if len(args) > 0:
        road_file = args[0]
    if len(args) > 1:
        map_file = args[1]

    assert os.path.isfile(map_file),'map file not exist, please check again'
    assert os.path.isfile(road_file),'road file not exist, please check again'

    #readMap
    #got Map []
    readMap()

    #readRoad
    #got Road []
    readRoad()

    # defination of all the threads
    #
    tGNSS= threading.Thread(target = recvGNSS, args = ())

    tGNSS.setDaemon(True)

    # start all threads
    tGNSS.start()

    prGreen('all threads started ......')

    alive = True
    while not is_exit:
        time.sleep(0.5)
        pass
    pass

    prRed('all threads were ended by Ctrl-C')
    off()


def showAbstract():
    pass

def readMap():
    global Map
    print('start reading map......')
    with open(map_file) as fMap:
        fMap.readline()
        line = fMap.readline()
        lineNum = 0
        #read map line by line
        while line:
            #split line with space, to contents list
            contents = line.split('\t')
            #if too slow, there is not enough messages, read and continue
            if len(contents) < 8:
                line = fMap.readline()
                continue
            #build a new object
            #starting reading a road
            road = ROad()
            seID = int(contents[0])
            road.id = int(contents[1])
            road.left = int(contents[2])
            road.right = int(contents[3])
            #road.speed = int(contents[4])
            #road.width = int(content[5])
            #left are point list of lat,lon,head
            for content in contents[4:]:
                args = content.split(',')
                #lat,lon,head
                if(len(args) > 2):
                    #road.points.append( RoadPoint(float(args[0]), float(args[1]), float(args[2])) )
                    road.points.append( RoadPoint(float(args[1]), float(args[0]), float(args[2])) )
            #ended reading a road
            #for now, road is ok, need to add it to a seg or new a seg for it
            pass
            #check if this segID existed in Map
            isHave = False
            #if existed, add the road to 
            for i,seg in enumerate(Map):
                if seg.id == seID:
                    isHave = True
                    Map[i].roads.append(road)
                    break
            #if not existed, add a new seg
            if not isHave:
                seg = Segment(seID)
                seg.roads.append(road)
                Map.append(seg)
            line = fMap.readline()
            lineNum = lineNum + 1
            if lineNum % 5 == 0:
                prBlue('loaded ' + str(lineNum) +  ' roads until now................')

    print('end reading map')
    pass

#define read road
def readRoad():
    global Road
    global SegID
    global RoadID
    global nextSegID
    global nextRoadID
    print('start reading road .......')
    with open(road_file) as fRoad:
        fRoad.readline()
        line = fRoad.readline()
        while line:
            if len(line.split('\t')) > 1:
                Road.append( [int(line.split('\t')[0]), int(line.split('\t')[1])] )
            line = fRoad.readline()
        pass
    pass
    nextSegID = Road[0][0]
    nextRoadID = Road[0][1]
    print('end reading road number .......')
    

#define recv policy command
# steer limit and config
def recvGNSS():
    global ctx
    global node
    sub = ctx.socket(zmq.SUB)
    sub.connect(GnssAddr)
    sub.setsockopt(zmq.SUBSCRIBE,'CurGNSS')

    pub= ctx.socket(zmq.PUB)
    pub.bind(NavAddr)

    prGreen('thread recvGNSS started')
    i = 0
    while not is_exit:
        i = (i+1) % 9999
        content = sub.recvPro()
        node = content
        send = error()
        if send is not None:
            pub.sendPro("Road",send)
            if i % 20 == 0:
                prContent = "seg: " + str(send['SegID']) + "\t\troad: " + str(send['RoadID']) + "\t\tdis: "\
                            + str(send['Dis']) + '\t\thead: ' + str(send['Head'])
                if(math.fabs(send['Dis']) < 0.2 ):
                    prGreen(prContent)
                    prGreen(send)
                elif(math.fabs(send['Dis']) < 0.4 ):
                    prBlue(prContent)
                    prBlue(send)
                elif(math.fabs(send['Dis']) < 0.6 ):
                    prYellow(prContent)
                    prYellow(send)
                else:
                    prRed(prContent)
                    prRed(send)
        pass
    print('thread recvGNSS ended by Ctrl-C')
    pass

# distance for foresight
def alpha(ve):
    return  max( ( ( math.log1p(ve) ) )  + ve * 3/4 + 2, 6)

def stepSeg():
    global Road
    global Path
    global SegID
    global RoadID
    global Left
    global Right 
    global Speed
    global Width
    global nextLeft
    global nextRight
    global nextSpeed
    global nextWidth
    global nextSegID
    global nextRoadID
    global PathMark

    #Left = nextLeft
    #Right = nextRight
    #Width = nextWidth
    #Speed = nextSpeed
    #SegID = nextSegID
    #RoadID = nextRoadID
    if len(Road) > 0:
        nextSegID = Road[0][0]
        nextRoadID = Road[0][1]
        for i,seg in enumerate(Map):
            if seg.id == Road[0][0]:
                #prGreen('found seg')
                for j,road in enumerate(seg.roads):
                    if road.id == Road[0][1]:
                        #prGreen('found road')
                        PathMark = len(road.points) - 1
                        Path = Path + road.points
                        nextLeft = road.left
                        nextRight = road.right
                        nextSpeed = road.speed
                        nextWidth = road.width
                        break
                        pass
                break
    Road = Road[1:]
    pass

def getRelatedXY(x0,y0,x1,y1,angle):
    angle = angle + 180
    x = math.cos(math.radians(angle)) * (x1 - x0) - math.sin(math.radians(angle)) * (y1 - y0)
    y = math.sin(math.radians(angle)) * (x1 - x0) + math.cos(math.radians(angle)) * (y1 - y0)
    return -x, y


def error():
    global Path
    global PathMark
    global SegID
    global RoadID
    global Left 
    global Right
    global Width
    global Speed
    # if terminal on trajectory
    if len(Path) < 3 and len(Road) == 0:
        content = {"SegID":0,"RoadID":0,"Left":0,"Right":0,"Speed":0,"Width":0,"Dis":0,"Head":0,"DHead":0}
        return content
        pass

    # if Path's data too little
    while len(Path) < 25 and len(Road) > 0:
        prGreen("path too less and len(Road) > 0, so step another seg")
        stepSeg()

    #now , there is no road left, ending

    #current X,Y from Lat,Lon
    easting,northing,zone,zone_letter = UTM.from_latlon(node['Lat'],node['Lon'])
    curDis = 9999999
    #fine nearest point
    mark = 0
    markE = 0
    markN = 0
    for i,p in enumerate(Path):
        dffhead = math.fabs( int(node['Head'] - p.head  )  )
        if dffhead > 75 and dffhead < 275:
            continue
        E,N,Z,Z_l = UTM.from_latlon(p.lat ,p.lon )
        dis = math.sqrt(math.fabs( math.pow(easting - E,2) + math.pow(northing - N,2))  )
        if dis < curDis:
            curDis = dis 
            mark = i
            markE = E
            markN = N

    if curDis > 20:
        stepSeg()
        prGreen("closet point too long away, find on, so step another seg")
        Path = Path[mark:]
        return error()

    #got closet X,Y
    closeX,closeY = getRelatedXY(easting, northing, markE, markN, node['Head'])
    curV = node['Speed']
    #compute pre point
    alp = alpha(curV)
    tarDis = 99999
    tarMark = mark
    tarHead = Path[mark].head
    if len(Path) - mark < 50:
        stepSeg()
        prGreen("not enough point for looking asight , so step another seg")
    for i,p in enumerate(Path[mark:]):
        E,N,Z,Z_l= UTM.from_latlon(p.lat,p.lon )
        dis = math.fabs( math.sqrt( math.fabs(math.pow(easting - E,2 )) + \
              math.pow(northing - N,2)  ) - alp )
        if dis < tarDis:
            tarDis = dis
            tarMark = mark + i
            tarHead = p.head
    
    #got target head
    head = tarHead - node['Head']
    if head < -180:
        head = head + 360
    if head > 180:
        head = head - 360
    TarHead = Path[max(tarMark - 2,0)].head
    head1 = tarHead - node['Head']
    if head1 < -180:
        head1 = head1 + 360
    if head1 > 180:
        head1 = head1 - 360
    TarHead = Path[max(tarMark - 1,0)].head
    head2 = tarHead - node['Head']
    if head2 < -180:
        head2 = head2 + 360
    if head2 > 180:
        head2 = head2 - 360
    TarHead = Path[min(tarMark +1 ,len(Path) - 1)].head
    head3 = tarHead - node['Head']
    if head3 < -180:
        head3 = head3 + 360
    if head3 > 180:
        head3 = head3 - 360
    TarHead = Path[min(tarMark + 2 ,len(Path) - 1)].head
    head4 = tarHead - node['Head']
    if head4 < -180:
        head4 = head4 + 360
    if head4 > 180:
        head4 = head4 - 360
    head = (head + head1 + head2 + head3 + head4) / 5

    #got qulv of this
    Head = ( Path[max(mark - 2,0)].head +  Path[max(mark - 1,0)].head + Path[max(mark - 0,0)].head + Path[min(mark + 1,len(Path) - 1)].head + Path[min(mark + 2,len(Path) -1 )].head ) /5
    TarHead = ( Path[max(tarMark - 2,0)].head +  Path[max(tarMark - 1,0)].head + Path[max(tarMark - 0,0)].head + Path[min(tarMark + 1,len(Path) - 1)].head + Path[min(tarMark + 2,len(Path) -1 )].head ) /5
    #Head = Path[max(mark,0)].head
    index = 0
    if node['Speed'] < 4:
        #index = tarMark - mark
        index = 10
    Head = Path[max(mark - index,0)].head
    TarHead = Path[max(tarMark,0)].head
    dhead = TarHead - Head
    if dhead < -145:
        dhead = dhead + 360
    if dhead > 145:
        dhead = dhead - 360

    Head = Path[max(mark - index -2,0)].head
    TarHead = Path[max(tarMark - 2,0)].head
    dhead2 = TarHead - Head
    if dhead2 < -145:
        dhead2 = dhead2 + 360
    if dhead2 > 145:
        dhead2 = dhead2 - 360

    Head = Path[max(mark - index -1,0)].head
    TarHead = Path[max(tarMark - 1,0)].head
    dhead3 = TarHead - Head
    if dhead3 < -145:
        dhead3 = dhead3 + 360
    if dhead3 > 145:
        dhead3 = dhead3 - 360

    Head = Path[max(mark - index +1,0)].head
    TarHead = Path[min(tarMark +1 ,len(Path) - 1)].head
    dhead4 = TarHead - Head
    if dhead4 < -145:
        dhead4 = dhead4 + 360
    if dhead4 > 145:
        dhead4 = dhead4 - 360

    Head = Path[max(mark - index + 2,0)].head
    TarHead = Path[min(tarMark + 2 ,len(Path) - 1)].head
    dhead5 = TarHead - Head
    if dhead5 < -145:
        dhead5 = dhead5 + 360
    if dhead5 > 145:
        dhead5 = dhead5 - 360

    dhead = ( dhead + dhead5 + dhead2 + dhead3 + dhead4) / 10
    #print(mark)
    #print(tarMark)
    #print(Head)
    #print(TarHead)
    #print(dhead)
    #print("=========================")

    if mark > len(Path) - PathMark:
        SegID = nextSegID
        RoadID = nextRoadID
        Left = nextLeft
        Right = nextRight
        Width = nextWidth
        Speed = nextSpeed
    if SegID == 40:
        #dhead = dhead - 10
        closeX = closeX - 8
    content = {"SegID":SegID,"RoadID":RoadID,"Left":Left,"Right":Right,"Speed":Speed,"Width":Width,"Dis":closeX,"Head":head,"DHead":dhead}
    #Path = Path[mark:]
    Path = Path[max(0, mark * 2 - tarMark):]
    return content
    pass

def off():
    pass

if __name__ == "__main__":
    #args list
    #args one mapname, default is '../data/map/tju.map'
    main(sys.argv[1:])

