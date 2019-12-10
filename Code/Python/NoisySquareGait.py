# SmarticleSyncExample.py
import sys
sys.path.append('modules')

from SmarticleSwarm import *
from random import randint
import numpy as np

# TO DO: change to your port
PORT_NAME = '/dev/tty.usbserial-DN05LPOA'
# expected number of smarticles to add
num_smarticles = 3


def gait_function(noise_var):
    noise_var = int(noise_var)
    # square gait
    L = [0,180,180,0]
    R = [0,0,180,180]
    # get next step in gait
    ii = gait_function.counter%len(L)
    # add random noise
    gait = [L[ii],R[ii]]+np.random.randint(-noise_var//2,noise_var//2,2)
    # increment counter
    gait_function.counter+=1
    # IMPORTANT: clip resulting values to be between 0 and 180
    return list(np.clip(gait,0,180))

def start_stream():
    stream.run_flag.set()

def pause_stream():
    stream.run_flag.clear()

def timed_go(min):
    '''runs gait interpolation for inputted duration of time'''
    s = int(min*60)
    start_stream()
    print("sleeping for {} minutes...".format(min))
    time.sleep(s)
    stop_stream()




# instantiate SmarticleSwarm object with default args
swarm = SmarticleSwarm(port=PORT_NAME)
# discover smarticles on network; by default has 15s timeout
swarm.build_network(num_smarticles)

# initalize attribute for helper function
gait_function.counter = 0;
# set variance of noise
noise_var = 90
# make lambda function with this variance
gaitf = lambda t: gait_function(noise_var)
# turns on random delay of max 100ms to desynchronize gaits
swarm.set_delay(1,100);


# initialize stream thread
# specify radio, gait function, and streaming period (ms)
stream = StreamThread(swarm.xb,gaitf,450)
stream.run_flag.clear()
stream.start()
swarm.set_mode(1)


# use this to end the streaming thread:
# stream.close()
