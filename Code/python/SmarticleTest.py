#SmarticleTest.py

from SmarticleSwarm import SmarticleSwarm
from random import randint
import time
import numpy as np


def rx_callback(xbee_message):
    '''Simple call_back function to print received packets'''

    print("From {} >> {}".format(xbee_message.remote_device.get_node_id(),
                             xbee_message.data.decode()))

def random_gaits(x):
    '''Generates and sends unique random gaits of x points to all smarticles in network'''
    for dev in swarm.xb.devices.values():
        L = [randint(0,180) for x in range(x)]
        R = [randint(0,180) for x in range(x)]
        gait=[L,R]
        #randomly generate period between 200 and 300ms
        swarm.gi(gait,randint(200,300),remote_device=dev)
        time.sleep(0.2)
        swarm.set_pose(L[0],R[0],remote_device=dev)

def pseudo_inactive_smart2(x):
    '''Generates and sends random gaits centered around 90 degress to smart2'''
    dev = swarm.xb.smart2
    L = [int(np.random.normal(90,15)) for x in range(x)]
    R = [int(np.random.normal(90,15)) for x in range(x)]
    #uniform random gait between 70 and 110
    # L = [randint(70,110) for x in range(x)]
    # R = [randint(70,110) for x in range(x)]

    gait=[L,R]
    #randomly generate period between 200 and 300ms
    swarm.gi(gait,randint(200,300),remote_device=dev)
    time.sleep(0.2)
    #set smarticles to initial position in gait
    swarm.set_pose(L[0],R[0],remote_device=dev)

def timed_go(min):
    '''runs gait interpolation for inputted duration of time'''
    s = int(min*60)
    swarm.set_servos(1)
    print("sleeping for {} minutes...".format(min))
    time.sleep(s)
    swarm.set_servos(2)

#instantiate SmarticleSwarm object with default args
#change/specify USB port!!
swarm = SmarticleSwarm(port='/dev/tty.usbserial-DN050I6Q')
swarm.xb.add_rx_callback(rx_callback)
#discover smarticles on network; by default has 15s timeout
swarm.build_network(5)
#change all smarticles to gait interpolate mode
swarm.set_mode(2)
time.sleep(0.1)
#send random gaits to smarticles
random_gaits(15)
time.sleep(0.1)
#make smarticle 2 pseudo inactive
# pseudo_inactive_smart2(15)
