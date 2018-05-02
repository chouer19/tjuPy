import pygame, sys
from pygame.locals import *
from math import pi
import math
import utils
import proUTM
import utm

pygame.init()
screen = pygame.display.set_mode((971,701))
#screen = pygame.display.set_mode((1361,1001))
pygame.display.set_caption("fuck")

FPS = 50
fpsClock = pygame.time.Clock()
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
DARKPINK = (255,20,147)
DARKRED = (138,0,0)
PURPLE = (160,32,240)
YELLOW = (255,255,0)
GREEN = (00,255,0)
BLUE = (0,0,255)
LIGHTBLUE = (176,226,255)
ORANGE4 = (139,69,0)
screen.fill(BLACK)
global E 
E = 1.07

global minX 
global minY
global offsetX
global offsetY
class Line:
   def __init__(self,thisType):
      self.type = thisType
      self.points = []


mapLines = []
mapPoints = []
def readMap():
   global minX
   global minY
   global offsetX
   global offsetY
   offsetX = -249963.28216614993 - 30.5
   offsetY = -337.179002976045 - 28.7
   offsetX = 28
   offsetY = -1766
   mapMinX = 999999
   mapMinY = 9999999
   f = open('./YBY-1.txt','r')
   lineRead = f.readline()
   #for lineRead in open('../data/YBY-1.txt',encoding='utf-8', errors='ignore'):
   while lineRead:
      lineRead = f.readline()
      lineSplit = lineRead.split()
      #read points
      if len(lineSplit) > 0 and lineSplit[0] == 'POINT':
         lineRead = f.readline()
         lineRead = f.readline()#type
         lineRead = f.readline()#zuobiao
         lineSplit = lineRead.split()
         #x,y = float(lineSplit[0]) - 4414360,float(lineSplit[1])-429000
         y,x = float(lineSplit[0]) + offsetY ,float(lineSplit[1]) + offsetX
         mapMinX = x if x < mapMinX else mapMinX
         mapMinY = y if y < mapMinY else mapMinY
         mapPoints.append([x,y])
      #read lines
      if  len(lineSplit) > 0 and lineSplit[0] == 'LINE':
         lineRead = f.readline()#what type???
         lineRead = f.readline()#read real type
         lineSplit = lineRead.split()#split type
         theType = int(float(lineSplit[0]))#get Type
         line = Line(theType)
         lineRead = f.readline()#num
         lineSplit = lineRead.split()#split num
         length = int(float(lineSplit[0]))#get Type
         for i in range (0,length):
            lenlen = len(line.points)
            lineRead = f.readline()#zuobiao
            lineSplit = lineRead.split()
            y,x = float(lineSplit[0]) + offsetY ,float(lineSplit[1])+ offsetX
            mapMinX = x if x < mapMinX else mapMinX
            mapMinY = y if y < mapMinY else mapMinY
#            #spline
#            if lenlen > 0 and (line.type == 129998):
#               for k in range(0,8):
#                  x1 = x + (x - line.points[lenlen-1][0] ) * (k+1) / 9
#                  y1 = y + (y - line.points[lenlen-1][1] ) * (k+1) / 9
#                  line.points.append([x1,y1])
            line.points.append([x,y])
#         lineSpline = Line(line.type)
         #lineSpline.points.append(line.points[0])
#         for i in range(0,len(line.points)-2):
#            lineSpline.points.append(line.points[i])
#            for k in range(0,9):
#               x1 = line.points[i][0] + (line.points[i+1][0] - line.points[i][0] ) * (k+1) / 10
#               y1 = line.points[i][1] + (line.points[i+1][1] - line.points[i][1] ) * (k+1) / 10
#               lineSpline.points.append([x1,y1])
#         lineSpline.points.append(line.points[len(line.points) - 1])   
         mapLines.append(line)
         #mapLines.append(lineSpline)
   #print(points)
   #print(lines)
   print('done reading map .......................')
   minX = mapMinX
   minY = mapMinY
   print('min X of map is : ',mapMinX)
   print('min Y of map is : ',mapMinY)
   f.close()

#data read from offline txt
onlineData = []
class Point:
   def __init__(self,x,y,h):
      self.x = x
      self.y = y
      self.heading = h
def readOfflineData():
   global minX
   global minY
   global offsetX
   global offsetY
   mapMinX = 999999
   mapMinY = 9999999
   f = open('./065631.txt','r')
   lineRead = f.readline()
   #for lineRead in open('../data/YBY-1.txt',encoding='utf-8', errors='ignore'):
   while lineRead:
      lineSplit = lineRead.split()
      if lineSplit[7] == 'True':
         lat = float(lineSplit[0])
         lon = float(lineSplit[1])
         heading = float(lineSplit[2])
         x1,y1 = utils.BLH2XYZ(lat,lon,heading)
         x,y,z = proUTM.LLtoUTM(23,lat,lon)
         #print(math.sqrt( (x - x1 - offsetX) * (x - x1 - offsetX) + (y - y1 - offsetY)*(y - y1 - offsetY) ) )
         #print(x,'   ',y)
         print(y - y1)
         mapMinX = x if x < mapMinX else mapMinX
         mapMinY = y if y < mapMinY else mapMinY
         point = Point(x,y,heading)
         onlineData.append(point)
      lineRead = f.readline()
   #print(onlineData)
   #print(len(onlineData))
   print('done reading onlineData ......................')
   print('min X of onlineData is : ',mapMinX)
   print('min Y of onlineData is : ',mapMinY)
   print('min X of diff is : ',minX - mapMinX)
   print('min Y of diff is : ',minY - mapMinY)
   f.close()
      
