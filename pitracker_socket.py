# -*- coding: utf-8 -*-
"""
Commands:
'p': preview mode (on the rPi), requires connection through VNC
's': streaming mode - not working yet
'r': recording mode
'q': turn off rPis
'z': shut down socket (can be restarted)

"""

# import io
import socket
# import struct
import time

from pynput import keyboard

# /run/user/1000/gvfs/smb-share:server=137.248.137.8,share=pi/Data


server_ip = '0.0.0.0'

# shares = conn.listShares()

# for share in shares:
#     if not share.isSpecial and share.name not in ['NETLOGON', 'SYSVOL']:
#         sharedfiles = conn.listPath(share.name, '/')
#         for sharedfile in sharedfiles:
#             print(sharedfile.filename)

# conn.close()


# # # human
# pi_address1 = "137.248.137.8" #pcneuro06 - scene
# pi_address2 = "137.248.137.9" #pcneuro07 - eye

# monkey 1
# pi_address1 = "137.248.137.6" #pcneuro04 - scene
# pi_address2 = "137.248.137.7" #pcneuro05 - eye

# monkey 2
# pi_address1 = "137.248.137.10" #pcneuro08 - scene
# pi_address12 = "137.248.137.11" #pcneuro09 - eye

# Elmo
pi_address1 = "137.248.137.1"   #pcneuro08 - scene
pi_address2 = "137.248.137.12"  #pcneuro09 - eye


pi_port = 1959

userID = 'user'
password = 'password'
client_machine_name = 'localpcname'

server_name = 'servername'
domain_name = 'domainname'


try:
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.settimeout(2)
    sock1.connect((pi_address1, pi_port))
    print('Connected to Pi 1')
except socket.timeout:
    print('Timed out')
    sock1 = -1
except OSError:
    print('OS error')
    sock1 = -1

try:
    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock2.settimeout(2)
    sock2.connect((pi_address2, pi_port))
    print('Connected to Pi 2')
except socket.timeout:
    print('Timed out')
    sock2 = -1
except OSError:
    print('OS error')
    sock2 = -1

# try:
#     connSMB1 = SMBConnection(userID, password, client_machine_name, server_name, domain=domain_name, use_ntlm_v2=True,
#                      is_direct_tcp=True)

# conn.connect(server_ip, 445)
# except:
#     sock2 = -1
#     print("Failed connectiong with Pi 2")  

print("Sockets running")


def on_press(key):
    pass


def on_release(key):
    try:
        msg = ''
        if key.char == 'p':
            msg = b"p"
            print("Requested preview")
        elif key.char == 's':
            msg = b"s"
            print("Requested streaming")
        elif key.char == 'r':
            msg = b"r"
            print("Requested recording")
        elif key.char == 'q':
            msg = b"q"
            print("Requested shutdown")
        elif key.char == 'z':
            listener.stop()
            print("Listener stopped")
            if not (sock1 == -1):
                sock1.close()
            if not (sock2 == -1):
                sock2.close()
            print("Sockets closed")

        if len(msg) > 0:
            if not (sock1 == -1):
                sock1.sendall(msg)
            if not (sock2 == -1):
                sock2.sendall(msg)
        #
        # server_socket = socket.socket()
        # server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        # server_socket.bind(('0.0.0.0', 8000))
        # server_socket.listen(0)
        #
        # connection = server_socket.accept()[0].makefile('rb')
        #
        # while True:
        #     try:
        #         image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        #
        #         image_stream = io.BytesIO()
        #         image_stream.write(connection.read(image_len))
        #
        #         image_stream.seek(0)
        #         image = Image.open(image_stream)
        #         cv_image = np.array(image)
        #         cv2.imshow('Stream',cv_image)
        #         if cv2.waitKey(1) & 0xFF == cv2.ord('s'):
        #             print('Q pressed')
        #             break
        #     except Exception as e:
        #         print(e)

        # connection.close()
        # server_socket.close()

        time.sleep(0.2)

    except AttributeError:
        pass
    except AssertionError as error:
        print(error)


listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

lastSent = 0
isStreaming = 0
while 1:

    if not (sock1 == -1):
        try:
            data = sock1.recv(1024)
            if not data:
                sock1 == -1
            print("Pi1: %s" % (data.decode()))
            if data.decode() == 'Shutting down':
                sock1 == -1
            if data.decode() == 'Start streaming':
                isStreaming = 1
        except:
            pass

    if not (sock2 == -1):
        try:
            data = sock2.recv(1024)
            if not data:
                sock2 == -1
            print("Pi2: %s" % (data.decode()))
            if data.decode() == 'Shutting down':
                sock2 == -1
        except:
            pass

    if (sock1 == -1) and (sock2 == -1):
        print("Lost connection with both Pis")
        break

listener.stop()
print("Socket closed")
