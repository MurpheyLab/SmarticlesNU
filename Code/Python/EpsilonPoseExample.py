# SmarticleSyncExample.py
import sys
sys.path.append('pysmarticle')

from SmarticleSwarm import *
from random import randint
import time
import numpy as np
import math

# TO DO: change to your port
PORT_NAME = '/dev/tty.usbserial-DN050I6Q'


def rx_callback(xbee_message):
    '''Simple call_back function to print received packets'''

    print("From {} >> {}".format(xbee_message.remote_device.get_node_id(),
                             xbee_message.data))



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
swarm.set_pose_epsilon(0.1)
