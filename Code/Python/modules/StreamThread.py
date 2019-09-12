#  StreamThread.py
# Alex Samland
# August 30, 2019
# Module built for SmarticleSwarm class for streaming servo commands

import threading
import time

class StreamThread(threading.Thread):

    def __init__(self,xbee,gait_f, period_ms, remote_device= None, time_noise= None):
        if time_noise == None:
            self.time_noise = lambda: 0
        self.xb=xbee
        self.thread_flag = threading.Event()
        self.exit_flag = threading.Event()
        self.exit_flag.clear()
        self.period_s = round(period_ms/1000,3)
        self.gait=gait_f
        self.dev = remote_device
        super().__init__(target=self.target_function, args=(self.gait, self.period_s, self.dev, self.xb, self.time_noise), daemon = True)

    def kill(self):
        self.exit_flag.set()

    def target_function(self,gaitf,period_s,dev,xb,time_noise):
        t=0
        while self.exit_flag.is_set() and self.thread_flag.wait():
            t0 = time.time()
            t_noise = time_noise()
            gait = gaitf(t)-[32,32] #subtract ASCII_OFFSET
            msg = bytearray(gait)+bytearray(0x12)
            while ((time.time()-t0<period_s+t_noise)):
                pass
            xb.broadcast(msg,remote_device=dev)
            t+=period_s
