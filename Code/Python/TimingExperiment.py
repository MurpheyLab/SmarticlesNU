# SmarticleSyncExample.py
import sys
sys.path.append('modules')

from SmarticleSwarm import *
from random import randint
import time
import numpy as np
import math

# TO DO: change to your port
PORT_NAME = '/dev/tty.usbserial-DN050I6Q'


def rx_callback(xbee_message):
    '''Simple call_back function to print received packets'''

    # print("From {}  {}".format(xbee_message.remote_device.get_node_id(),
    #                          xbee_message.data.decode("utf-8",errors="replace")))
    print(xbee_message.data.decode("utf-8",errors="backslashreplace"), end ='')

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



def go_to_gi():
    stream.run_flag.clear()
    swarm.set_mode(2)
    swarm.start_sync()


# instantiate SmarticleSwarm object with default args
# change/specify USB port!!
swarm = SmarticleSwarm(port=PORT_NAME, debug=1)
swarm.xb.add_rx_callback(rx_callback)
# discover smarticles on network; by default has 15s timeout
swarm.build_network(8)

# initialize square gait
swarm.set_mode(2)
L = [0,180,0,180,0,180,0,180,0,180,0,180,0,180, 90]
R = [0,180,0,180,0,180,0,180,0,180,0,180,0,180, 90]


swarm.gait_init([L,R], 1200,gait_num = 0) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(0)
swarm.gait_init([L,R],567, gait_num = 1) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
# time.sleep(2)
swarm.gait_init([R,R], 533,gait_num = 2) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(2)
swarm.gait_init([L,L],500, gait_num = 3) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
# swarm.init_sync_thread()
swarm.gait_init([L,R], 1200,gait_num = 0) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(0)
swarm.gait_init([L,R],567, gait_num = 1) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
# time.sleep(2)
swarm.gait_init([R,R], 533,gait_num = 2) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(2)
swarm.gait_init([L,L],500, gait_num = 3) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
swarm.gait_init([L,R], 1200,gait_num = 0) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(0)
swarm.gait_init([L,R],567, gait_num = 1) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
# time.sleep(2)
swarm.gait_init([R,R], 533,gait_num = 2) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(2)
swarm.gait_init([L,L],500, gait_num = 3) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
# swarm.init_sync_thread()
swarm.gait_init([L,R], 1200,gait_num = 0) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(0)
swarm.gait_init([L,R],567, gait_num = 1) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms
# time.sleep(2)
swarm.gait_init([R,R], 533,gait_num = 2) #gaits, delay between poitns in ms; I wouldnt go faster than 200m
# time.sleep(2)
swarm.gait_init([L,L],500, gait_num = 3) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms


# swarm.start_sync()
