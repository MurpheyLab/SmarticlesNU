#SmarticleReadSensorsExample.py

from modules.SmarticleSwarm import SmarticleSwarm
from random import randint
import time
import numpy as np

# TO DO: change to your port
PORT_NAME = '/dev/ttyUSB0'


def rx_callback(xbee_message):
    '''Simple call_back function to print received packets'''

    print("From {} >> {}".format(xbee_message.remote_device.get_node_id(),
                             xbee_message.data.decode()))


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
swarm.build_network(5)
#change all smarticles to gait interpolate mode
swarm.set_mode(2)
swarm.set_read_sensors(1)
swarm.set_transmit(1)

#send all smarticles the same random gait
n=15
L = [randint(30,60) for x in range(n)]
R = [randint(70,110) for x in range(n)]
swarm.gi([L,R],200) #gaits, delay between poitns in ms; I wouldnt go faster than 200ms

#enable smarticle to read sensors (photo_front, photo_back, microphone)
swarm.set_read_sensors(1)

swarm.set_servos(1)
#enable smarticle to transmit sensor data; I would save this until after initializing everything because it slows things down
swarm.set_transmit(1)
#if you dont want them to be synchronized:
#swarm.set_servos(1) or timed_go(minutes)
