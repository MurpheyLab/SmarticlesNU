# SmarticleSwarm.py
# Alex Samland
# August 13, 2019
# Module for communicating with smarticle swarm over Xbee3s

import time
from modules.XbeeComm import XbeeComm
from modules.StreamThread import StreamThread
import threading


class SmarticleSwarm(object):
    '''
    Class that Utilizies XbeeCom class for performing smarticle operations
    coordinated with Smarticle.h and Smarticle.cpp used on the Smarticle microcontrollers
    '''

    GI_LENGTH = 15
    ASCII_OFFSET = 32

    def __init__(self, port='/dev/tty.usbserial-DN050I6Q', baud_rate = 9600, debug = 1,servo_period_ms=0):
        '''
        Initalizes and opens local base xbee (connected via USB) with given port and baud rate and adds it to attribute `base`

        *Arguments*
        | Argument            | Type     | Description                                | Default Value                       |
        | :------:            | :--:     | :---------:                                | :-----------:                       |
        | port                | `string` | USB port to open for local XBee            | please set for your own convenience |
        | baud_rate           | `int`    | Baud rate to use for USB serial port       | 9600                                |
        | debug               | `int`    | Enables/disables print statements in class | 1                                   |
        | servo_period_ms     | `int`    | Servo Stream period for thread in ms       | 0                                   |

        *Returns*
        void
        '''
        self.xb = XbeeComm(port,baud_rate,debug)
        self.servo_period_s = servo_period_ms*0.001
        self.lock = threading.Lock()


    def build_network(self, exp_no_smarticles=None):
        '''
        Clears `devices` dictionary as well as all devices on network.
        Discovers remote devices on network, initializes dictionary of all connected devices.
        Will ask for retries if expected no of smarticles is not discovered
        modified from Digi XBee example DiscoverDevicesSample.py

        *Arguments*
        | Argument                        | Type     | Description                                | Default Value    |
        | :------:                        | :--:     | :---------:                                | :-----------:    |
        | exp_no_smarticles               | `int`    | Expected number of smarticles to discover  | None             |

        *Returns*
        void
        '''
        self.xb.discover()
        if exp_no_smarticles != None:
            if (len(self.xb.devices))<exp_no_smarticles:
                inp= input('Failed to discover all {} expected Smarticles. Retry discovery (Y/N)\n'.format(exp_no_smarticles))
                if inp[0].upper()=='Y':
                    self.build_network(exp_no_smarticles)
                else:
                    #purge Smarticle Xbee buffer
                    time.sleep(0.5)
                    self.xb.broadcast('\n')
                    time.sleep(0.5)
                    print('Network Discovery Ended\n')



    def set_servos(self, state, remote_device = None):
        '''
        Enables/disables updating of servos. When enabled it also resets the gait interpolation sequence back to its first initial point
        When set_servos ==0, servos can still be controlled using set_pose()

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `bool`                                         | Value: 1 or 0. enables/disables updating servos in timer interrupt       | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above | `None`         |

        *Returns*
        void
        '''
        if (state==True):
            msg = ':S:1\n'
        else:
            msg = ':S:0\n'
        self.xb.command(msg, remote_device)


    def set_transmit(self, state, remote_device = None):
        '''
        Enables/disables smarticle transmitting data.
        Data sent in following format: '{int Phot_front}, {int photo_back}, {int mic}'(values between 0-1023)

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `bool`                                         | Value: 1 or 0. enables/disables transmitting Data                        | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above | `None`         |

        *remote_device*
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Returns*
        void
        '''
        if (state==1):
            msg = ':T:1\n'
        else:
            msg = ':T:0\n'
        self.xb.command(msg, remote_device)


    def set_read_sensors(self, state, remote_device = None):
        '''
        Enables/disables smarticle reading sensors

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `bool`                                         | Value: 1 or 0. enables/disables reading sensors                          | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above | `None`         |

        *remote_device*
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Returns*
        void
        '''
        if (state==True):
            msg = ':R:1\n'
        else:
            msg = ':R:0\n'
        self.xb.command(msg, remote_device)

    def set_mode(self, state, remote_device = None):
        '''
        Changes operating mode of smarticle(s)

        *States*
        | Value | Mode             | Description                                                      |
        | :---: | :--:             | :---------:                                                      |
        | 0     | Idle             | Smarticle does nothing. Servos detach and no data is transmitted |
        | 1     | Stream servos    | Servo points streamed (still in development)                     |
        | 2     | Gait interpolate | Iterate through interpolated points sent to smarticle            |

        *remote_device*
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Arguments*
        | Argument        | Type                                          | Description                                                                | Default Value  |
        | :------:        | :--:                                          | :---------:                                                                | :-----------:  |
        | state           | `int`                                         | Values: 0-2. 0: inactive, 1: stream servo (unfinished), 2:gait interpolate | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        void
        '''
        assert (state>=0 and state<=2),"Mode must between 0-2"
        msg = ':M:{}\n'.format(int(state))
        self.xb.command(msg, remote_device)

    def set_plank(self, state, remote_device = None):
        '''
        Sets smarticle to plank or deplank Note: only active when set_servos  == 1

        *remote_device*
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Arguments*
        | Argument        | Type                                          | Description                                                                | Default Value  |
        | :------:        | :--:                                          | :---------:                                                                | :-----------:  |
        | state           | `bool`                                         | Values: 0,1. 0: deplank 1: plank                                           | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        void
        '''
        if (state==True):
            msg = ':P:1\n'
        else:
            msg = ':P:0\n'
        self.xb.command(msg, remote_device)

    def set_pose(self, posL, posR, remote_device = None):
        '''
        Sets smarticle to specified servo positions

        *remote_device*
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Arguments*
        | Argument        | Type                                          | Description                                                                | Default Value  |
        | :------:        | :--:                                          | :---------:                                                                | :-----------:  |
        | posL            | `int`                                         | Left servo angle: 0-180 deg                                                | N/A            |
        | posR            | `int`                                         | Right servo angle: 0-180 deg                                               | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        void
        '''
        msg=':SP:{},{}\n'.format(int(posL),int(posR))
        self.xb.command(msg, remote_device)

    def set_delay(self, state=-1, max_val=-1, remote_device = None):
        '''
        Enables/disables random delay in stream servo mode for smarticles.
        Writing  value of negative  one (-1) leaves that  field as is on the smarticle

        *remote_device*
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Arguments*
        | Argument        | Type                                          | Description                                                                | Default Value  |
        | :------:        | :--:                                          | :---------:                                                                | :-----------:  |
        | state           | `int`                                         | Values: 0,1 see note about negative values above                           | -1             |
        | max_val         | `int`                                         | Maximum value of random delay                                              | -1             |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        void
        '''
        msg=':SD:{},{}\n'.format(int(state),int(max_val))
        self.xb.command(msg, remote_device)


    def gait_init(self, gait, delay_ms=250, remote_device = None):
        '''
        Sends gait interpolation data to remote smarticles including:
            1. left and right servo interpolation points (max 15 points each)
            2. data length
            3. period between interpolation points

        *gait*
        Lists of two lists: gaitLpoints and gaitRpoints. These lists must be equal in length and contain at most 15 points

        *remote_device*
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Arguments*
        | Argument        | Type                                          | Description                                                                | Default Value  |
        | :------:        | :--:                                          | :---------:                                                                | :-----------:  |
        | gait            | list of lists of int                          | [gaitLpoints, gaitRpoints]                                                 | N/A            |
        | period_ms       | `int`                                         | period (ms) between gait points                                            | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        void
        '''
        self.delay_ms = delay_ms
        timer_counts = int(delay_ms/0.128)
        gaitL=gait[0]
        gaitR=gait[1]
        gaitL = [int(x+self.ASCII_OFFSET) for x in gaitL]
        gaitR = [int(x+self.ASCII_OFFSET) for x in gaitR]
        assert len(gaitL)==len(gaitR),'Gait lists must be same length'
        gait_points = len(gaitL)
        if gait_points != self.GI_LENGTH:
            while len(gaitL)!=self.GI_LENGTH:
                gaitL.append(self.ASCII_OFFSET)
                gaitR.append(self.ASCII_OFFSET)
        str = ':GI:{:02},'.format(gait_points)
        b_str = bytearray(str,'utf-8')
        b_delay = bytearray(timer_counts.to_bytes(2,'big'))+bytearray(';','utf-8')
        msg=  b_str+b_delay+bytearray(gaitL)+bytearray(gaitR)+bytearray('\n','utf-8')
        self.xb.command(msg, remote_device)
        time.sleep(0.1) #ensure messages are not dropped as buffer isn't implemented yet

    def sync_signal(self):
        '''
        Broadcasts sync signal '0x11' to maintain synchronization
        '''
        msg = bytearray(b'\x11')
        t = time.time()
        self.xb.broadcast(msg)
        print("sync! {}\n".format(t))

    def sync_thread_target(self,sync_period_s):
        '''
        Thread to keep gaits in sync
        '''
        time_adjust_s=sync_period_s-0.035 #subtract 35ms based on results from timing experiments
        msg = bytearray(b'\x11')
        #threading.event.wait() blocks until it is a) set and then returns True or b) the specified timeout elapses in which it retrusn nothing
        while self.sync_flag.wait() and not self.timer_counts.wait(timeout=(time_adjust_s)):
                self.xb.broadcast(msg)


    def init_sync_thread(self):
        '''Initializes gait sync thread. Must be called every time the gait sequence is updated'''
        # calculate sync period: approximately 3s but must be a multiple of the gait delay
        self.sync_period_s = int((max(3000//self.delay_ms,1))*self.delay_ms)/1000
        self.sync_thread = threading.Thread(target=self.sync_thread_target, args= (self.sync_period_s,),  daemon = True)
        self.timer_counts = threading.Event()
        self.sync_flag = threading.Event()
        self.sync_thread.start()

    def start_sync(self):
        '''starts gait sequence and sync thread'''
        delay_t = self.delay_ms/3000
        #starts gait sequence
        self.set_servos(1)
        #wait 1/3 of gait delay to begin sync sequene
        time.sleep(delay_t)
        #set sync flag so that it returns True and stops blocking
        self.sync_flag.set()

    def stop_sync(self):
        '''stops gait sequence and pauses gait sync thread'''
        #stop gait sequence
        self.set_servos(0)
        #cause sync_flag.wait() to block
        self.sync_flag.clear()


##Still being developed;
    # def servo_thread_target(self, gaitf):
    #     '''DOC'''
    #
    #     t = 0
    #     self.lock.acquire()
    #     while self.run_servos:
    #         self.lock.release()
    #         t0 = time.time()
    #         self.xb.broadcast('{}\n'.format(int(gaitf(t))))
    #         t += self.servo_period_s
    #         while ((time.time()-t0)<self.servo_period_s):
    #             time.sleep(0.001)
    #         self.lock.acquire()
    #     self.lock.release()
    #
    # def init_servo_thread(self, gait_fun=None):
    #     '''DOC: initializes servo thread'''
    #     self.servo_thread = threading.Thread(target=self.servo_thread_target, args= (gait_fun,), daemon = True)
    #
    #
    # def start_servo_thread(self):
    #     '''DOC'''
    #     with self.lock:
    #         self.run_servos = 1
    #     self.servo_thread.start()
    #
    # def stop_servo_thread(self):
    #     '''DOC'''
    #     with self.lock:
    #         self.run_servos = 0
