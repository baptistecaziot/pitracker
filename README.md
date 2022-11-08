# pitracker
This repository contains scripts to use the PiTracker.

[Hardware](#hardware)

[Installation](#Installation)

[Usage](#Usage)

## Hardware
With the exception of the accelerometer, the Raspberry Pis (rPis) can be set up prior building the actual eye-tracker. And in facts it might be easier.
1. Requirements:
  - 2 Raspberry Pi zeros (https://www.raspberrypi.com/products/raspberry-pi-zero-w/). Ideally one with pins and one without.
  - 2 SD cards. I've had good experience with the SanDisk Extreme 64GB.
  - 2 rPi cameras. Cameras for the regular rPi and rPi zero are not compatible. For the scene-camera I prefer the spy camera with a 120deg angle and for the eye-camera the spy camera with a 15cm cable.
  - 1 BNO055 accelerometer (https://www.adafruit.com/product/2472).
  - 1 LiPo SHIM (https://www.adafruit.com/product/3196).
  - 1 LiPo battery. The size depends on your application, but 2000mAh allows over 1h of stable recording (e.g. https://www.adafruit.com/product/2011).
  - 1 mini-HDMI to HDMI-A adapter (https://www.raspberrypi.com/products/mini-hdmi-c-male-to-standard-hdmi-a-female-adapter/)
  - 1 micro-USB to USB-A adapter (https://www.raspberrypi.com/products/micro-usb-male-to-usb-a-female-cable/)
  - 1 power supply, although a micro-usb cable connect to a computer is enough (https://www.raspberrypi.com/products/type-c-power-supply/).
2. Stack the Raspberry Pis: If you purchased one rPi with pins and one without, simply stack the pin-less rPi on the one with pins and solder every pin. When pressed as close as possible, the rPis will have a small angle. You can use spacers to keep them straight but I've had no issues without.
3. Add the LiPo shield: Stack the LiPo shield on top of the 2 rPis. The pins should be long enough to allow you to solder it as well.
4. Add the accelerometer:
5. Add the synchronization plug:

Warning: It is said that the rPis SD cards get corrupted over time. To preserve them try to boot off the rPi from the "Log Out" menu and not by unplugging power. Similarly try to get a battery large enough that you can turn off the system at the end of the recording rather than the battery running out. That being said, I have not yet experienced a SD card getting corrupted so this is not something to worry too much about.

## Installation
Note: necessary steps are indicated by numbers. All necessary steps needs to be taken, not necessarily in order. When different solutions are available, they are denoted by dots. Only one of the possible solution denoted by a dot needs to be taken.
1. Install NOOB: Install NOOB on a SD card, start the Pi.

https://www.raspberrypi.org/documentation/installation/noobs.md

**Be careful to change the rPis default passwords**, automated scripts scan the internet and automatically log in rPis with unchanged default passwords.

2. Activate the camera module.
  - Using the graphical interface: go to Preference>Raspberry Pi Configuration>Interfaces and enable the camera module, then reboot the Pi. https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/1
  - Using the terminal: type ```sudo raspi-config```, select "3 Interface Options">"P1 Camera">Enable camera 

  You can test the camera by typing ```raspistill -o ~/Desktop/test.jpg``` in the terminal. A JPG image should be created on the desktop. Or ```raspistill -d```, which should display the camera for few seconds.
  
3. Set up the wifi network. Here I use a wifi router to create a local network where data files can be transfered at the end of data collection. This router can also connect the rPis to the internet for updating scripts, libraries etc. However I strongly recommend not keeping the rPis connected to the internet permanently. Unless you are updating the rPis, unplug the router from the netwrok. Raspberry Pis will create weak points in a network security, especially if the default password have not been changed.
    1. Figure out the IP adress of the router. Typically it is 192.168.0.1 or 192.168.1.1.
    2. On the rPis you can set static IP by editing the dhcp configuration file: ```sudo nano /etc/dhcpcd.conf```. Add the following lines:
    ```
    interface wlan0
    static ip_address = 192.168.0.101/24
    static routers = 192.168.0.1
    static domain_name_servers = 192.168.0.1
    ```
    Here the rPi IP address will be 192.168.0.101, using the network mask 255.255.255.0 (/24). The router address is 192.168.0.1. The DNS server doesn't matter if you do not connect the rPis to the internet. Change these parameters accordingly to your configuration.
    
    3. Quit nano with Ctrl+X, type "Y" to save, do not change the filename to overwrite it. Then restart the DHCP service with ```sudo /etc/init.d/dhcpcd restart```.
    
    4. Set a fixed IP on the data server. Depending on the OS the computer you use to collect data:
        - Windows: go to "Control Panel">"Network Connections". Right clock on the wifi connection and select "Properties". Then select "Internet Protocol Version 4 (TCP/IPv4)" and click on "Properties". Select "Use the followinfg IP address" and set the IP address to 192.168.0.100, Subnet mask to 255.255.255.0 and gateaway to 192.168.0.1 (if that is the address of your router). On Windows the terminal command to display connections is ```ipconfig```.
        - Mac: go to "System Preferences">"Network". Select Wifi and click on "Advanced". Here in the "TCP/IP" tab select "Configure IPv4: Manually" and set the IP address address like described above for Windows.
        - Linux: the process is the same as for the Raspberry Pis. Edit the dhcpcd.conf file, set the wlan0 connection to the same fixed address described above then restart the DHCP service.
    
    5. Before setting up a shared folder between computers, make sure the network works as expected by checking the IP address of each computer (```ipconfig``` on Windows and ```ifconfig``` on Linux and Mac, on Linux you might have install net-tools: ```sudo apt-get install net-tools```). Then make sure each computer can see other computers using ```ping 192.168.0.???``` (change ??? for the IP address of the computer you want to test). You should see "Reply from 192.168.0.???: bytes=32 time=?ms TTL=64".

4. Set up shared folders:
    1. Install Samba: ```sudo apt-get install samba```. What you select regarding DHCP doesn't matter as we will use fixed-IP.
    2. Create data folder ```mkdir ~/Data```. This folder can be anywhere on the disk, here it is created directly in the user's home. Change the rights to the data folder with ```chmod 777 ~/Data```, to allow everybody to read and write in that folder.
    3. Edit the Samba config file: ```sudo nano /etc/samba/smb.conf```. Change the following lines: 
    - Required: at the end of the file in the "Share definition" section add the following:
    ```
    [PiShare]
    comment=Shared data folder
    path=/home/pi/Data
    browseable=Yes
    writeable=Yes
    only guest=no
    create mask=0777
    directory mask=0777
    public=no
    ```
    If you created a data folder at a different location, change the path line accordingly.
  
    - Optional: Change the "Global" section as
    ```
    workgroup = WORKGROUP
    wins support = yes
    ```
    Most likely you only need to add the ```wins support = yes``` line after workgroup in the global section of the config file. This line is not necessary, especially on small networks and especially if using fixed-IP but can help on large Windows networks typical on university settings (i.e. if the rPis are connected to the university wifi network instead of a local wifi network). The workgroup name can be anything respecting the Windows group names guidelines (e.g. PITRACKER), but that name has to match on the different computers/rPis (WORKGROUP is the default group name on Windows). It is not strictly necessary either as we use fixed IP, but might make your life slightly easier.
  
    - Finally quit Nano typing CTRL+X, type Y to save changes, do not change filename to overwrite previous config file.

    4. Add a user to the authorized samba users list. If you set access to public=yes, this step is not necessary. To add the default Pi user type ```sudo smbpasswd -a pi```. Then enter a network password when prompted (it can be anything, though the same password as the Pi account would probably avoid confusion).

    5. Finally restart Samba with ```sudo /etc/init.d/smbd restart```
    
    6. Now you should be able to see the shared folder on other computers:
    - In Windows you might be able to see the rPi in Network tab of the File Explorer. In any case you can go to "This PC">"Add a network location">"Next">"Choose a custom network location". (If Windows asks anything about broadband connection just quit that window to go back to the "Add network location" interface.) Here enter the network location of the shared folder. In the described example it would be \\192.168.0.101\pi\Data
    - In OSX open Finder and select "Go">"Connect to server". Here enter "smb://192.168.0.101/pi/Data" (change IP address accordingly). If it asks for credentials enter "pi" and the network password you set on the rPi. You should also be able to connect as guest if you set the "public" parameter to yes.
    - In Linux: Go to "smb://192.168.0.101/pi/Data" (change IP address accordingly), enter "pi" as user and the password you set for Samba.

5. Clone this repository and install required libraries:
    1. Download this repository on all rPi zeros (typically inside "~/Documents"): ```git clone https://github.com/baptistecaziot/pitracker.git```
    2. Install libraries: ```pip3 install picamera pynput netifaces pysmb```

6. Set up python scripts to start automatically on boot. To do this edit the file rc.local: ```sudo nano /etc/rc.local```. Add the following line before the ```exit 0``` tag: ```python /home/pi/Documents/pitracker/pitracker_scenecamera.py```. Of course this line should be added on the rPi connected to the scene camera and will work only it the git repository has been cloned into Documents. Change the path accordingly and change for ```pitracker_eyecamera.py``` on the rPi connected to the eye camera. Consider using sudo nice -n -20 ```python script.py``` to run with highest priority.

7. Set up VNC "Virtual Network Computing". Raspberry Pis come with a VNC server preinstalled. You need to activate it on each rPi then install the VNC Viewer on your server to remotely connect to the rPis:
    1. Activate VNC on the rPi: go to Preferences > Interfaces > Enable VNC (or use raspi-config).
    2. Activate Direct Capture Mode: in VNC server, go to Options>Troubleshooting and activate Direct Capture Mode.
    3. On your server, download VNC Viewer for your OS: https://www.realvnc.com/en/connect/download/viewer/

8. At this point you should have set up the rPis and be ready for recording. You can test the system by running the pthon script. Otherwise when you'll reboot the rPi the python scripts will start automatically in background.

## Usage
The PiTrackers allow different ways to trigger recordings.
1. Trigger recordings:
  - From the server (recommended): for convenience I provide a python script to run on a separate computer. This script will connect to the rPis and trigger recordings remotely. First modify the rPis IP addresses at the top of the script. 
  - Using VNC: connect to the rPis using VNCviewer. If you have created an account and logged-in on each rPi you should see them in your "team". If not enter the rPi IP address in the search bar (e.g. 192.168.0.101). When prompted enter the rPi login info ("pi" and the rPi password). You should now see the rPi desktop as if it were connected to a monitor. You can manually start the python script on each rPi. The console should display "Running...". You might see an error message about a channel already in use which is unimportant. Now you can preview the camera by pressing "p". If you are satisfied with the image you can trigger a recording by pressing "r". The rPi will automatically create a video file in the folder "~/Data/" named after the date and time of the recording. After pressing "r" a second time the recording will stop. Note that if you performed step 6 of the installation section the script will already be running in background so it is not recommended to start the script again.
  - Using the recording pin. By default this option is turned off to avoid starting or stopping a recording accidently. However you can enable this option by setting ```allowRecordingPin = 1``` in the rPi global.ini file. In this case a recording will be triggered by sending a pulse to the pin 26 (the second pin at the bottom left).
2. Synchronize recordings: during recording, the rPi stores frame times in a .txt file alongside the video file. Pin 21 (the bottom right pin) is also monitored at each frame and its value stored in the same text file. Because the 2 rPis are soldered together the values of pin 21 can be used to synchronize the recording offline, as well as with separate recordings such as behavioral or neural data. However, be careful because the rPi are 3.3V devices. **Do not send 5V pulses** (such as from an arduino) to the rPis, they will burn right away.
3. Recover video files:
  - Using the server script: When the server script triggers a recoding, it receives and stores the file name through the socket connection. You can then use the script to recover these files by pressing "f". File transfer will be very slow, do not interupt the script before the end. In any case the video files will remain stored on the rPis, so you can recover them even if something happens during file transfer. This also means that you must delete them manually to save space.
  - Using a file explorer: connect to the samba shared folder as in step 4-6 of the installation section. You can manually copy/paste files to a different computer. Here again the file will remain on the rPi SD card until you manually delete them.
4. Analyze video file. 


## Accelerometer

Allow I2C communication with the accelerometer:
    1. Install libraries: ```sudo apt install i2c-tools python3-smbus```.
    2. Activate I2C communication: ```sudo raspi-config```>"3 Interface Options">Enable I2C, or as usual go to options to do the same thing. Restart the rPi.
    3. Get the address of the I2C slave: in terminal type ```i2cdetect -y 1```. The address is 7 bits in heaxadimal (thus has to be written 0xNN with NN the number returned by i2cdetect). The default address address should be 0x68.
    4. Change the i2c baudrate to 50kHz:```sudo cat /sys/module/i2c-bcm2708/parameters/baudrate``` and ```sudo modprobe i2c-bcm2708 baudrate=50000```
    5. Install the Adafruit BNO055 python library:
```
cd ~
git clone https://github.com/adafruit/Adafruit_Python_BNO055.git
cd Adafruit_Python_BNO055
sudo python3 setup.py install
```
If you get a syntax error, you are using python2 and not python3.
