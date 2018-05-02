#!/bin/env python
# -*- coding: utf-8 -*-
#filename: peartest.py

import threading, signal

is_exit = False

def doStress(i, cc):
    global is_exit
    idx = i
    while not is_exit:
        if (idx < 10000000):
            print "thread[%d]: idx=%d"%(i, idx)
            idx = idx + cc
        else:
            break
    if is_exit:
        print "receive a signal to exit, thread[%d] stop."%i
    else:
        print "thread[%d] complete."%i

def handler(signum, frame):
    global is_exit
    is_exit = True
    print "receive a signal %d, is_exit = %d"%(signum, is_exit)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    cc = 5
    t = threading.Thread(target=doStress, args=(0,cc))
    t.setDaemon(True)
    t.start()
    while 1:
        alive = False
        alive = alive or t.isAlive()
        if not alive:
            break
