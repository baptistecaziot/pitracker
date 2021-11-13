
####################################
#
#
#
# B. Caziot, June 2021
#
####################################

import os, io, time, datetime, picamera
import RPi.GPIO as gpio
import pynput.keyboard as keyboard


# Parameters
synchPin = 21
irPin = 13
cameraResolution = (320,320)
cameraFramerate = 90
videoDuration = 60
videoQuality = 10
isRecording = 0
isPreviewing = 0

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
    global isRecording, camera
    if (isRecording==0):
        if (isPreviewing==1):
            stop_previewing()
        
        fileName = time.strftime("/home/pi/Data/eye_%Y-%m-%d_%H-%M-%S")
        camera.start_recording(pitrackercamera(camera, synchPin, fileName+'.h264', fileName+'.txt'), format='h264', quality=videoQuality)
        isRecording = 1

def stop_recording():
    global isRecording, camera
    if (isRecording==1):
        camera.stop_recording()
        isRecording = 0

def start_previewing():
    global isPreviewing, camera
    if (isPreviewing==0):
        camera.start_preview()
        isPreviewing = 1

def stop_previewing():
    global isPreviewing, camera
    if (isPreviewing==1):
        camera.stop_preview()
        isPreviewing = 0

def on_press(key):
    try:
        if (key==keyboard.Key.space):
            if (isPreviewing==0):
                print('Start preview')
                start_previewing()
            else:
                print('Stop preview')
                stop_previewing()
        elif (key==keyboard.Key.enter):
            if (isRecording==0):
                print('Start recording')
                start_recording()
            else:
                print('Stop recording')
                stop_recording()
e    except AssertionError as error:
        print(error)

listener = keyboard.Listener(on_press=on_press)
listener.start()

camera = picamera.PiCamera()
camera.resolution = cameraResolution
camera.framerate = cameraFramerate


"""
#camera = picamera.PiCamera()
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
#camera.capture(str(datetime.datetime.now())+'.jpg')



camera.start_recording(videoName+".h264")
print("Recording...")
time.sleep(videoDuration)
camera.stop_recording()

command = "MP4Box -add "+videoName+".h264 "+videoName+".mp4"
os.system(command)

"""


