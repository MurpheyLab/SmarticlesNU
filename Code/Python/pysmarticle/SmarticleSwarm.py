# SmarticleSwarm.py
# Alex Samland
# August 13, 2019
# Module for communicating with smarticle swarm over Xbee3s

import time
from .XbeeComm import XbeeComm
from .StreamThread import StreamThread
import threading
import numpy as np


class SmarticleSwarm(object):
    '''
    Class that Utilizies XbeeComm class for performing smarticle operations
    coordinated with Smarticle.h and Smarticle.cpp used on the Smarticle microcontrollers
    '''
    msg_code_dict = {'toggle_led': 0x20, 'set_mode': 0x21, 'toggle_t4_interrupt': 0x22,\
        'set_transmit_counts': 0x23, 'select_gait': 0x24, 'toggle_read_sensors': 0x25,\
        'toggle_transmit': 0x26, 'set_gait_epsilon': 0x27, 'set_pose_noise': 0x28,\
        'toggle_light_plank': 0x29, 'set_debug': 0x2A, 'set_id': 0x2B, 'set_pose': 0x30,\
        'set_sync_noise': 0x31, 'set_stream_timing_noise': 0x32,\
        'set_light_plank_threshold': 0x40, 'init_gait': 0x41, 'stream_pose': 0x42, 'set_plank': 0x43}
    msg_prefix = bytearray([0x13,0x13])
    msg_end = bytearray([0x0A])

    ASCII_OFFSET = 32
    SAMPLE_TIME_MS = 10

    def __init__(self, port='/dev/tty.usbserial-DN050I6Q', baud_rate = 9600, debug = 0):
        '''
        Initalizes and opens local base xbee (connected via USB) with given port and baud rate and adds it to attribute `base`

        **Arguments**

        | Argument            | Type       | Description                                | Default Value                       |
        | :------             | :--        | :---------                                 | :-----------                        |
        | port                | `string`   | USB port to open for local XBee            | set for your own convenience        |
        | baud_rate           | `int`      | Baud rate to use for USB serial port       | 9600                                |
        | debug               | `int`      | Enables/disables print statements in class | 0                                   |
        |<img width=250/>|<img width=250/>|<img width=1000/>|<img width=700/>|

        **Returns**
        `None`
        '''
        self.xb = XbeeComm(port,baud_rate,debug)
        self.lock = threading.Lock()

    @classmethod
    def format_msg(self, msg):
        return self.msg_prefix+msg+self.msg_end

    @classmethod
    def convert_to_2_chars(self, val):
        val = val&0x3ffff
        c1 = (val>>7)+self.ASCII_OFFSET
        c2 = (val&0x7f)+self.ASCII_OFFSET
        return [c1,c2]


    def build_network(self, exp_n_smarticles=None):
        '''
        Clears `devices` dictionary as well as all devices on network.
        Discovers remote devices on network, initializes dictionary of all connected devices.
        Will ask for retries if expected no of smarticles is not discovered
        modified from Digi XBee example DiscoverDevicesSample.py

        *Arguments*
        | Argument                        | Type     | Description                                | Default Value    |
        | :------:                        | :--:     | :---------:                                | :-----------:    |
        | exp_n_smarticles               | `int`    | Expected number of smarticles to discover  | None             |

        *Returns*
        `None`
        '''
        self.xb.discover()
        if exp_n_smarticles != None:
            if (len(self.xb.devices))<exp_n_smarticles:
                inp= input('Only discovered {} out of {} expected Smarticles. Retry discovery (Y/N)\n'.format(len(self.xb.devices),exp_n_smarticles))
                if inp[0].upper()=='Y':
                    self.build_network(exp_n_smarticles)
                else:
                    #purge Smarticle Xbee buffer
                    time.sleep(0.5)
                    self.xb.broadcast('\n')
                    time.sleep(0.5)
                    print('Network Discovery Ended\n')
            else:
                #purge Smarticle Xbee buffer
                print('Successfully discovered {} out of {} expected Smarticles\n'.format(len(self.xb.devices),exp_n_smarticles))
                time.sleep(0.5)
                self.xb.broadcast('\n')
                time.sleep(0.5)
                print('Network Discovery Ended\n')
        else:
            #purge Smarticle Xbee buffer
            time.sleep(0.5)
            self.xb.broadcast('\n')
            time.sleep(0.5)
            print('Network Discovery Ended\n')

    def send_ids(self,asynch=False):
        '''
        Sends IDs to smarticles

        *Arguments*
        | Argument        | Type                      | Description                                                                   | Default Value |
        | :------:        | :--:                      | :---------:                                                                   | :-----------: |
        | asynch           | `bool`                    | Determines whether to send asynchronously (without ack) or not                | False         |

        *Returns*
        void
        '''
        msg_code = self.msg_code_dict['set_id']
        for id in self.xb.devices.keys():
            msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+id]))
            self.xb.send(self.xb.devices[id],msg,asynch=False)


    def close(self):
        '''closes serial connection to XBee'''
        self.xb.close_base()




    def set_servos(self, state, remote_device = None):
        '''
        Enables/disables updating of servos. When enabled it also resets the gait interpolation sequence back to its first initial point
        When set_servos ==0, servos can still be controlled using set_pose()

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `int`                                         | Value: 1 or 0. enables/disables updating servos in timer interrupt       | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above | `None`         |

        *Returns*
        `None`
        '''
        msg_code = self.msg_code_dict['toggle_t4_interrupt']
        if state != 1:
            state = 0
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+state]))
        self.xb.command(msg, remote_device)


    def set_transmit(self, state, remote_device = None):
        '''
        Enables/disables smarticle transmitting data.
        Data sent in following format: '{int Photo_front}, {int photo_back}, {int photo_right} {int current_sense}'(values between 0-1023)

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `int`                                         | Value: 1 or 0. enables/disables transmitting Data                        | N/A            |
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
        `None`
        '''
        msg_code = self.msg_code_dict['toggle_transmit']
        if state != 1:
            state = 0
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+state]))
        self.xb.command(msg, remote_device)

    def set_light_plank(self, state, remote_device = None):
        '''
        Enables/Disables light plank (i.e. smarticles planking when light sensors are above set threshold)

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `bool`                                         | Value: 1 or 0. enables/disables light planking                          | N/A            |
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
        `None`
        '''

        msg_code = self.msg_code_dict['toggle_light_plank']
        if state != 1:
            state = 0
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+state]))
        self.xb.command(msg, remote_device)

    def set_sensor_threshold(self, thresh, remote_device = None):
        '''
        Sets sensor threshold that triggers planking

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | thresh          | `list of int`                                 | Threshold values for PR_front, PR_back, PR_right, current sense          | N/A            |
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
        `None`
        '''
        assert len(thresh)==4, 'Threshold list must be 4 elements'
        msg_code = self.msg_code_dict['set_light_plank_threshold']
        val = bytearray()
        for t in thresh:
            val+= self.convert_to_2_chars(t)
        msg = self.format_msg(bytearray([msg_code]+val))
        self.xb.command(msg, remote_device)



    def set_read_sensors(self, state, remote_device = None):
        '''
        Enables/disables smarticle reading sensors

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | state           | `int`                                        | Value: 1 or 0. enables/disables reading sensors                          | N/A            |
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
        `None`
        '''
        msg_code = self.msg_code_dict['toggle_read_sensors']
        if state != 1:
            state = 0
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+state]))
        self.xb.command(msg, remote_device)

    def set_transmit_period(self, period_ms, remote_device=None):
        '''
        Sets approximate data transmit period of smarticles

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | period_ms       | `int`                                         |  transmit period in ms. Max value of 2000s                               | N/A            |
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
        `None`
        '''
        msg_code = self.msg_code_dict['set_transmit_counts']
        counts = period_ms//self.SAMPLE_TIME_MS
        counts = np.clip(counts, 1, 200)
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+counts]))
        self.xb.command(msg, remote_device)



    def set_debug(self, state, remote_device=None):
        '''
        Sets debug level of smarticle

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | debug          | `int`                                        | Value: 0,1,2. Sets level of debug output. 0 is no output, 1 is limited output, 2 is full output | N/A            |
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
        `None`
        '''
        msg_code = self.msg_code_dict['set_debug']
        if state not in [0,1,2]:
            state = 0
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+state]))
        self.xb.command(msg, remote_device)



    def set_pose_epsilon(self, eps, remote_device = None):
        '''
        Sets epsilon value for smarticle poses. The smarticle will move the arm
        randomly propoportional to epsilon (0-1). For example, if epsilon is 0.1,
        the smarticle will move its arm to a random angle 10% of the time

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value  |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:  |
        | eps             | 'float'                                       | Value: 0-1, determines proportion of random arm movements                | N/A            |
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
        `None`
        '''
        # ensure eps is between 0 and 1
        eps = 100*round(np.clip(eps,0,1),2)
        msg_code = self.msg_code_dict['toggle_light_plank']
        if state != 1:
            state = 0
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+eps]))
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
        `None`
        '''
        assert (state>=0 and state<=2),"Mode must between 0-2"
        msg_code = self.msg_code_dict['set_mode']
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+state]))
        self.xb.command(msg, remote_device)

    def set_plank(self, state_arr, remote_device = None):
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
        `None`
        '''
        msg_code = self.msg_code_dict['set_plank']
        l = len(state_arr)+self.ASCII_OFFSET
        state_arr = list((state_arr+self.ASCII_OFFSET).flatten())
        msg = self.format_msg(bytearray([msg_code,l]+state_arr))
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
        `None`
        '''
        msg_code = self.msg_code_dict['set_pose']
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+posL,self.ASCII_OFFSET+posR]))
        self.xb.command(msg, remote_device)

    def stream_pose(self, poses, remote_device=None):
        '''
        Sets smarticle to specified servo positions. Differs from set_pose in
        that it sends angles over the streaming pipeline, which sends a batch message that can specify 
        separate commands for each smarticle in the same message. Specify id as zero to broadcast servo command to whole swarm.

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
        | poses            | `np.array`                                   | Nx3 array of servo commands. Each row specifies [id, angL, angR]     | N/A            |

        *Returns*
        `None`
        '''
        msg_code = self.msg_code_dict['stream_pose']
        l = len(poses)+self.ASCII_OFFSET
        poses = list((poses+self.ASCII_OFFSET).flatten())
        msg = self.format_msg(bytearray([msg_code,l]+poses))
        self.xb.command(msg,remote_device)


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
        `None`
        '''
        msg=':SD:{},{}\n'.format(int(state),int(max_val))
        self.xb.command(msg, remote_device)


    def set_pose_noise(self, max_val, remote_device = None):
        '''
        Sets noise on servo positions (noisy arm angles)

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
        | max_val         | `int`                                         | Maximum value of random noise                                              | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        `None`
        '''
        assert max_val < 100, 'value must be less than 100'
        val=int(2*max_val)
        msg_code = self.msg_code_dict['set_pose_noise']
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+val]))
        self.xb.command(msg, remote_device)


    def set_sync_noise(self, max_val, remote_device = None):
        '''
        Sets noise on synchronization time for gait interp mode

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
        | max_val         | `int`                                         | Maximum value of random delay                                              | N/A            |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above   | `None`         |

        *Returns*
        `None`
        '''
        timer_counts = self.convert_to_2_chars(int(max_val/0.128))
        msg_code = self.msg_code_dict['set_sync_noise']
        msg = self.format_msg(bytearray([msg_code]+timer_counts))
        self.xb.command(msg, remote_device)


    def gait_init(self, gait, delay_ms, gait_num=0, remote_device = None):
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
        `None`
        '''
        msg_code = bytearray([self.msg_code_dict['init_gait']])
        self.delay_ms = delay_ms
        self.gait_len = len(gait[0])
        timer_counts = int(delay_ms/0.128)
        gaitL=gait[0]
        gaitR=gait[1]
        gaitL = [int(x+self.ASCII_OFFSET) for x in gaitL]
        gaitR = [int(x+self.ASCII_OFFSET) for x in gaitR]
        assert len(gaitL)==len(gaitR),'Gait lists must be same length'
        gait_points = self.gait_len+self.ASCII_OFFSET
        n = gait_num +self.ASCII_OFFSET
        delay = self.convert_to_2_chars(timer_counts)
        msg=  self.format_msg(msg_code+bytearray([n, gait_points]+delay+gaitL+gaitR))
        self.xb.command(msg, remote_device)
        time.sleep(0.1) #ensure messages are not dropped as buffer isn't implemented yet

    def select_gait(self, n, remote_device = None):
        '''
        DOC
        '''
        msg_code = self.msg_code_dict['select_gait']
        msg = self.format_msg(bytearray([msg_code,self.ASCII_OFFSET+n]))
        self.xb.command(msg, remote_device)


    def sync_thread_target(self,sync_period_s, keep_time):
        '''
        Thread to keep gaits in sync
        '''
        time_adjust_s=sync_period_s-0.0357 #subtract 35ms based on results from timing experiments
        msg = bytearray(b'\x11')
        #threading.event.wait() blocks until it is a) set and then returns True or b) the specified timeout elapses in which it retrusn nothing
        while self.sync_flag.wait() and not self.timer_counts.wait(timeout=(time_adjust_s)):
                self.xb.broadcast(msg)
                if keep_time:
                    t = time.time()
                    with self.lock:
                        self.sync_time_list.append(t)



    def init_sync_thread(self, keep_time=False):
        '''Initializes gait sync thread. Must be called every time the gait sequence is updated'''
        # calculate sync period: approximately 3s but must be a multiple of the gait delay
        self.sync_period_s = (self.gait_len*self.delay_ms)/1000
        print('sync_period: {}'.format(self.sync_period_s))
        if keep_time:
            self.sync_time_list =[]
        self.sync_thread = threading.Thread(target=self.sync_thread_target, args= (self.sync_period_s,keep_time),  daemon = True)
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
