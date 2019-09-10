#SmarticleSyncExample.py

from modules.SmarticleSwarm import SmarticleSwarm
from random import randint
import time
import numpy as np

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


#instantiate SmarticleSwarm object with default args
#change/specify USB port!!
swarm = SmarticleSwarm(port=PORT_NAME)
swarm.xb.add_rx_callback(rx_callback)
#discover smarticles on network; by default has 15s timeout
swarm.build_network(1)
