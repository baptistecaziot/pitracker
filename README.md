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
  
3. Set up the network: connect the Pis to a wifi router, set up fixed IP.

4. Set up shared folders: install and set up Samba.

  a. Install Samba: ```sudo apt-get install samba samba-common-bin```. What you select regarding DHCP doesn't matter as we will use fixed-IP.
  
  b. Create data folder ```mkdir ~/data```. This folder can be anywhere on the disk, here it is created directly in the user's home.

  c. Edit the Samba config file: ```sudo nano /etc/samba/smb.conf```. Change the following lines: 
  - Required: at the end of the file add the following section:
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
  If you created a data fiolder at a different location, change the path line accordingly.
  
  - Optional: Change the "Global" section as
  ```
  workgroup = WORKGROUP
  wins support = yes
  ```

  Most likely you only need to add the ```wins support = yes``` line after workgroup in the global section of the config file. This line is not necessary, especially on small networks and especially if using fixed-IP but can help on large Windows networks typical on university settings (i.e. if the rPis are connected to the university wifi network instead of a local wifi network). The workgroup name can be anything respecting the Windows group names guidelines (e.g. PITRACKER), but that name has to match on the different computers/rPis (WORKGROUP is the default group name on Windows).
  
  - Finally quit Nano typing CTRL+X, type Y to save changes, do not change filename to overwrite previous config file. 

5. Install required libraries and copy python scripts.
  a. install libraries: ```pip install ???```

6. Set up python scripts to start automatically on boot.

## Usage
