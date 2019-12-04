# QueuePlank.py
# Alex Samland
# Dec 2, 2019
# Module built for streaming commands to smarticle swarm using a queue


import queue
import threading
import time
from pdb import set_trace as bp

class QueueSPlank(threading.Thread):
    '''Class that for streaming poses to smarticles that are specified by adding
    them to a queue rather than providing a function'''

    def __init__(self,xbee):
        self.xb=xbee
        self.q = queue.Queue()
        super().__init__(target=self.target_function, args=(self.q,), daemon = True)
        self.start()

    def target_function(self,q):
        '''Execute commands on queue until queue is joined'''
        while True:
            [state, remote_device] = q.get()
            if (state==1):
                msg = ':P:1\n'
            else:
                msg = ':P:0\n'
            self.xb.command(msg,remote_device, async = True)
            q.task_done()
