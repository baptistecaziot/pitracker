
####################################
#
#
#
# B. Caziot, June 2021
#
####################################

import os, io, time, datetime, picamera, socket, struct
import RPi.GPIO as gpio
import pynput.keyboard as keyboard


# Parameters
synchPin = 21
irPin = 13
ledPin = 12
recordPin = 26
allowRecordingPin = 0
cameraResolution = (1296,972)
cameraFramerate = 30
videoFormat = 'mjpeg' # h264, mjpeg, rgb, rgba or yuv
videoQuality = 10
pi_port = 1959

isRecording = 0
isPreviewing = 0
isStreaming = 0
isConnected = 0

gpio.setmode(gpio.BCM)
gpio.setup(synchPin,gpio.IN)
gpio.setup(recordPin,gpio.IN)
gpio.setup(irPin,gpio.OUT)
gpio.output(irPin,gpio.LOW)
gpio.setup(ledPin,gpio.OUT)
gpio.output(ledPin,gpio.LOW)


def record_callback():
    toggle_recording()
if allowRecordingPin:
    gpio.add_event_detect(recordPin, gpio.RISING, callback=record_callback, bouncetime=1000)


class pitrackercamera(object):
    def __init__(self, camera, synchPin, videoName, timestampsName):
        self.camera = camera
        self.synchPin = synchPin
        self.quality = 10
        self.video_output = io.open(videoName, 'wb') 
        self.pts_output = io.open(timestampsName, 'w')
        self.start_time = None
    
    def write(self, buf):
        self.video_output.write(buf)
        if self.camera.frame.complete and self.camera.frame.timestamp:
            if self.start_time is None:
                self.start_time = self.camera.frame.timestamp
                self.pts_output.write('# timecode format v2\n')
            self.pts_output.write('%f,%i\n' % (((self.camera.frame.timestamp - self.start_time) / 1000.0), gpio.input(self.synchPin)))
            
    def flush(self):
        self.video_output.flush()
        self.pts_output.flush()
        
    def close(self):
        self.video_output.close()
        self.pts_output.close()


def start_recording():
    filePath = "/home/pi/Data/"
    fileName = time.strftime("scene_%Y-%m-%d_%H-%M-%S")
    if ((videoFormat=='mjpeg') or (videoFormat=='h264')):
        camera.start_recording(pitrackercamera(camera, synchPin, filePath+fileName+'.'+videoFormat, filePath+fileName+'.txt'), format=videoFormat, quality=videoQuality)
    else:
        camera.start_recording(pitrackercamera(camera, synchPin, filePath+fileName+'.'+videoFormat, filePath+fileName+'.txt'), format=videoFormat)
    gpio.output(irPin,gpio.HIGH)
    gpio.output(ledPin,gpio.HIGH)
    return fileName

def stop_recording():
    camera.stop_recording()
    gpio.output(irPin,gpio.LOW)
    gpio.output(ledPin,gpio.LOW)
    
def start_previewing():
    camera.start_preview()
    gpio.output(irPin,gpio.HIGH)
    gpio.output(ledPin,gpio.HIGH)

def stop_previewing():
    camera.stop_preview()
    gpio.output(irPin,gpio.LOW)
    gpio.output(ledPin,gpio.LOW)

def shutdown():
    global isRecording, isConnected
    if (isRecording==1):
        stop_recording()
    if isConnected:
        clientsocket.send("Sutting down".encode());
    os.system("sudo shutdown -h now")

def toggle_previewing():
    global isPreviewing, isConnected
    if (isPreviewing==0):
        msg = 'Start preview'
        start_previewing()
        isPreviewing = 1
    else:
        msg = 'Stop preview'
        stop_previewing()
        isPreviewing = 0
    print(msg)
    if isConnected:
        clientsocket.send(msg.encode())
    
def toggle_recording():
    global isPreviewing, isRecording, isConnected
    if (isPreviewing==1):
        stop_previewing()
        isPreviewing = 0
        
    if (isRecording==0):
        fileName = start_recording()
        msg = 'Start recording'+': '+fileName
        isRecording = 1
    else:
        msg = 'Stop recording'
        stop_recording()
        isRecording = 0
    print(msg)
    if isConnected:
        clientsocket.send(msg.encode());

def on_press(key):
    try:
        if (key==keyboard.Key.space):
            toggle_previewing()
        elif (key==keyboard.Key.enter):
            toggle_recording()       
        elif (key==keyboard.Key.esc):
            shutdown()
        
    except AssertionError as error:
        print(error)

listener = keyboard.Listener(on_press=on_press)
listener.start()

camera = picamera.PiCamera()
camera.resolution = cameraResolution
camera.framerate = cameraFramerate

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
sock.bind(('',pi_port))
sock.setblocking(False)
sock.listen(1)

print('Running...')

while True:
    try:
        (clientsocket,address) = sock.accept()
        print('Received connection from %s' % address[0])
        isConnected = 1
        
        while True:
            data = clientsocket.recv(1024)
            if not data:
                break
            elif (data==b"p"):
                toggle_previewing()
            elif (data==b"r"):
                toggle_recording()
            elif (data==b"e"):
                shutdown()
    
        isConnected = 0
    
    except BlockingIOError:
        pass
    except ConnectionResetError:
        print("Connection reset")
        isConnected = 0
    except AssertionError as error:
         print(error)




"""
#camera.hflip = True
#camera.vflip = True
#camera.resolution = (2592,1944)

camera.sharpness = 0
camera.contrast = 0
camera.brightness = 0
camera.saturation = 0
camera.ISO = 1
camera.video_stabilization = 0
camera.exposure_compensation = 0
camera.exposure_mode = 'auto'
camera.meter_mode = 'average'
camera.awb_mode = 'auto'
camera.image_effect = 'none'
camera.color_effects = None
camera.rotation = 0
camera.crop = (0.0,0.0,1.0,1.0)
"""



