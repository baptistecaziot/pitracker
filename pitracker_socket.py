
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import socket
from pynput import keyboard



# pi_address1 = "137.248.137.8" #pcneuro06 - scene
# pi_address2 = "137.248.137.9" #pcneuro07 - eye
pi_address1 = "137.248.137.14" #pcneuro04 - scene
pi_address2 = "137.248.137.7" #pcneuro05 - eye
pi_port = 1959
server_address = "137.248.137.15"
server_port = 1959

sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock1.connect((pi_address1, pi_port))
# sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock2.connect((pi_address2, pi_port))

print("Socket running")

# def on_press(key):
#     pass
  
    
# def on_release(key):
#     try:
#         msg = ''
#         if (key==keyboard.Key.space):
#             msg = b"p"
#             print("Requested preview")
#         elif (key==keyboard.Key.enter):
#             msg = b"r"
#             print("Requested recording")
#         elif (key==keyboard.Key.backspace):
#             listener.stop()
#             print("Listener stopped")
#             sock.close()
#             print("Socket closed")
#         elif (key==keyboard.Key.esc):
#             msg = b"e"
#             print("Requested shutdown")
          
          
#         if len(msg)>0:
#             sock.sendto(msg,(pi_address1,pi_port))
#             sock.sendto(msg,(pi_address2,pi_port))
#     except AssertionError as error:                                                                                            
#         print(error)

# listener = keyboard.Listener(on_press=on_press,on_release=on_release)
# listener.start()

# lastSent = 0
# while True:
#     try:
#         data, addr = sock.recvfrom(1024).decode()
#         print("{0}: {1}".format(addr,data))
#     except:
#         pass




