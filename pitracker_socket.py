
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import socket, time
from pynput import keyboard
   


# pi_address1 = "137.248.137.8" #pcneuro06 - scene
# pi_address2 = "137.248.137.9" #pcneuro07 - eye
# pi_address1 = "137.248.137.6" #pcneuro04 - scene
# pi_address2 = "137.248.137.7" #pcneuro05 - eye
pi_address1 = "137.248.137.14" #pcneuro04 - scene
pi_address2 = "137.248.137.7" #pcneuro05 - eye
pi_port = 1959


try:
    sock1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock1.settimeout(1)
    sock1.connect((pi_address1, pi_port))
except:
    sock1 = -1
    print("Failed connectiong with Pi 1")  
    
try:
    sock2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock2.settimeout(1)
    sock2.connect((pi_address2, pi_port))
except:
    sock2 = -1
    print("Failed connectiong with Pi 2")  

print("Sockets running")

def on_press(key):
    pass
  
def on_release(key):
    try:
        msg = ''
        if (key==keyboard.Key.space):
            msg = b"p"
            print("Requested preview")
        elif (key==keyboard.Key.enter):
            msg = b"r"
            print("Requested recording") 
        elif (key==keyboard.Key.backspace):
            listener.stop()
            print("Listener stopped")
            if not (sock1==-1):
                sock1.close()
            if not (sock2==-1):
                sock2.close()
            print("Sockets closed")
        elif (key==keyboard.Key.esc):
            msg = b"e"
            print("Requested shutdown")
          
        if len(msg)>0:
            if not (sock1==-1):
                sock1.send(msg)
            if not (sock2==-1): 
                sock2.send(msg)
        
        time.sleep(0.5)
        
    except AssertionError as error:                                                                                            
        print(error)

listener = keyboard.Listener(on_press=on_press,on_release=on_release)
listener.start()


lastSent = 0
while (sock1!=-1) or (sock2!=-1):
    if not (sock1==-1):
        try:
            data = sock1.recv(1024)
            if not data:
                sock1==-1
            print("Pi1: %s" % (data.decode()))
        except:
            pass
    if not (sock2==-1):
        try:
            data = sock2.recv(1024)
            if not data:
                sock2==-1
            print("Pi2: %s" % (data.decode()))
        except:
            pass

listener.stop()
print("Lost connection with both Pis")




