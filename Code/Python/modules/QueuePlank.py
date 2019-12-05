# QueuePlank.py
# Alex Samland
# Dec 2, 2019
# Module built for streaming commands to smarticle swarm using a queue


import queue
import threading
import time
from pdb import set_trace as bp

class QueuePlank(threading.Thread):
    '''Class that for streaming poses to smarticles that are specified by adding
    them to a queue rather than providing a function'''

    def __init__(self,xbee):
        self.xb=xbee
        self.q = queue.Queue()
        self.plank_smarticle = None
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

    def update_action_queue(self,a):
            """
            updates action queue based on input of action vector
            """
            amax = a.argmax()
            devs = list(self.xb.devices.values())
            # if action is to deplank all smarticles
            if a[-1] == 1:
                # if smarticles are not already all deplanked
                if self.plank_smarticle is not None:
                    # deplank the planked smarticle
                    self.q.put([0, devs[self.plank_smarticle]])
                    self.plank_smarticle = None
            # if smarticle to plank is arleady planked, do nothing
            elif amax == self.plank_smarticle:
                return
            # if no smarticle is currently planked
            elif self.plank_smarticle is None:
                # plank new smarticle
                self.q.put([1, devs[amax]])
                self.plank_smarticle = amax
            # if current smarticle needs to be deplanked,
            # and new smarticle needs to be planked
            else:
                # deplank previously planked smarticle
                self.q.put([0,devs[self.plank_smarticle]])
                # plank new smarticle
                self.q.put([1, devs[amax]])
                self.plank_smarticle = amax
