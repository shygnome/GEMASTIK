from gpiozero import Servo
from time import sleep

myGPIO=17

myServo=Servo(myGPIO)

myServo.min()
sleep(1)
