# pitracker
This repository contains scripts to use the pi-tracker.

[Installation](#Installation)

[Usage](#Usage)

## Installation
1. Install NOOB: Install NOOB on a SD card, start the Pi.

https://www.raspberrypi.org/documentation/installation/noobs.md
  
2. Activate the camera module.
  - Using the graphical interface: go to Preference>Raspberry Pi Configuration>Interfaces and enable the camera module, then reboot the Pi. https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/1
  - Using the terminal: type ```sudo raspi-config```, select "5 Interfacing options">"P1 Camera">Enable camera 

  You can test the camera by typing ```raspistill -o ~/Desktop/test.jpg``` in the terminal. A JPG image should be created on the desktop.
  
3. Set up the wifi network. Here we use a wifi router to create a local network where data files can be transfered at the end of data collection. This router can also connect the rPis to the internet for updating scripts, libraries etc. However we strongly recommend not keeping the rPis connected to the internet permanently. Unless you are updating the rPis, unplug the router from the netwrok. Raspberry Pis are notoriously unsecure and create weak points in a network security.
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
    2. Create data folder ```mkdir ~/data```. This folder can be anywhere on the disk, here it is created directly in the user's home. Change the rights to the data folder with ```chmod 777 ~/data```, to allow everybody to read and write in that folder.
    3. Edit the Samba config file: ```sudo nano /etc/samba/smb.conf```. Change the following lines: 
    - Required: at the end of the file in the "Share definition" section add the following:
    ```
    [PiShare]
    comment=Shared data folder
    path=/home/pi/data
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
    - In Windows you might be able to see the rPi in Network tab of the File Explorer. In any case you can go to "This PC">"Add a network location">"Next">"Choose a custom network location". (If Windows asks anything about broadband connection just quit that window to go back to the "Add network location" interface.) Here enter the network location of the shared folder. In the described example it would be \\192.168.0.101\pi\data
    - In OSX open Finder and select "Go">"Connect to server". Here enter "smb://192.168.0.101/pi/data". If it asks for credentials enter "pi" and the network password you set on the rPi. You should also be able to connect as guest if you set the "public" parameter to yes.
    - In Linux: 

5. Install required libraries and copy python scripts
    1. Download this repository on all rPi zeros: ```git clone https://github.com/baptistecaziot/pitracker.git```
    2. Install libraries: ```pip install ???```
    3. Download scripts

6. Set up python scripts to start automatically on boot. To do this edit the file rc.local: ```sudo nano /tec/rc.local```. Add the following line before the ```exit 0``` tag: ```python /home/pi/Documents/pitracker/pitracker_scenecamera.py```. Of course this line should be added on the rPi connected to the scene camera and will work only it the git repository has been cloned into Documents. Change the path accordingly and change for ```pitracker_eyecamera.py``` on the rPi connected to the eye camera.

## Usage
