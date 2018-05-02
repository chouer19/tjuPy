
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
import UTM 

# zmq tools
ctx = proContext()

SpeedSetAddr = 'tcp://127.0.0.1:8098'
pub= ctx.socket(zmq.PUB)
pub.bind(SpeedSetAddr)

while True:
    #speed,gear = input()
    speed = input()
    #if str(speed).isdigit() and str(gear).isdigit():
    if str(speed).isdigit():
        speed = int(speed)
        #gear = int(gear)
        pub.sendPro("SpeedSet",speed )
