#SmarticleSyncExample.py

from modules.SmarticleSwarm import SmarticleSwarm
from modules.StreamThread import StreamThread
from random import randint
import time
import numpy as np
import math

# TO DO: change to your port
PORT_NAME = '/dev/ttyUSB0'


def rx_callback(xbee_message):
    '''Simple call_back function to print received packets'''

    print("From {} >> {}".format(xbee_message.remote_device.get_node_id(),
                             xbee_message.data))

def random_gaits(num_pts, delay_ms):
    '''Generates and sends unique random gaits of x points to all smarticles in network'''
    for dev in swarm.xb.devices.values():
        L = [randint(0,180) for x in range(num_pts)]
        R = [randint(0,180) for x in range(num_pts)]
        gait=[L,R]
        #if you want them to have different delays
        swarm.gait_init(gait,delay_ms,remote_device=dev)
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

def go_to_stream():
    swarm.stop_sync()
    swarm.set_mode(1)
    stream.run_flag.set()

def go_to_gi():
    stream.run_flag.clear()
    swarm.set_mode(2)
    swarm.start_sync()


# instantiate SmarticleSwarm object with default args
# change/specify USB port!!
swarm = SmarticleSwarm(port=PORT_NAME)
swarm.xb.add_rx_callback(rx_callback)
# gaitf = lambda t: list(np.random.choice([0,180],2))
gaitf = lambda t: [190,190] #[190,190] signifies unique random corners
# discover smarticles on network; by default has 15s timeout
swarm.build_network(3)
swarm.set_mode(2)
swarm.set_delay(1,100)
#send all smarticles the same random gait
n=15
L = [0,180,180,0]
R = [0,0,180,180]
swarm.gait_init([L,R],400) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms

#or if I want to send them each a unique random gait
stream = StreamThread(swarm.xb,gaitf,450)
stream.run_flag.clear()
stream.start()
# #change all smarticles to gait interpolate mode
# swarm.set_mode(2)
#
# #send all smarticles the same random gait
# n=15
L = [0,180,180,0]
R = [0,0,180,180]
swarm.gait_init([L,R],450) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
swarm.init_sync_thread()
# or if I want to send them each a unique random gait
# random_gaits(15, 200)


# always call this after updating gait in swarm.gait_init()


## to start sync:
# swarm.start_sync()
## or use
# timed_sync(minutes)

#if you dont want them to be synchronized:
#swarm.set_servos(1) or timed_go(minutes)
