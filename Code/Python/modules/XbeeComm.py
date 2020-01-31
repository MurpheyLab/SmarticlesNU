# XbeeComm.py
# Alex Samland
# August 1, 2019
# Module for communicating with smarticle swarm over Xbee3s

import time
import numpy as np
from digi.xbee.models.status import NetworkDiscoveryStatus
from digi.xbee.devices import Raw802Device

default_port = '/dev/tty.usbserial-DN050I6Q'

class XbeeComm(object):
    ''''Class for simplified XBee communication with remote Smarticles
        Built on top of Digi XBee python library:
            https://github.com/digidotcom/xbee-python'''


    def __init__(self, port='/dev/tty.usbserial-DN050I6Q', baud_rate = 9600, debug = 0):
        '''
        Initalizes and opens local base xbee (connected via USB) with given port and baud rate and adds it to attribute `base`

        *Arguments*
        | Argument  | Type     | Description                                | Default Value                       |
        | :------:  | :--:     | :---------:                                | :-----------:                       |
        | port      | `string` | USB port to open for local XBee            | please set for your own convenience |
        | baud_rate | `int`    | Baud rate to use for USB serial port       | 9600                                |
        | debug     | `int`    | Enables/disables print statements in class | 0                                   |

        *Returns*
        void
        '''

        self.base = Raw802Device(port, baud_rate)
        self.debug = debug
        self.open_base()
        self.callbacks_added = False
        self.ascii_offset = 32


    def open_base(self):
        '''
        Opens local xbee defined by attribute 'base' which is set in `__init__`

        *Arguments*
        None

        *Returns*
        This function returns a 1 if it successfully opens the local port and a 0 otherwise.
        '''
        success = 0
        self.base.open()
        if self.base is not None and self.base.is_open():
            success = 1
        elif self.debug:
            print("Failed to open device")
        return success

    def close_base(self):
        '''
        Closes local xbee defined by attribute 'base' which is set in `__init__`

        *Arguments*
        None

        *Returns*
        void
        '''
        if self.base is not None and self.base.is_open():
            self.base.close()

    def add_callbacks(self):
        '''adds callback functions for discovery processess'''
        # Callback for discovered devices.
        def callback_device_discovered(remote):
            print("Device discovered: %s" % remote)
            self.add_remote(remote)

        # Callback for discovery finished.
        def callback_discovery_finished(status):
            if status == NetworkDiscoveryStatus.SUCCESS:
                # print("Discovery process finished successfully.\nDevices: {}".format(self.devices))
                print("Discovery cycle finished\n")
            else:
                print("There was an error discovering devices: %s" % status.description)

        self.network.add_device_discovered_callback(callback_device_discovered)

        self.network.add_discovery_process_finished_callback(callback_discovery_finished)


    def add_remote(self,remote_device):
        '''
        takes in RemoteXbee Object and creates an attribute for it based on its NodeID and adds it to the device dictionary

        *Arguments*
        | Argument        | Type                      | Description                                                                   | Default Value |
        | :------:        | :--:                      | :---------:                                                                   | :-----------: |
        | remote_device   | `RemoteXbeeDevice` Object | Stores info such as ID and address; see Digi Xbee Documentation for more info | N/A           |

        *Returns*
        void

        More info on RemoteXbeeDevice:
        https://xbplib.readthedocs.io/en/stable/api/digi.xbee.devices.html#digi.xbee.devices.RemoteXBeeDevice
        '''
        smarticle_number = int(''.join([s for s in remote_device.get_node_id() if s.isdigit()]))
        setattr(self,remote_device.get_node_id(),remote_device)
        self.devices[smarticle_number]=remote_device


    def discover(self):
        '''
        Clears `devices` dictionary as well as all devices on network.
        Discovers remote devices on network, initializes dictionary of all connected devices.
        modified from Digi XBee example DiscoverDevicesSample.py

        *Arguments*
        None

        *Returns*
        void
        '''
        self.devices ={}
        self.network = self.base.get_network()
        self.network.clear()
        self.network.set_discovery_timeout(15)  # 15 seconds.

        if self.callbacks_added == False:
            self.add_callbacks()
            self.callbacks_added = True

        self.network.start_discovery_process()
        print("Discovering remote XBee devices...")

        while self.network.is_discovery_running():
            time.sleep(0.1)


    def send(self, remote_device, msg, asynck = False):
        '''
        Sends message to remote xbee and receives acknowledgement on sucess.
        modified from digi's example SendDataSample.py

        *Arguments*
        | Argument        | Type                      | Description                                                                   | Default Value |
        | :------:        | :--:                      | :---------:                                                                   | :-----------: |
        | remote_device   | `RemoteXbeeDevice` Object | Stores info such as ID and address; see Digi Xbee Documentation for more info | N/A           |
        | msg             | `string` or `bytearray`   | Message to send to XBee. Maximum of 108 bytes                                 | N/A           |
        | async           | `bool`                    | Determines whether to send asynchronously (without ack) or not                | False         |

        *Returns*
        void

        More info on RemoteXbeeDevice:
        https://xbplib.readthedocs.io/en/stable/api/digi.xbee.devices.html#digi.xbee.devices.RemoteXBeeDevice
        '''

        if remote_device is None:
            if self.debug():
                print("Could not find the remote device")
            exit(1)
        if self.debug:
            print("Sending data to {} >> {}...".format(remote_device.get_node_id(), msg))

        if asynck is True:
            self.base.send_data_async(remote_device, msg)
        else:
            self.base.send_data(remote_device, msg)

            if self.debug:
                print("Success")


    def format_stream_msg(self, pose):
        '''
        takes in list of arm angles and returns string in form of stream command
        to be sent to Smarticle in stream mode

        *Arguments*
        | Argument  | Type                  | Description                | Default Value |
        | :------:  | :--:                  | :---------:                | :-----------: |
        | pose      | 2 element list of int | pose angles to set arms to | N/A           |

        *Returns*
        void

        More info on RemoteXbeeDevice:
        https://xbplib.readthedocs.io/en/stable/api/digi.xbee.devices.html#digi.xbee.devices.RemoteXBeeDevice
        '''
        pose = [int(pose[0]), int(pose[1])]
        pose = np.clip(pose, 0, 254-self.ascii_offset) + self.ascii_offset #clip values outside of 0-180 and add ASCII_OFFSET
        b_stream = bytearray([18]) # Decimal 18, hex 0x12 is stream character
        msg = bytearray(list(pose))+b_stream

        return msg


    def broadcast(self, msg):
        '''
        Broadcasts to all xbees on network. NOTE: there are no acknowledgements when using broadcast

        *Arguments*
        | Argument        | Type                      | Description                                                                   | Default Value |
        | :------:        | :--:                      | :---------:                                                                   | :-----------: |
        | msg             | `string` or `bytearray`   | Message to send to XBee. Maximum of 108 bytes                                 | N/A           |

        *Returns*
        void
        '''
        self.base.send_data_broadcast(msg)


    def ack_broadcast(self,msg):
        '''
        Broadcasts to all xbees on network by sending message individually to each remote xbee in `devices` dictionary.
        This broadcast includes acknowledgements.

        *Arguments*
        | Argument        | Type                      | Description                                                                   | Default Value |
        | :------:        | :--:                      | :---------:                                                                   | :-----------: |
        | msg             | `string` or `bytearray`   | Message to send to XBee. Maximum of 108 bytes                                 | N/A           |

        *Returns*
        void
        '''

        for remote_dev in list(self.devices.values()):
            self.send(remote_dev,msg)


    def command(self, msg, remote_device = None, asynck = False):
        '''
        Sends message to remote Xbee in one of three ways depending on the `remote_device` argument
            1. remote_device == `None`:
                broadcasts message without acks using `broadcast()`
            2. remote_device == `True`:
                broadcasts message with acks using `ack_broadcast()`
            3. remote_device in values of devices dictionary:
                send message to single Xbee using `send()`

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value    |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:    |
        | msg             | `string` or `bytearray`                       | Message to send to XBee. Maximum of 108 bytes                            | N/A              |
        | remote_device   | `RemoteXbeeDevice` Object or `None` or `bool` | Argument value and type determines communication mode as described above | `None`           |
        | async           | `bool`                                        | Determines whether to send asynchronously (without ack) or not           | False            |

        *Returns*
        void
        '''

        if remote_device == None:
            self.broadcast(msg)
        elif (isinstance(remote_device,bool) and remote_device==True):
            self.ack_broadcast(msg)
        else:
            assert remote_device in self.devices.values(),"Remote Device not found in active devices"
            self.send(remote_device,msg, asynck)

    def add_rx_callback(self, callback_fun):
        '''
        Adds a data received callback function that is called everytime a message is received

        *Arguments*
        | Argument        | Type                                          | Description                                                              | Default Value    |
        | :------:        | :--:                                          | :---------:                                                              | :-----------:    |
        | callback_fun    | function                                      | Function that takes 'XbeeMessage' as input                               | N/A              |

        *Returns*
        void
        '''
        self.base.add_data_received_callback(callback_fun)







# def example_data_receive_callback(xbee_message):
#     '''DOC'''
#
#     print("From {} >> {}".format(xbee_message.remote_device.get_node_id(),
#                              xbee_message.data.decode()))
