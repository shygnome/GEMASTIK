from picamera import PiCamera
from time import sleep

def take_pic(camera):
    for i in range(5):
        camera.capture('../img/pic-'+str(i)+'.jpg')
        sleep(0.3)

camera = PiCamera()
camera.rotation = 270
take_pic(camera)
