#  QueueStreaming.py
# Alex Samland
# Nov 24, 2019
# Module built for streaming commands to smarticle swarm using a queue


import queue
import threading
import time
from pdb import set_trace as bp

class QueueStreaming(threading.Thread):
    '''Class that for streaming poses to smarticles that are specified by adding
    them to a queue rather than providing a function'''

    def __init__(self,xbee):
        self.xb=xbee
        self.q = queue.Queue()
        super().__init__(target=self.target_function, args=(self.q,), daemon = True)

    def target_function(self,q):
        '''Execute commands on queue until queue is joined'''
        while True:
            [PosL, PosR, remote_device] = q.get()
            msg = self.xb.format_stream_msg([posL, posR])
            self.xb.command(msg,remote_device)




    def close(self):
        '''Ends operation of Target Function'''
        self.q.join()
