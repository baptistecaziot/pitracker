#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 19:11:36 2022

@author: bremmerlab
"""

import io
import socket
import struct
import time
import picamera

class SplitFrames(object):
    def __init__(self, connection):
       self.connection = connection
       self.stream = io.BytesIO()
       self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)

client_socket = socket.socket()
client_socket.connect(('137.248.137.15', 8000))
connection = client_socket.makefile('wb')
try:
    output = SplitFrames(connection)
    camera = picamera.PiCamera()
    camera.resolution = (320,320)
    camera.framerate = 30
    videoFormat = 'mjpeg'
    time.sleep(1)
    start = time.time()
    camera.start_recording(output, format='mjpeg')
    while 1:
        pass
except Exception as e:
    print(e)
finally:
    camera.stop_recording()
    connection.write(struct.pack('<L', 0))
    connection.close()
    client_socket.close()
    finish = time.time()
print('Sent %d images in %d seconds at %.2ffps' % (
    output.count, finish-start, output.count / (finish-start)))