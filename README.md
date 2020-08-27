# SmarticlesNU

This repository includes all the hardware design and software files for the smarticle system. Examples can be found in Code/Python/Examples. See [Smarticle Tracking](https://github.com/murpheylab/SmarticleTracking) for the a python AprilTag tracking library and [SmarticleSimulation](https://github.com/asamland/SmarticleSimulation) for a PyBullet simulator of the system.  

All documentation for the python modules in this repository is available [here](https://murpheylab.github.io/SmarticlesNU/)

Installing Python Dependencies
------------

You can install pyserial and the XBee Python library using pip

    $ pip install pyserial
    $ pip install digi-xbee
    
  
    
Running Your First Program
-----------
Use the included `SmarticleSyncGait.py` to test your setup. You will have to modify `PORT_NAME` to match the USB port name of the local XBee connected to your computer.  

Run the the following command to execute the code and keep the python script open  
    
    $ python3 -i SmarticleSyncGait.py
    
Then you can run this command to run the smarticles for 1 minute  

    >>> timed_sync(1)
    
    
Interfacing with The Xbees
---
To Change the settings of the Base Xbee, use [DIGI XCTU](https://www.digi.com/resources/documentation/digidocs/90001526/tasks/t_download_and_install_xctu.htm)  
The Settings for the base Xbee are the default settings for 802.15.4 firmware with these changes:  
<br>
        **1.** Change mode (AP) to API Enabled  
        **2.** Change Pan ID (ID) to 1984  
        **3.** Ensure address (MY) is 0  
        **4.** Change Destination Low Address (DL) to 0xFFFF (broadcast)  
        
You can also modify these settings in a simple serial console by entering command mode. See this [guide](https://cdn.sparkfun.com/learn/materials/29/22AT%20Commands.pdf) for more information.
    
Modifying Code on The Smarticles
---
To modify the code on the smarticles themselves, you will also need to instal MiniCore into the Arduino IDE and an SI Labs driver for the CP2104 chip.  
  <br> 
    Get the CP210x Driver for your OS: [SI Labs Drivers Link](https://www.silabs.com/products/interface/usb-bridges/classic-usb-bridges/device.cp2104?q=cp2104;page=1;x6=searchHeader;q6=Software)  
    Download Arduino IDE: [Arduino IDE Link](https://www.arduino.cc/en/Main/Software)  
    Follow the instructions to install in Arduino IDE: [MiniCore Link](https://github.com/MCUdude/MiniCore#how-to-install) 
    <br>
    
After Installing all these dependencies you will have to move the files from the Code/Arduino folder into your local Arduino folder (usually found in documents)  
<br>
        **1.**  Move the programmable_smarticle folder into your Arduino directory (should be then documents/Arduino/programmable_smarticle)  
        **2.**  Move the contents of the repo Arduino/libraries folder into your local Arduino/libraries folder  
    
You will have to restart the Arduino IDE and then you should be able to open the programmable_smarticle.ino sketch and you should see PWMServo, NeoHWSerial, and Smarticle in the Sketch->Include Library file menu.

To upload the program to the smarticle, use the follow board configuration under the tools file menu:  

  | Field | Value|
|:------------:|:-------------------------------:| 
| Board        | ATmega328                      | 
| Clock        | 8MHz External                   |  
| BOD          | BOD 2.7V                        |  
| Compiler LTO | LTO Enabled                     |  
| Variant      | 328PB                           |  
| Bootloader   | Yes (UART0)                     |  
| Port         | select USB port of SI Labs Chip |  
