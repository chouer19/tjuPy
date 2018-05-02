
import zmq
from proContext import *
import time

ctx = proContext()
pub = ctx.socket(zmq.PUB)
pub.bind('tcp://*:6001')

content = {'name':'xuechong', 'age':24, 'school':'Tsinghuaaaaaaaaaaaaaaaaaaaaaaaaa'}
content_ = {'name':'shabi', 'age':100, 'school':'Tuttle'}


while True:
    pub.sendPro('test',content)
    time.sleep(0.2)
