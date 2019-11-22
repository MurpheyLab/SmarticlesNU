#SmarticleSyncExample.py

from modules.SmarticleSwarm import SmarticleSwarm
from modules.StreamThread import StreamThread
from random import randint
import time
import numpy as np
import math

# TO DO: change to your port
PORT_NAME = '/dev/ttyUSB0'


# instantiate SmarticleSwarm object with default args
# change/specify USB port!!
swarm = SmarticleSwarm(port=PORT_NAME)
# discover smarticles on network; by default has 15s timeout
swarm.build_network(3)



# switch to stream mode
swarm.set_mode(1)
# turns on random delay, inputs set min and max on range in ms
swarm.set_delay(1,100);

# stream first pose
devs = list(swarm.xb.devices.values())


for i in np.linspace(80,140,10):
    swarm.stream_pose(i,i,remote_device=devs[0])
    swarm.stream_pose(i,i-50,remote_device=devs[1])
    swarm.stream_pose(i-50,i,remote_device=devs[2])
    time.sleep(0.5)






## to start sync:
# swarm.start_sync()
## or use
# timed_sync(minutes)

#if you dont want them to be synchronized:
#swarm.set_servos(1) or timed_go(minutes)