def drawCarRed():
   pygame.draw.circle(screen,RED,[730 - 1*6 + 3,450 - 2*6 - 3],3,2)
   pygame.draw.circle(screen,RED,[730 + 1*6 - 3,450 - 2*6 - 3],3,2)
   pygame.draw.rect(screen,LIGHTBLUE,[730 - 1*6, 450 - 2*6, 2*6 , 4*6 ])
   pygame.draw.circle(screen,RED,[240 - 1*6 + 3,450 - 2*6 - 3],3,2)
   pygame.draw.circle(screen,RED,[240 + 1*6 - 3,450 - 2*6 - 3],3,2)
   pygame.draw.rect(screen,LIGHTBLUE,[240 - 1*6, 450 - 2*6, 2*6 , 4*6 ])

def drawCarYellow():
   pygame.draw.circle(screen,YELLOW,[730 - 1*6 + 3,450 - 2*6 - 3],3,3)
   pygame.draw.circle(screen,YELLOW,[730 + 1*6 - 3,450 - 2*6 - 3],3,3)
   pygame.draw.rect(screen,LIGHTBLUE,[730 - 1*6, 450 - 2*6, 2*6 , 4*6 ])
   pygame.draw.circle(screen,YELLOW,[240 - 1*6 + 3,450 - 2*6 - 3],3,3)
   pygame.draw.circle(screen,YELLOW,[240 + 1*6 - 3,450 - 2*6 - 3],3,3)
   pygame.draw.rect(screen,LIGHTBLUE,[240 - 1*6, 450 - 2*6, 2*6 , 4*6 ])

#draw circle with 1.07 ** 1 ......
def drawLogInRoll():
   for i in range (1,76):
      pygame.draw.circle(screen,ORANGE4,[240,450],i * 6,1)

def drawMiInRoll():
   global E
   for i in range (2,151):
      pygame.draw.circle(screen,ORANGE4,[240,450],int(math.log(i) / math.log(E) * 6),1)

def drawAxisX():
   pygame.draw.line(screen, RED,[0,450],[481,450],2)
def drawAxisY():
   pygame.draw.line(screen, RED,[240,0],[240,701],2)
def getRelatedXY(x0,y0,x1,y1,angle):
   angle = angle + 180
   x = math.cos(math.radians(angle)) * (x1 - x0) - math.sin(math.radians(angle)) * (y1 - y0)
   y = math.sin(math.radians(angle)) * (x1 - x0) + math.cos(math.radians(angle)) * (y1 - y0)
   return -x, y
   #return (x1 - x0),(y1 - y0)
def drawMapInRoll(curIndex):
   #print(onlineData[curIndex].heading)
   pygame.draw.rect(screen,BLACK,[490,0,481,701])
   pygame.draw.rect(screen,BLUE,[482,0,8,701])
   for i in range (0,len(mapPoints)):
      x,y = getRelatedXY(onlineData[curIndex].x, onlineData[curIndex].y, mapPoints[i][0], mapPoints[i][1], onlineData[curIndex].heading)
      #x,y = mapPoints[i][0] - onlineData[curIndex].x,  mapPoints[i][1] - onlineData[curIndex].y
      pygame.draw.circle(screen,RED,[int(x * 6 + 730), int(y * 6 + 450)],2,0)
      pygame.draw.circle(screen,GREEN,[int(x * 6 + 730), int(y * 6 + 450)],3,1)
   for i in range(0,len(mapLines)):
      pointlist = []
      for j in range(0,len(mapLines[i].points)):
         x,y = getRelatedXY(onlineData[curIndex].x, onlineData[curIndex].y,mapLines[i].points[j][0] ,mapLines[i].points[j][1], onlineData[curIndex].heading)
         #x,y = mapLines[i].points[j][0] - onlineData[curIndex].x,  mapLines[i].points[j][1] - onlineData[curIndex].y
         #print('[',x,',',y,']')
         pointlist.append([int(x * 6 + 730),int(y * 6 + 450)])
      #lane
      if mapLines[i].type == 410400 :
         pygame.draw.lines(screen, WHITE,False,pointlist, 1)
      #edge
      if mapLines[i].type == 450100:
         pygame.draw.lines(screen, RED,False,pointlist, 2)
      #indicator
      if mapLines[i].type == 490001:
         pygame.draw.lines(screen, YELLOW,False,pointlist, 2)
      #stop line
      if mapLines[i].type == 490004:
         pygame.draw.lines(screen, DARKRED,False,pointlist, 2)
      #virtual edge and stop line
      if mapLines[i].type == 129998:
         pygame.draw.lines(screen,DARKPINK,False,pointlist, 2)
      #virtual
      #if mapLines[i].type == 149997:
      #   pygame.draw.lines(screen,PURPLE,False,pointlist, 1)
