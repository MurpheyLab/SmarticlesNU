#SmarticleSyncExample.py

from modules.SmarticleSwarm import SmarticleSwarm
from modules.StreamThread import StreamThread
from random import randint
import time
import numpy as np
import math

# TO DO: change to your port
PORT_NAME = '/dev/tty.usbserial-DN050I6Q'


# instantiate SmarticleSwarm object with default args
# change/specify USB port!!
swarm = SmarticleSwarm(port=PORT_NAME)
# discover smarticles on network; by default has 15s timeout
swarm.build_network(8)



# switch to stream mode
swarm.set_mode(1)
# turns on random delay, inputs set min and max on range in ms
swarm.set_delay(1,100);
# stream first pose
swarm.stream_pose(75,75)






## to start sync:
# swarm.start_sync()
## or use
# timed_sync(minutes)

#if you dont want them to be synchronized:
#swarm.set_servos(1) or timed_go(minutes)
