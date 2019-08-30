# SmarticlesNU

Installating Python Dependencies
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
    
You will have to restart the Arduino IDE and then you should be able to open the programmable_smarticle.ino sketch and you should see PWMServo, NeoSWSerial, and Smarticle in the Sketch->Include Library file menu.

To upload the program to the smarticle, use the follow board configuration under the tools file menu:  


| Board        | ATmega328p                      |  
|:------------:|:-------------------------------:|  
| Clock        | 8MHz External                   |  
| BOD          | BOD 2.7V                        |  
| Compiler LTO | LTO Enabled                     |  
| Variant      | 328PB                           |  
| Bootloader   | Yes (UART0)                     |  
| Port         | select USB port of SI Labs Chip |  
