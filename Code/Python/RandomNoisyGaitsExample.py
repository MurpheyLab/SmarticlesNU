# SmarticleSyncExample.py
import sys
sys.path.append('modules')

from SmarticleSwarm import *
from random import randint
import time
import numpy as np
import math

# TO DO: change to your port
PORT_NAME = '/dev/tty.usbserial-DN05LPOA'


def rx_callback(xbee_message):
    '''Simple call_back function to print received packets'''

    print("From {} >> {}".format(xbee_message.remote_device.get_node_id(),
                             xbee_message.data))

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
# discover smarticles on network; by default has 15s timeout
swarm.build_network(8)

# initialize square gait
swarm.set_mode(2)
L = [0,180,180,0]
R = [0,0,180,180]
swarm.gait_init([L,R],450) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
swarm.set_pose_noise(25)
# maximum value should be less than 50% of gait period (450ms in this example)
# In practice I wouldnt go above 40-45%
swarm.set_sync_noise(200)
# always call this after updating gait in swarm.gait_init()
swarm.init_sync_thread()

# initialize streaming settings
# turns on random delay of max 100ms
swarm.set_delay(1,100);
gaitf = lambda t: [190,190] #[190,190] signifies unique random corners
stream = StreamThread(swarm.xb,gaitf,450)
stream.run_flag.clear()
stream.start()






## to start sync:
# swarm.start_sync()
## or use
# timed_sync(minutes)

#if you dont want them to be synchronized:
#swarm.set_servos(1) or timed_go(minutes)
