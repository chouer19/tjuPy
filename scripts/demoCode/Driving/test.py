import pygame, sys
from pygame.locals import *
from math import pi
import math
import utils

pygame.init()
screen = pygame.display.set_mode((971,701))
#screen = pygame.display.set_mode((1361,1001))
pygame.display.set_caption("fffffkkkkkkk")

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
class Line:
   def __init__(self,thisType):
      self.type = thisType
      self.points = []


mapLines = []
mapPoints = []
lines = []

for i in range(0,20):
    lines.append([i,i+i*i])
while True:
   screen.fill(BLACK)
   for event in pygame.event.get():
      if event.type == QUIT:
         pygame.quit()
         sys.exit()
   pygame.draw.lines(screen, WHITE,False, lines , 1)
   pygame.display.update()
   fpsClock.tick(FPS)
