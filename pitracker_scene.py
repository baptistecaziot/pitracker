
####################################
#
#
#
# B. Caziot, June 2021
#
####################################

import os, io, time, datetime, socket, netifaces, struct
import pynput.keyboard as keyboard
from pitracker import Pitracker

# Initiate pitracker
PT = Pitracker('scene')

def on_press(key):
    try:
        if (key.char=='p'):
            PT.toggle_previewing()
        elif (key.char=='s'):
            PT.toggle_streaming()
        elif (key.char=='r'):
            PT.toggle_recording()       
        elif (key.char=='q'):
            PT.shutdown()
    except AttributeError:
        pass
    except AssertionError as error:
        print(error)

listener = keyboard.Listener(on_press=on_press)
listener.start()


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
sock.bind(('',PT.piPort))
sock.setblocking(False)
sock.listen(1)

print('Running...')

while True:
    try:
        (PT.clientSocket,PT.clientAddress) = sock.accept()
        print('Received connection from %s' % PT.clientAddress[0])
        PT.isConnected = 1
        
        while True:
            data = PT.clientSocket.recv(1024)
            if not data:
                break
            elif (data==b"p"):
                PT.toggle_previewing()
            elif (data==b"s"):
                PT.toggle_streaming()
            elif (data==b"r"):
                PT.toggle_recording()
            elif (data==b"q"):
                PT.shutdown()
        
        print('Lost connection with %s'%(PT.clientAddress[0]))
        if PT.isStreaming:
            print('Stop streaming')
            PT.stop_streaming()
        PT.isConnected = 0
        PT.clientSocket = None
        PT.clientAddress = None
        
    except BlockingIOError:
        pass
    except ConnectionResetError:
        print("Connection reset")
        PT.isConnected = 0
        PT.clientSocket = None
        PT.clientAddress = None
    except AssertionError as error:
        print(error)




