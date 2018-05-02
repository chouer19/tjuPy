import sys
import threading
import time
import signal


is_exit = False
i = 0
def func():
    global i
    #global is_exit
    while not is_exit:
        print(i)
        time.sleep(0.5)

    print('exited')



def handler(signum, frame):
    global is_exit
    is_exit = True
    print "receive a signal %d, is_exit = %d"%(signum, is_exit)

def main():
    global i
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    threads = []
    t = threading.Thread(target = func,args = ())
    t.setDaemon(True)
    threads.append(t)
    #t.start()
    for th in threads:
        th.start()
    
    while t.isAlive():
        i = (i + 1) % 9999
        pass
    
    
    print('ended')


if __name__ == "__main__":
    main()