def drawOffDataInLog(curIndex):
   global E
   pathLeft = []
   pathRight = []
   for i in range (0,len(onlineData)):
      x,y = getRelatedXY(onlineData[curIndex].x, onlineData[curIndex].y, onlineData[i].x, onlineData[i].y, onlineData[curIndex].heading)
      if x*x + y*y > 1:
         x = ((math.log(math.sqrt(x*x + y*y)) / math.log(E)) / math.sqrt(x*x + y*y)) * x
         y = ((math.log(math.sqrt(x*x + y*y)) / math.log(E)) / math.sqrt(x*x + y*y)) * y
         pygame.draw.circle(screen,GREEN,[int(x * 6 + 240), int(y * 6 + 450)],2,0)
      
def drawOffDataInRoll(curIndex):
   global E
   pathLeft = []
   pathRight = []
   for i in range (0,len(onlineData)):
      x,y = getRelatedXY(onlineData[curIndex].x, onlineData[curIndex].y, onlineData[i].x, onlineData[i].y, onlineData[curIndex].heading)
      pygame.draw.circle(screen,GREEN,[int(x * 6 + 730), int(y * 6 + 450)],2,0)

def drawMapInLog(curIndex):
   global E
   #print(onlineData[curIndex].heading)
   for i in range (0,len(mapPoints)):
      x,y = getRelatedXY(onlineData[curIndex].x, onlineData[curIndex].y, mapPoints[i][0], mapPoints[i][1], onlineData[curIndex].heading)
      #x,y = mapPoints[i][0] - onlineData[curIndex].x,  mapPoints[i][1] - onlineData[curIndex].y
      if x*x + y*y > 1:
         x = ((math.log(math.sqrt(x*x + y*y)) / math.log(E)) / math.sqrt(x*x + y*y)) * x
         y = ((math.log(math.sqrt(x*x + y*y)) / math.log(E)) / math.sqrt(x*x + y*y)) * y
         pygame.draw.circle(screen,RED,[int(x * 6 + 240), int(y * 6 + 450)],2,0)
         pygame.draw.circle(screen,GREEN,[int(x * 6 + 240), int(y * 6 + 450)],3,1)
   for i in range(0,len(mapLines)):
      pointlist = []
      for j in range(0,len(mapLines[i].points)):
         x,y = getRelatedXY(onlineData[curIndex].x, onlineData[curIndex].y,mapLines[i].points[j][0] ,mapLines[i].points[j][1], onlineData[curIndex].heading)
         if x*x + y*y > 1:
            x = ((math.log(math.sqrt(x*x + y*y)) / math.log(E)) / math.sqrt(x*x + y*y)) * x
            y = ((math.log(math.sqrt(x*x + y*y)) / math.log(E)) / math.sqrt(x*x + y*y)) * y
            pointlist.append([int(x * 6 + 240),int(y * 6 + 450)])
         else:
            break;
      #lane
      if mapLines[i].type == 410400 and len(pointlist) > 1:
         pygame.draw.lines(screen, WHITE,False,pointlist, 1)
      #edge
      if mapLines[i].type == 450100 and len(pointlist) > 1:
         pygame.draw.lines(screen, RED,False,pointlist, 2)
      #indicator
      if mapLines[i].type == 490001 and len(pointlist) > 1:
         pygame.draw.lines(screen, YELLOW,False,pointlist, 2)
      #stop line
      #if mapLines[i].type == 490004 and len(pointlist) > 1:
      #   pygame.draw.lines(screen, DARKRED,False,pointlist, 2)
      #virtual edge and stop line
      if mapLines[i].type == 129998 and len(pointlist) > 1:
         pygame.draw.lines(screen,DARKPINK,False,pointlist, 2)
      #virtual
      #if mapLines[i].type == 149997 and len(pointlist) > 1:
      ##   pygame.draw.lines(screen,PURPLE,False,pointlist, 1)
      pygame.draw.circle(screen,BLACK,[240,450],6,0)

readMap()
readOfflineData()
offDataLength = len(onlineData)
index = 0
isRed = True
while True:
   screen.fill(BLACK)
   for event in pygame.event.get():
      if event.type == QUIT:
         pygame.quit()
         sys.exit()
   #drawLogInRoll()
   drawMiInRoll()
   drawAxisX()
   #drawAxisY()
   drawMapInLog(index)
   drawOffDataInLog(index)
   drawMapInRoll(index)
   drawOffDataInRoll(index)
   if isRed:
      isRed = False
      drawCarRed()
   else:
      isRed = True
      drawCarYellow()
   #update index of current car,position
   index = (index + 1 + offDataLength) % offDataLength
   pygame.display.update()
   fpsClock.tick(FPS)
