#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################
#
#
#
# B. Caziot, June 2021
#
####################################

import os, io, time, datetime, picamera, socket, netifaces, struct
import RPi.GPIO as gpio
from configparser import ConfigParser
from threading import Thread
from pitracker_streaming import StreamingServer,StreamingHandler,StreamingOutput



# Writer object for the PiCamera.start_recoding function
class CameraOutput(object):
    
    # Constructor
    def __init__(self, camera, videoName, txtName, synchPin):
        self.camera = camera
        self.videoOuput = io.open(videoName, 'wb')
        self.txtOutput = io.open(txtName, 'w')
        self.synchPin = synchPin
        self.startTime = None
        
    # Callback on frame acquisition
    def write(self, buf):
        self.videoOuput.write(buf)
        if self.camera.frame.complete and self.camera.frame.timestamp:
            if self.startTime is None:
                self.startTime = self.camera.frame.timestamp
                self.txtOutput.write('frame_time,synch_pin\n')
            self.txtOutput.write('%f,%i\n' % (((self.camera.frame.timestamp - self.startTime) / 1000.0), gpio.input(self.synchPin)))
        
        
    # Flush camera buffer, automatically called on close
    def flush(self):
        self.videoOuput.flush()
        self.txtOutput.flush()

    # Close files
    def close(self):
        self.videoOuput.close()
        self.txtOutput.close()


# Split frames object for rapid streaming
class SplitFrames(object):
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.stream.seek(0)
        self.stream.write(buf)
    
    def flush(self):
        self.stream.flush()
    
    def close(self):
        print('close writer')
        self.stream.close()


# Pitracker object
class Pitracker(object):
    
    # Load global parameters
    config = ConfigParser()
    config.read('global.ini')
    
    synchPin = int(config.get('pin', 'synchPin'))
    irPin = int(config.get('pin', 'irPin'))
    ledPin = int(config.get('pin', 'ledPin'))
    recordPin = int(config.get('pin', 'recordPin'))
    
    filePath = config.get('var', 'filePath')
    piPort = int(config.get('var', 'piPort'))
    allowRecordingPin = int(config.get('var', 'allowRecordingPin'))
    
    gpio.setwarnings(False)
    gpio.setmode(gpio.BCM)
    gpio.setup(synchPin,gpio.IN) 
    gpio.setup(recordPin,gpio.IN)
    gpio.setup(irPin,gpio.OUT)
    gpio.output(irPin,gpio.LOW)
    gpio.setup(ledPin,gpio.OUT)
    gpio.output(ledPin,gpio.LOW)
    
    # Constructor
    def __init__(self, profile):
        
        self.profile = profile
        
        # Load device specific parameters
        config = ConfigParser()
        config.read('%s.ini' % (profile))
        
        # Initiate PiCamera
        self.camera = picamera.PiCamera()
        self.camera.resolution = (int(config.get('vid', 'cameraResolutionW')),int(config.get('vid', 'cameraResolutionH')))
        self.camera.framerate = int(config.get('vid', 'cameraFramerate'))
        
        # Some parameters
        self.videoFormat = config.get('vid', 'videoFormat')
        self.videoQuality =  int(config.get('vid', 'videoQuality'))
        self.startTime = None
        self.clientSocket = None
        self.clientAddress = None
        
        # State variables
        self.isConnected = 0
        self.isPreviewing = 0
        self.isStreaming = 0
        self.isRecording = 0
        
        if self.allowRecordingPin:
            gpio.add_event_detect(self.recordPin, gpio.RISING, callback=self.toggle_recording(), bouncetime=1000)
    
    
    def start_recording(self):
        self.fileName = time.strftime("{}_%Y-%m-%d_%H-%M-%S".format(self.profile))
        self.videoName = self.filePath + self.fileName + '.' + self.videoFormat
        self.txtName = self.filePath + self.fileName + '.txt'
        
        gpio.output(self.irPin,gpio.HIGH)
        gpio.output(self.ledPin,gpio.HIGH)
        
        if ((self.videoFormat=='mjpeg') or (self.videoFormat=='h264')):
            self.camera.start_recording(CameraOutput(self.camera, self.videoName, self.txtName, self.synchPin), format=self.videoFormat, quality=self.videoQuality)
        else:
            self.camera.start_recording(CameraOutput(self.camera, self.videoName, self.txtName, self.synchPin), format=self.videoFormat)
        self.isRecording = 1
        return 

    def stop_recording(self):
        self.camera.stop_recording()
        gpio.output(self.irPin,gpio.LOW)
        gpio.output(self.ledPin,gpio.LOW)
        self.isRecording = 0
    
    def start_previewing(self):
        self.camera.start_preview()
        gpio.output(self.irPin,gpio.HIGH)
        gpio.output(self.ledPin,gpio.HIGH)
        self.isPreviewing = 1
    
    def stop_previewing(self):
        self.camera.stop_preview()
        gpio.output(self.irPin,gpio.LOW)
        gpio.output(self.ledPin,gpio.LOW)
        self.isPreviewing = 0
    
    def start_streaming(self):
        gpio.output(self.irPin,gpio.HIGH)
        gpio.output(self.ledPin,gpio.HIGH)
        
        self.streamingSocket = socket.socket()
        self.streamingSocket.connect((self.clientAddress[0], 8000))
        self.streamingConnection = self.streamingSocket.makefile('wb')
        output = SplitFrames(self.streamingConnection)
        self.camera.start_recording(output, format='mjpeg')
        
        self.isStreaming = 1
        
    def stop_streaming(self):
        gpio.output(self.irPin,gpio.LOW)
        gpio.output(self.ledPin,gpio.LOW)
        self.camera.stop_recording()
        try:
            self.streamingConnection.write(struct.pack('<L', 0))
            self.streamingConnection.close()
            self.streamingSocket.close()
        except Exception as e:
            print(e)
        self.isStreaming = 0
    
    def shutdown(self):
        if self.isRecording:
            self.stop_recording()
        if self.isConnected:
            self.clientSocket.send("Sutting down".encode());
        os.system("sudo shutdown -h now")
    
    def toggle_previewing(self):
        if self.isPreviewing:
            msg = 'Stop preview'
            self.stop_previewing()
        else:
            msg = 'Start preview'
            self.start_previewing()
        print(msg)
        if self.isConnected:
            self.clientSocket.send(msg.encode())
            
    def toggle_streaming(self):
        if self.isConnected:
            if self.isStreaming:
                msg = 'Stop streaming'
                self.stop_streaming()
            else:
                msg = 'Start streaming'
                self.start_streaming()
            print(msg)
            self.clientSocket.send(msg.encode())
        else:
            print('No connections')
    
    def toggle_recording(self):
        if self.isPreviewing:
            self.stop_previewing()
            
        if self.isRecording:
            msg = 'Stop recording'
            self.stop_recording()
        else:
            self.start_recording()
            msg = 'Start recording'+': ' + self.videoName
        
        print(msg)
        if self.isConnected:
            self.clientSocket.send(msg.encode());



# """
# #camera.hflip = True
# #camera.vflip = True
# #camera.resolution = (2592,1944)

# camera.sharpness = 0
# camera.contrast = 0
# camera.brightness = 0
# camera.saturation = 0
# camera.ISO = 1
# camera.video_stabilization = 0
# camera.exposure_compensation = 0
# camera.exposure_mode = 'auto'
# camera.meter_mode = 'average'
# camera.awb_mode = 'auto'
# camera.image_effect = 'none'
# camera.color_effects = None
# camera.rotation = 0
# camera.crop = (0.0,0.0,1.0,1.0)
# """


