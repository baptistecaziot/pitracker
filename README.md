# pitracker
This repository contains scripts to use the pi-tracker.

# Installation
(1) Install NOOB: Install NOOB on a SD card, start the Pi.
  
(2) Activate the camera module.
  - Using the graphical interface: go to Preference>Raspberry Pi Configuration>Interfaces and enable the camera module, then reboot the Pi. 
    https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/1
  - Using the terminal: type sudo raspi-config, select "5 Interfacing options">"P1 Camera">Enable camera 

  You can test the camera by typing raspistill -o ~/Desktop/test.jpg in the terminal. A JPG image should be created on the desktop.
  
(3) Set up the network: connect the Pis to a wifi router, set up fixed IP.

(4) Set up shared folders: install and set up Samba.
  https://raspberrypihq.com/how-to-share-a-folder-with-a-windows-computer-from-a-raspberry-pi/

(5) Copy python scripts

(6) Set up python scripts to start automatically on boot.

