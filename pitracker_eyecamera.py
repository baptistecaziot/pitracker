
####################################
#
#
#
# B. Caziot, June 2021
#
####################################

import os, io, time, datetime, picamera, socket, netifaces, struct
import RPi.GPIO as gpio
import pynput.keyboard as keyboard


# Parameters
synchPin = 21
irPin = 13
cameraResolution = (320,320)
cameraFramerate = 90
videoFormat = 'mjpeg' # h264, mjpeg, rgb, rgba or yuv 
videoQuality = 10
isRecording = 0
isPreviewing = 0
isStreaming = 0

pi_interface = "wlan0"
pi_address = netifaces.ifaddresses(pi_interface)[netifaces.AF_INET][0]["addr"]
pi_port = 1959
pi_streamingPort = 1981
server_address = "137.248.137.15"
server_port = 1959


gpio.setmode(gpio.BCM)
gpio.setup(synchPin,gpio.IN)
gpio.setup(irPin,gpio.OUT)
gpio.output(irPin,gpio.HIGH)


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
    fileName = time.strftime("/home/pi/Data/eye_%Y-%m-%d_%H-%M-%S")
    if ((videoFormat=='mjpeg') or (videoFormat=='h264')):
        camera.start_recording(pitrackercamera(camera, synchPin, fileName+'.'+videoFormat, fileName+'.txt'), format=videoFormat, quality=videoQuality)
    else:
        camera.start_recording(pitrackercamera(camera, synchPin, fileName+'.'+videoFormat, fileName+'.txt'), format=videoFormat)
        
def stop_recording():
    camera.stop_recording()

def start_previewing():
    camera.start_preview()

def stop_previewing():
    camera.stop_preview()

def shutdown():
    global isRecording
    if (isRecording==1):
        stop_recording()
    os.system("sudo shutdown -h now")

def toggle_previewing():
    global isPreviewing
    if (isPreviewing==0):
        msg = 'Start preview'
        start_previewing()
        isPreviewing = 1
    else:
        msg = 'Stop preview'
        stop_previewing()
        isPreviewing = 0
    print(msg)
    sock.sendto(msg.encode(),(server_address,server_port))
    
def toggle_recording():
    global isPreviewing, isRecording
    if (isPreviewing==1):
        stop_previewing()
        isPreviewing = 0
        
    if (isRecording==0):
        msg = 'Start recording'
        start_recording()
        isRecording = 1
    else:
        msg = 'Stop recording'
        stop_recording()
        isRecording = 0
    print(msg)
    sock.sendto(msg.encode(), (server_address,server_port));

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

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.setblocking(1)
# sock.setblocking(0)
sock.bind((pi_address,pi_port))

print('Running...')

# while True:
#     try:
#         data, addr = sock.recvfrom(1024)
#         if (data==b"p"):
#             toggle_previewing()
#         elif (data==b"r"):
#             toggle_recording()
#         
#     except AssertionError as error:
#         print(error)




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


# Make a picture
camera.capture(str(datetime.datetime.now())+'.jpg')
"""


