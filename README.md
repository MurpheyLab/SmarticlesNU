# SmarticlesNU

Installating Dependencies
------------

You can install XBee Python library using pip

    $ pip install digi-xbee
    
To modify the code on the smarticles themselves, you will also need to instal MiniCore into your Arduino IDE and an SI Labs driver for the CP2104 chip.  
  <br> 
    [MiniCore Link](https://github.com/MCUdude/MiniCore)  
    [SI Labs Drivers Link](https://www.silabs.com/products/interface/usb-bridges/classic-usb-bridges/device.cp2104?q=cp2104;page=1;x6=searchHeader;q6=Software)
    
    
Running Your First Program
-----------
Use the included `SmarticleRandomGait.py` to test your setup. You will have to modify `PORT_NAME` to match the USB port name of the local XBee connected to your computer.  

Run the the following command the execute the code and keep the python script open  
    
    $ python3 -i SmarticleRandomGait.py
    
Then you can run this command to run the smarticles for 10 seconds  

    >>> timed_go(1/6)
