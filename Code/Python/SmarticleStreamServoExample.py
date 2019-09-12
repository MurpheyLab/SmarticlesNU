#SmarticleSyncExample.py

from modules.SmarticleSwarm import SmarticleSwarm
from modules.StreamThread import StreamThread
from random import randint
import time
import numpy as np
import math

# TO DO: change to your port
PORT_NAME = '/dev/tty.usbserial-DN050I6Q'


def rx_callback(xbee_message):
    '''Simple call_back function to print received packets'''

    print("From {} >> {}".format(xbee_message.remote_device.get_node_id(),
                             xbee_message.data.decode()))

def random_gaits(num_pts, delay_ms):
    '''Generates and sends unique random gaits of x points to all smarticles in network'''
    for dev in swarm.xb.devices.values():
        L = [randint(0,180) for x in range(num_pts)]
        R = [randint(0,180) for x in range(num_pts)]
        gait=[L,R]
        #if you want them to have different delays
        #delay_ms = randint(200,300)
        swarm.gi(gait,delay_ms,remote_device=dev)
        #move to first pose in gait sequence
        swarm.set_pose(L[0],R[0],remote_device=dev)

def timed_sync(min):
    '''runs gait interpolation for inputted duration of time'''
    s = int(min*60)
    swarm.start_sync()
    print("sleeping for {} minutes...".format(min))
    time.sleep(s)
    swarm.stop_sync()

def timed_go(min):
    '''runs gait interpolation for inputted duration of time'''
    s = int(min*60)
    swarm.set_servos(1)
    print("sleeping for {} minutes...".format(min))
    time.sleep(s)
    swarm.set_servos(0)


# instantiate SmarticleSwarm object with default args
# change/specify USB port!!
swarm = SmarticleSwarm(port=PORT_NAME)
swarm.xb.add_rx_callback(rx_callback)
gaitf = lambda t: round(90+45*math.sin(math.pi/5*t))
# discover smarticles on network; by default has 15s timeout
swarm.build_network(5)
stream = StreamServo(swarm.xb,gaitf,400)
# #change all smarticles to gait interpolate mode
# swarm.set_mode(2)
#
# #send all smarticles the same random gait
# n=15
# L = [randint(30,60) for x in range(n)]
# R = [randint(70,110) for x in range(n)]
# swarm.gi([L,R],200) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms

# or if I want to send them each a unique random gait
# random_gaits(15, 200)


# always call this after updating gait in swarm.gi()
# swarm.init_sync_thread()

## to start sync:
# swarm.start_sync()
## or use
# timed_sync(minutes)

#if you dont want them to be synchronized:
#swarm.set_servos(1) or timed_go(minutes)
