
import zmq
from proContext import *
import time

ctx = proContext()

sub2 = ctx.socket(zmq.SUB)
sub2.connect('tcp://localhost:6001')
sub2.setsockopt(zmq.SUBSCRIBE,'test')
#content = {'name':'xuechong', 'age':24, 'school':}
i = 0

while True:
    content = sub2.recvPro()
    print(i)
    i = i+1
    i = i % 1000
    content = sub2.recvPro()
    print("topic : test")
    print('name :',content['name'], 'age : ',content['age'], 'school : ', content['school'])

