# SmarticleSwarm.py
# Alex Samland
# August 13, 2019
# Module for communicating with smarticle swarm over Xbee3s

import time
from XbeeComm import XbeeComm
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
                    print('Network Discovery Ended\n')



    def set_servos(self, state, remote_device = None):
        '''
        Enables/disables updating of servos.
        When set_servos ==0, servos can still be controlled using set_pose()

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `int`                                         | Value: 1 or 0. enables/disables updating servos in timer interrupt       | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above | `None`         |

        *Returns*
        void
        '''
        if (state==1):
            msg = ':S:1\n'
        else:
            msg = ':S:0\n'
        self.xb.command(msg, remote_device)


    def set_transmit(self, state, remote_device = None):
        '''DOC'''
        if (state==1):
            msg = ':T:1\n'
        else:
            msg = ':T:0\n'
        self.xb.command(msg, remote_device)

    def set_mode(self, state, remote_device = None):
        '''
        Changes operating mode of smarticle(s)

        *States*
        | Value | Mode             | Description                                                      |
        | :---: | :--:             | :---------:                                                      |
        | 0     | Inactive         | Smarticle does nothing. Servos detach and no data is transmitted |
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
        | state           | `int`                                         | Values: 0,1. 0: deplank 1: plank                                           | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        void
        '''
        if (state==1):
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


    def gi(self, gait, period_ms=250, remote_device = None):
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
        str = ':GI:{:02},{:04};'.format(gait_points,period_ms)
        b_str = bytearray(str,'utf-8')
        msg=  b_str+bytearray(gaitL)+bytearray(gaitR)+bytearray('\n','utf-8')
        self.xb.command(msg, remote_device)
        time.sleep(0.1) #ensure messages are not dropped as buffer isn't implemented yet

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
