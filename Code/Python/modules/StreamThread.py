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
        self.run_flag = threading.Event()
        self.run_flag.set()
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
        b_stream = bytearray([18]) # Decimal 18, hex 0x12 is stream character
        print('in target function!')
        while not self.exit_flag.is_set() and self.run_flag.wait():
            t0 = time.time()
            t_noise = time_noise()
            gait = [gaitf(t)[0]+32,gaitf(t)[1]+32] #subtract ASCII_OFFSET
            msg = bytearray(gait)+b_stream
            while ((time.time()-t0<period_s+t_noise)):
                pass
            xb.command(msg,remote_device=dev)
            # print(gait)
            t+=period_s
