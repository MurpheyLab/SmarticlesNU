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
        self.planked_smarticle = None
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
            self.xb.command(msg,remote_device, asynck = True)
            q.task_done()

    def update_action_queue(self,a,smart_ids):
            """
            updates action queue based on input of action vector
            """
            if a[-1] == 1:
                # if smarticles are not already all deplanked
                if self.planked_smarticle is not None:
                    # deplank the planked smarticle
                    self.q.put([0, self.xb.devices[self.planked_smarticle]])
                    self.planked_smarticle = None
                return

            new_plank_smarticle = smart_ids[a.argmax()]

            # if smarticle to plank is arleady planked, do nothing
            if new_plank_smarticle == self.planked_smarticle:
                return
            # if no smarticle is currently planked
            elif self.planked_smarticle is None:
                # plank new smarticle
                self.q.put([1, self.xb.devices[new_plank_smarticle]])
                self.planked_smarticle = new_plank_smarticle
            # if current smarticle needs to be deplanked,
            # and new smarticle needs to be planked
            else:
                # deplank previously planked smarticle
                self.q.put([0,self.xb.devices[self.planked_smarticle]])
                # plank new smarticle
                self.q.put([1, self.xb.devices[new_plank_smarticle]])
                self.planked_smarticle = new_plank_smarticle
