#  StreamServo.py
# Alex Samland
# August 30, 2019
# Module built for SmarticleSwarm class for streaming servo commands

import threading
import time

class StreamServo(Thread):

    def __init__(self,xbee,gait_f, frequency = 30, remote_device= None):
        self.dev = remote_device
        self.f=frequency
        self.period_s = round(1/frequency,3)
        self.gait=gait_f
        self.xb=xbee
        self.thread_flag = threading.event()

    def initialize(self):
        super().__init__(target=self.target_function, args = (self.gait,self.period_s,self.dev), daemon = True)
        self.event()

    def self.target_function(self,gaitf,period_s,dev):
        t=0
        while self.thread_flag.wait():
            t0 = time.time()
            gait = gaitf(t)-[32,32] #subtract ASCII_OFFSET
            msg = bytearray(gait)+bytearray(0x12)
            whiile ((time.time()-t0):
                pass
            self.xb.broadcast(msg,remote_device=dev)
            t+=period_s
