
####################################
#
#
#
# B. Caziot, June 2021
#
####################################

import os, io, time, datetime, picamera
import RPi.GPIO as gpio


# Parameters
synchPin = 21
cameraResolution = (1296,972)#(1920,1080)
cameraFramerate = 30
videoDuration = 60
fileName = time.strftime("/home/pi/Data/scene_%Y-%m-%d_%H-%M-%S")
gpio.setmode(gpio.BCM)
gpio.setup(synchPin,gpio.IN)


class pitrackercamera(object):
    def __init__(self, camera, synchPin, videoName, timestampsName):
        self.camera = camera
        self.synchPin = synchPin
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


with picamera.PiCamera() as camera:
    camera.resolution = cameraResolution
    camera.framerate = cameraFramerate
    camera.start_recording(pitrackercamera(camera, synchPin, fileName+'.h264', fileName+'.txt'), format='h264')
    #camera.start_preview()
    camera.wait_recording(videoDuration)
    camera.stop_recording()


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


