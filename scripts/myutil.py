#!/usr/bin/python3

from picamera import PiCamera
from time import sleep

def take_pic():
    camera = PiCamera()
    camera.rotation = 270
    for i in range(5):
        camera.capture('../img/pic-'+str(i)+'.jpg')
        sleep(0.2)

take_pic()
