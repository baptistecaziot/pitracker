#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 19:11:55 2022

@author: bremmerlab
"""

import io
import socket
import struct
from PIL import Image
import cv2
import numpy as np


server_socket = socket.socket()
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
server_socket.bind(('0.0.0.0', 8000))
server_socket.listen(0)

connection = server_socket.accept()[0].makefile('rb')

while True:
    try:
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]

        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        
        image_stream.seek(0)
        image = Image.open(image_stream)
        cv_image = np.array(image)
        cv2.imshow('Stream',cv_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(e)
        
connection.close()
server_socket.close()